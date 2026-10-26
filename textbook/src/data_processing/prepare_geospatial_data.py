"""Prepare local map data and optionally import the original geoviz lecture assets.

Run from the repository root with ``uv run python
textbook/src/data_processing/prepare_geospatial_data.py``. Pass ``--lecture``
with the original 4-geoviz.ipynb to recover its population/election snapshots
and accompanying slides. Ordinary book renders use only the checked-in files
and never run this download script.
"""

import argparse
import json
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import geopandas as gpd
import pandas as pd

TEXTBOOK = Path(__file__).resolve().parents[2]
DATA = TEXTBOOK / "data"
COUNTRIES_URL = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
REGIONS_URL = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip"
EARTHQUAKES_URL = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/earthquakes.json"


def download(url):
    with urlopen(url, timeout=120) as response:
        return response.read()


def write_geojson(frame, path):
    """Keep source ring winding and round coordinates to reduce example sizes."""
    def rounded(value):
        if isinstance(value, list):
            return [rounded(item) for item in value]
        return round(value, 5) if isinstance(value, float) else value

    collection = json.loads(frame.to_json(drop_id=True, to_wgs84=True))
    for feature in collection["features"]:
        geometry = feature["geometry"]
        geometry["coordinates"] = rounded(geometry["coordinates"])
    path.write_text(json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n")


def lecture_records(cell):
    """Recover complete data from a saved Altair chart, not its truncated table."""
    for output in cell.get("outputs", []):
        html = "".join(output.get("data", {}).get("text/html", []))
        match = re.search(r'\{\s*"\$schema"\s*:', html)
        if not match:
            continue
        spec, _ = json.JSONDecoder().raw_decode(html[match.start():])
        datasets = list(spec.get("datasets", {}).values())
        datasets += [item["values"] for item in spec.get("data", []) if "values" in item]
        for records in datasets:
            if isinstance(records, dict):
                records = records.get("features", [])
            if records:
                yield pd.DataFrame([record.get("properties", {}) | record for record in records])


def import_lecture(path):
    notebook = json.loads(path.read_text())
    frames = [frame for cell in notebook["cells"] for frame in lecture_records(cell)]
    populations = next(frame for frame in frames if {"population", "name"} <= set(frame))
    populations = populations[["name", "population"]].drop_duplicates()
    assert len(populations) == 13
    assert populations["population"].sum() == 36_991_981
    populations.to_csv(DATA / "geospatial-canada-population-2021.csv", index=False)

    election = next(frame for frame in frames if {"name", "winning_party", "electoral_votes"} <= set(frame))
    election = election[["name", "winning_party", "electoral_votes"]].drop_duplicates()
    election["name"] = election["name"].replace({"Washington, D.C.": "District of Columbia"})
    # The notebook's inner join can omit DC because its two sources name it differently.
    if "District of Columbia" not in set(election["name"]):
        election = pd.concat([election, pd.DataFrame([{
            "name": "District of Columbia", "winning_party": "Dem", "electoral_votes": 3,
        }])], ignore_index=True)
    assert len(election) == 51
    assert election["electoral_votes"].sum() == 538
    assert election.groupby("winning_party")["electoral_votes"].sum().to_dict() == {"Dem": 332, "Rep": 206}
    election.sort_values("name").to_csv(DATA / "geospatial-us-election-2012.csv", index=False)

    shutil.copy2(path.with_name("slides-lec4.pdf"), TEXTBOOK / "lecture-material" / "slides-geoviz.pdf")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lecture", type=Path, help="Original instructor 4-geoviz.ipynb")
    args = parser.parse_args()

    with TemporaryDirectory(prefix="geospatial-data-") as temporary:
        temporary = Path(temporary)
        for name, url, columns in [
            ("countries", COUNTRIES_URL, [
                "NAME", "CONTINENT", "SUBREGION", "POP_EST", "POP_YEAR", "ECONOMY",
                "INCOME_GRP", "GDP_MD", "GDP_YEAR", "geometry",
            ]),
            ("regions", REGIONS_URL, [
                "wikipedia", "name", "region", "admin", "iso_a2", "postal",
                "latitude", "longitude", "geometry",
            ]),
        ]:
            archive = temporary / f"{name}.zip"
            archive.write_bytes(download(url))
            frame = gpd.read_file(archive)[columns].to_crs("EPSG:4326")
            if name == "regions":
                frame.geometry = frame.geometry.simplify(0.025, preserve_topology=True)
            assert frame.geometry.notna().all() and (~frame.geometry.is_empty).all()
            write_geojson(frame, DATA / f"geospatial-world-{name}.geojson")
            print(f"Saved {len(frame)} {name}")

    earthquakes = json.loads(download(EARTHQUAKES_URL))
    rows = []
    for feature in earthquakes["features"]:
        longitude, latitude, depth = feature["geometry"]["coordinates"]
        rows.append({
            "longitude": longitude, "latitude": latitude, "depth": depth,
            "magnitude": feature["properties"]["mag"],
            "place": feature["properties"]["place"],
        })
    pd.DataFrame(rows).to_csv(DATA / "geospatial-earthquakes.csv", index=False)

    topology = DATA / "plotly-geo"
    topology.mkdir(exist_ok=True)
    for name in ["world_110m.json", "usa_110m.json"]:
        (topology / name).write_bytes(download(f"https://cdn.plot.ly/{name}"))

    if args.lecture:
        import_lecture(args.lecture)


if __name__ == "__main__":
    main()
