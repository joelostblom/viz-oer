"""Prepare the complete and deliberately incomplete weather data for EDA.

Run explicitly from any directory; textbook renders only read these files.
The source is the Seattle daily weather example distributed by vega-datasets.
"""

import csv
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen


URL = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/seattle-weather.csv"
DATA = Path(__file__).resolve().parents[2] / "data"


def main():
    with urlopen(URL, timeout=60) as response:
        source = response.read()
    reader = csv.DictReader(io.StringIO(source.decode("utf-8-sig")))
    rows = list(reader)
    columns = ["date", "precipitation", "temp_max", "temp_min", "wind", "weather"]
    assert reader.fieldnames == columns
    assert len(rows) == 1461
    assert len({row["date"] for row in rows}) == len(rows)
    assert rows[0]["date"] == "2012-01-01" and rows[-1]["date"] == "2015-12-31"
    assert all(value != "" for row in rows for value in row.values())

    incomplete = [row.copy() for row in rows]
    for row in incomplete:
        for column in ("temp_min", "temp_max"):
            if float(row[column]) <= 0.6:
                row[column] = ""

    for filename, records in (
        ("seattle-weather-complete.csv", rows),
        ("seattle-weather-sensor.csv", incomplete),
    ):
        with (DATA / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
        print(f"{filename}: {len(records)} rows")
    print("Source SHA-256:", hashlib.sha256(source).hexdigest())
    for column in ("temp_min", "temp_max"):
        count = sum(row[column] == "" for row in incomplete)
        print(f"{column}: {count} values deliberately removed")


if __name__ == "__main__":
    main()
