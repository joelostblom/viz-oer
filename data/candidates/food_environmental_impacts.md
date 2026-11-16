# Food environmental impacts: observation-level CSV

Source: Poore & Nemecek (2018), *Reducing food's environmental impacts through
producers and consumers*, Science, DOI
[10.1126/science.aaq0216](https://doi.org/10.1126/science.aaq0216).

- [Full Excel model](https://ora.ox.ac.uk/objects/uuid:a63fb28c-98f8-4313-add6-e9eca99320a5)
- [Data S2: results, nutritional factors, and sample sizes](https://josephpoore.com/data/science-2018/Data%20S2.xls)
- [Supplementary methods and functional units](https://josephpoore.com/data/science-2018/Science%20360%206392%20987%20-%20SUPPLEMENTARY%20MATERIALS.pdf)

## Files

- `food_environmental_impacts.csv`: **2,519 product-level LCA records**, one row
  per record, covering all **43 product categories** in the full-model workbook.
- `food_environmental_impact_products.csv`: the 43 categories, their original
  names, nutrition/mass factors and sources, sample counts, and metric coverage.
- `food_environmental_impacts.provenance.json`: source file hashes, URLs,
  extraction details, and counts of available values.

### Why 2,519 rather than 2,278?

The paper reports **2,278 unique underlying observations**. The full workbook's
`Database` sheet contains **2,519 product records**, with distinct `ID` values
1–2519, across 43 `PID` categories. The export retains every one of these rows.
The workbook represents some underlying production information in multiple
products (e.g., soybeans as soymilk, tofu, or oil; milk as milk or cheese).
Dropping rows to force a 2,278-row export would discard product representations
requested for this dataset. The exported product counts match Data S2.

`record_id` is the workbook's product-record identifier, **not** a unique farm
identifier. No new deduplicated underlying-observation identifier is inferred:
the source does not supply one in this ID column, and matching study descriptions
alone is not enough to establish independent farm inventories. Keep products
separate when interpreting observation counts.

Each row can represent a single farm, an average across farms, or a regional
inventory. The data include field studies, surveys, and secondary/modelled
estimates. They are not 2,519 independently sampled individual farms.

## Environmental metrics

The export includes all six headline metrics available in the model:

| Column prefix | Meaning | Full-model column | Output numerator unit |
|---|---|---|---|
| `ghg_kg_co2e` | Greenhouse-gas emissions | BN | kg CO2-equivalent, AR5 including climate-carbon feedbacks |
| `land_use_m2_year` | Land occupation | AS | square-metre-years |
| `acidification_g_so2e` | Acidification potential | CU | g SO2-equivalent |
| `eutrophication_g_po4e` | Eutrophication potential | DE | g PO4-equivalent |
| `freshwater_withdrawals_l` | Freshwater withdrawals | DO | litres |
| `scarcity_weighted_water_l_eq` | Water use weighted by local scarcity | DV | scarcity-weighted litre-equivalents |

CU and DE are stored in **kg** equivalents in the full model and multiplied by
1,000 here to give **grams**, consistent with the main results presentation.
These are environmental impact indicators, not six measurements of emitted gases.

The impact boundary runs from production inputs through retail. It includes
allocated impacts and supply-chain losses before retail, but not cooking or
consumer losses. These values are **not annual emissions per farm**.

## Four denominator suffixes

Every metric has four columns, using the following suffixes:

| Suffix | Denominator |
|---|---|
| `_per_retail_unit` | The source product's functional unit: 1 kg or 1 litre, identified by `retail_unit` |
| `_per_kg` | 1 kg of the standardized retail product |
| `_per_100g_protein` | An amount of that product containing 100 g of protein |
| `_per_1000kcal` | An amount of that product providing 1,000 kcal |

For example, `ghg_kg_co2e_per_100g_protein` is the footprint of **100 g of
protein**, not the footprint of 100 g of food.

### Availability

- **Per kg:** conversion factors are available for **41 of 43 categories**.
  Beer and wine are reported per litre; the supplied sources do not provide
  suitable density constants, so their per-kg columns are blank.
- **Per 100 g protein:** supported for **16 categories**. Fourteen protein-rich
  categories use the exact factors in Data S2. Milk and soymilk use the nominal
  3.3% protein specification in supplementary Table S1, interpreted as 33 g/kg
  and combined with the full model's liquid densities. These two are explicitly
  approximate composition-based conversions, not directly published protein-
  normalized results.
- **Per 1,000 kcal:** supported for **six categories**: wheat/rye bread, maize
  meal, oatmeal, rice, potatoes, and cassava.

Both nutrient-denominator columns exist for every metric, but this source set
does not supply both protein and energy densities for each food. **Blank values
mean unavailable, not zero.** External food-composition data would be needed
to complete both nutritional bases for all products.

Oil protein denominators, for example, must not be treated as zero-emission
protein sources. No division by zero or fabricated nutrient density is used.
The nutrition factors are product-group constants, not measurements for each
individual farm. The exact Data S2 factors are used rather than substituting
numbers printed in supplementary Table S1, which are not always identical.

### Unit conversion

Let `I` be an impact per source retail unit, `m` be kg per retail unit, `p` be
protein g/kg, and `e` be kcal/kg:

```text
impact per kg           = I / m
impact per 100 g protein = I / (m * p / 100)
impact per 1,000 kcal    = I / (m * e / 1,000)
```

For solid products `m = 1`. Milk, soymilk, and five oils use the generic densities
from `Standardisation!C854:C860`. Beer, wine, milk, soymilk, and oils retain their
per-litre source unit as specified in supplementary Table S1 / Figure 1. Do not
use the per-row Excel `EK` value as a product density: it is an intermediate
conversion dependent on the original study's reporting unit.

The retail state matters: wheat/rye is harmonized to bread, soybeans can be
represented as tofu/soymilk/oil, and beef is edible retail meat rather than live
animal weight. `product` names the standardized product; `source_product`
preserves the more specific original label (e.g., winter wheat or goat's milk).

## Other columns

- `record_id`, `excel_row`, `product_id`: identifiers and location in the source
  workbook (`Database!AQ`, Excel row, and `Database!AN`, respectively).
- `product`, `source_product`, `scientific_name`: product identity.
- `country`, `region`, `latitude`, `longitude`: source geography; blank when
  unavailable.
- `reference_year`: may be a year or a multi-year range; retain it as text.
- `source_reference`: original study citation(s).
- `study_method`: Field data collection (F), Survey (S), or Secondary or modelled
  data (M), expanded from the workbook codes.
- `production_system`: Non-organic (C), Organic (O), Intensive (I), or
  Pasture-based (P); `production_system_details` retains the original description.
- `farms_assessed`: reported `Database!L`, where available. Missing values are
  not replaced with 1. Published "farms or regional inventories" totals in the
  product metadata are broader than this field's sum.
- `retail_unit`, `kg_per_retail_unit`, `protein_g_per_kg`, `energy_kcal_per_kg`:
  denominators used for the conversions. Their provenance is in the products CSV.
- `weight_land_ghg`, `weight_acidification`, `weight_eutrophication`,
  `weight_water`: source weights W, AC, AH, and AM. These reflect production
  representativeness, not the number of farms in a row.

An ordinary unweighted histogram shows the distribution **of database records**.
Production-weighted summaries answer a different question. Neither directly
reproduces the paper's final distributions, which also incorporate uncertainty
and resampling (supplementary methods section 9).

## Reading and plotting

No Excel packages are needed to use the extracted data:

```python
import altair as alt
import pandas as pd

data = pd.read_csv("data/food_environmental_impacts.csv")

selected = data[data["product"].isin([
    "Wheat & Rye (Bread)", "Beef (beef herd)", "Beef (dairy herd)"
])]

alt.Chart(selected).mark_boxplot().encode(
    x="product:N",
    y="ghg_kg_co2e_per_kg:Q",
)
```

For protein-normalized comparisons, choose products with protein information
(e.g., beef, peas, tofu, cheese) and use `ghg_kg_co2e_per_100g_protein`. The
wheat rows have calorie-normalized values but no source-supported protein
denominator in this export.

## Reproducing the extraction

From the repository root:

```sh
uv run --with openpyxl --with xlrd python \
  src/data_processing/candidates/extract_food_impacts.py \
  "$HOME/Downloads/LCA+Meta-Analysis+of+Food+Products+-+Full+Model+v0+(1).xlsx"
```

The command downloads Data S2 for its factors and validation counts. To run
offline, append `--nutrition-workbook /path/to/Data\ S2.xls`.

The extractor reads cached Excel formula results without modifying the workbook,
recalculating formulas, filling gaps, or creating simulated observations. It
preserves genuine zero impacts and negative GHG values (e.g., sequestration),
converts source `-` markers to empty CSV fields, and serializes floats with 12
significant digits. Sample counts are checked against Data S2 for all 43 products
and the land/GHG, acidification, eutrophication, and freshwater indicators.

The initial export also passed 756 independent comparisons against Data S2's
non-resampled minima/maxima, covering every metric/product and the published
protein- and calorie-normalized results where applicable. Liquid mass conversions,
missing denominators, genuine zero impacts, and negative GHG values were checked
separately. The example boxplot specification validates directly from the CSV.
