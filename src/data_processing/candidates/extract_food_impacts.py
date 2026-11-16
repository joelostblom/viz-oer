"""Extract readable product-level impact data from Poore & Nemecek's full model.

Run from the repository root (Excel readers are needed only for extraction):
    uv run --with openpyxl --with xlrd python \
        src/data_processing/candidates/extract_food_impacts.py /path/to/full-model.xlsx

Uses cached Excel values, never evaluates or modifies workbook formulas.
Data S2 supplies the precise published nutritional conversion factors. Pass
--nutrition-workbook to use a local Data S2.xls instead of downloading it.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from urllib.request import urlopen

import openpyxl
import xlrd
from openpyxl.utils import column_index_from_string as column

SUMMARY_URL = "https://josephpoore.com/data/science-2018/Data%20S2.xls"
MODEL_URL = "https://ora.ox.ac.uk/objects/uuid:a63fb28c-98f8-4313-add6-e9eca99320a5"
# Each metric is (Excel column, multiplier, observation-weight column).
# Acidification and eutrophication are converted from kg equivalents to grams.
METRICS = {
    "ghg_kg_co2e": ("BN", 1, "W"),
    "land_use_m2_year": ("AS", 1, "W"),
    "acidification_g_so2e": ("CU", 1000, "AC"),
    "eutrophication_g_po4e": ("DE", 1000, "AH"),
    "freshwater_withdrawals_l": ("DO", 1, "AM"),
    "scarcity_weighted_water_l_eq": ("DV", 1, "AM"),
}
BASES = ("retail_unit", "kg", "100g_protein", "1000kcal")
ENERGY_PRODUCTS = {1, 2, 4, 5, 6, 7}
PROTEIN_PRODUCTS = {10, 11, 12, 13, 15, 34, 35, 36, 37, 38, 40, 41, 42, 43}
LITRE_PRODUCTS = {3, 14, 16, 17, 18, 19, 20, 30, 39}
DENSITY_ROWS = {14: 859, 16: 858, 17: 856, 18: 860, 19: 857, 20: 855, 39: 854}
METHODS = {"F": "Field data collection", "S": "Survey", "M": "Secondary or modelled data"}
SYSTEMS = {"C": "Non-organic", "O": "Organic", "I": "Intensive", "P": "Pasture-based"}
PRODUCT_LABELS = {34: "Beef (beef herd)", 35: "Beef (dairy herd)"}


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def number(value, location):
    if value is None or value in ("", "-"):
        return None
    if not numeric(value):
        raise ValueError(f"Unexpected non-numeric value at {location}: {value!r}")
    return value


def text(value):
    if value is None or value == "-":
        return ""
    return str(value).strip()


def cell(row, name):
    return row[column(name) - 1]


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_csv(path, records):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows({
            key: format(value, ".12g") if isinstance(value, float) else value
            for key, value in record.items()
        } for record in records)


def product_metadata(summary, standard):
    sheet = summary.sheet_by_name("Results - Nutritional Units")
    result = {}
    for pid in range(1, 44):
        row_index = pid + 2
        label = sheet.cell_value(row_index, 0)
        factor = sheet.cell_value(row_index, 1)
        unit = "1 litre" if pid in LITRE_PRODUCTS else "1 kg"
        density_row = DENSITY_ROWS.get(pid)
        mass = 1.0 if unit == "1 kg" else None
        density_source = "Definition: one kilogram" if mass else ""
        if density_row:
            mass = number(standard[density_row - 1][2], f"Standardisation!C{density_row}")
            if mass is None or mass <= 0:
                raise ValueError(f"Missing/invalid density for {label}")
            density_source = f"Standardisation!C{density_row} (kg/litre)"
        protein, energy, protein_source, energy_source = None, None, "", ""
        if pid in PROTEIN_PRODUCTS:
            if not numeric(factor) or factor <= 0:
                raise ValueError(f"Invalid protein conversion factor for {label}")
            protein = factor * 100
            protein_source = f"Data S2, Results - Nutritional Units!B{row_index + 1} x 100"
        if pid in ENERGY_PRODUCTS:
            if not numeric(factor) or factor <= 0:
                raise ValueError(f"Invalid energy conversion factor for {label}")
            energy = factor * 1000
            energy_source = f"Data S2, Results - Nutritional Units!B{row_index + 1} x 1000"
        if pid in {14, 39}:
            # Table S1 defines these products at approximately 3.3% protein.
            # Interpret this explicitly as 33 g/kg, then use the model density
            # to convert a litre's impact. These are nominal, not measured,
            # product-level nutrient densities.
            protein = 33.0
            protein_source = "Supplementary Table S1: nominal 3.3% protein (33 g/kg)"
        result[pid] = {
            "product_id": pid, "product": PRODUCT_LABELS.get(pid, label),
            "source_product_group": label, "retail_unit": unit,
            "kg_per_retail_unit": mass, "mass_conversion_source": density_source,
            "protein_g_per_kg": protein, "protein_source": protein_source,
            "energy_kcal_per_kg": energy, "energy_source": energy_source,
        }
    return result


def extract(workbook_path, summary):
    workbook = openpyxl.load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        standard = list(workbook["Standardisation"].values)
        products = product_metadata(summary, standard)
        records = []
        for excel_row, row in enumerate(workbook["Database"].values, 1):
            pid, record_id = cell(row, "AN"), cell(row, "AQ")
            if not numeric(pid) or not numeric(record_id) or not cell(row, "C"):
                continue  # Headers, blank rows, and product-section labels.
            if pid not in products or int(record_id) != record_id:
                raise ValueError(f"Unexpected product or record ID on row {excel_row}")
            product = products[pid]
            mass, protein, energy = (product[k] for k in (
                "kg_per_retail_unit", "protein_g_per_kg", "energy_kcal_per_kg",
            ))
            denominators = {
                "retail_unit": 1,
                "kg": mass,
                "100g_protein": mass * protein / 100 if mass and protein else None,
                "1000kcal": mass * energy / 1000 if mass and energy else None,
            }
            record = {
                "record_id": int(record_id), "excel_row": excel_row,
                "product_id": int(pid), "product": product["product"],
                "source_product": text(cell(row, "C")),
                "scientific_name": text(cell(row, "D")),
                "country": text(cell(row, "I")), "region": text(cell(row, "J")),
                "reference_year": text(cell(row, "K")),
                "source_reference": text(cell(row, "B")),
                "study_method": METHODS.get(cell(row, "G"), text(cell(row, "G"))),
                "production_system": SYSTEMS.get(cell(row, "E"), text(cell(row, "E"))),
                "production_system_details": text(cell(row, "F")),
                "farms_assessed": number(cell(row, "L"), f"Database!L{excel_row}"),
                "latitude": number(cell(row, "M"), f"Database!M{excel_row}"),
                "longitude": number(cell(row, "N"), f"Database!N{excel_row}"),
                "retail_unit": product["retail_unit"], "kg_per_retail_unit": mass,
                "protein_g_per_kg": protein, "energy_kcal_per_kg": energy,
                "weight_land_ghg": number(cell(row, "W"), f"Database!W{excel_row}"),
                "weight_acidification": number(cell(row, "AC"), f"Database!AC{excel_row}"),
                "weight_eutrophication": number(cell(row, "AH"), f"Database!AH{excel_row}"),
                "weight_water": number(cell(row, "AM"), f"Database!AM{excel_row}"),
            }
            for metric, (source_column, multiplier, _) in METRICS.items():
                value = number(cell(row, source_column), f"Database!{source_column}{excel_row}")
                value = value * multiplier if value is not None else None
                for basis, denominator in denominators.items():
                    record[f"{metric}_per_{basis}"] = (
                        value / denominator if value is not None and denominator else None
                    )
            records.append(record)
    finally:
        workbook.close()
    return records, products


def validate(records, products, summary):
    ids = [r["record_id"] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate source record IDs")
    # A product ID is the row offset in the authors' sample-size table.
    sample_sizes = summary.sheet_by_name("Sample Sizes")
    for pid, product in products.items():
        subset = [r for r in records if r["product_id"] == pid]
        counts = {}
        for metric, sample_col in [("ghg_kg_co2e", 1), ("land_use_m2_year", 1),
                                   ("acidification_g_so2e", 2), ("eutrophication_g_po4e", 3),
                                   ("freshwater_withdrawals_l", 4)]:
            actual = sum(r[f"{metric}_per_retail_unit"] is not None for r in subset)
            expected = int(sample_sizes.cell_value(pid + 1, sample_col))
            if actual != expected:
                raise ValueError(f"Sample-size mismatch for {product['product']} {metric}: {actual} != {expected}")
            counts[metric] = actual
        product["record_count"] = len(subset)
        product["reported_farm_or_regional_inventories_land_ghg"] = int(sample_sizes.cell_value(pid + 1, 5))
        for metric in METRICS:
            product[f"n_{metric}"] = sum(r[f"{metric}_per_retail_unit"] is not None for r in subset)
    for record in records:
        for metric in METRICS:
            for basis in BASES:
                value = record[f"{metric}_per_{basis}"]
                if value is not None and not math.isfinite(value):
                    raise ValueError("Non-finite exported impact")
        # Negative GHG values can represent sequestration; do not discard them.
        for basis in BASES:
            value = record[f"land_use_m2_year_per_{basis}"]
            if value is not None and value < 0:
                raise ValueError("Unexpected negative land use")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--nutrition-workbook", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[3] / "data")
    args = parser.parse_args()
    if args.nutrition_workbook:
        summary_bytes = args.nutrition_workbook.read_bytes()
    else:
        with urlopen(SUMMARY_URL, timeout=60) as response:
            summary_bytes = response.read()
    summary = xlrd.open_workbook(file_contents=summary_bytes)
    records, products = extract(args.workbook, summary)
    validate(records, products, summary)
    if len(records) != 2519 or len(products) != 43:
        raise ValueError("Unexpected record count for the supported full-model v0 workbook")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "food_environmental_impacts.csv", records)
    write_csv(args.output_dir / "food_environmental_impact_products.csv", list(products.values()))
    metadata = {
        "source_model_url": MODEL_URL, "source_model_filename": args.workbook.name,
        "source_model_sha256": sha256(args.workbook), "source_nutrition_url": SUMMARY_URL,
        "source_nutrition_sha256": hashlib.sha256(summary_bytes).hexdigest(),
        "paper_reported_unique_observations": 2278,
        "exported_product_records": len(records), "product_groups": len(products),
        "row_unit": "Harmonized product-level LCA record; not necessarily an individual farm",
        "source_values": "Cached Excel formula results; no recalculation or resampling",
        "metric_source_columns": {name: values[0] for name, values in METRICS.items()},
        "metric_multipliers": {name: values[1] for name, values in METRICS.items()},
        "nutrition_coverage_product_groups": {
            "protein": sum(p["protein_g_per_kg"] is not None for p in products.values()),
            "energy": sum(p["energy_kcal_per_kg"] is not None for p in products.values()),
            "mass": sum(p["kg_per_retail_unit"] is not None for p in products.values()),
        },
        "nonmissing_impacts": {metric: {
            basis: sum(r[f"{metric}_per_{basis}"] is not None for r in records) for basis in BASES
        } for metric in METRICS},
    }
    (args.output_dir / "food_environmental_impacts.provenance.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Exported {len(records):,} product records across {len(products)} groups to {args.output_dir}")
    print("Nutritional/mass coverage:", metadata["nutrition_coverage_product_groups"])
    print("Validated each product's land/GHG, acidification, eutrophication, and freshwater counts against Data S2.")


if __name__ == "__main__":
    main()
