"""Instructor utility: encode a destination in a shuffled spatial dataset.

Run from the repository root:
    uv run --with qrcode python src/data_processing/candidates/create_mystery_pattern.py

Students only need the resulting CSV and Altair, not qrcode.
"""

import argparse
import csv
import random
from pathlib import Path

import qrcode


def create_dataset(destination, output):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    qr.add_data(destination)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    # Cartesian y coordinates: the first QR row should appear at the top.
    records = [
        (x, len(matrix) - 1 - row, int(dark))
        for row, values in enumerate(matrix)
        for x, dark in enumerate(values)
    ]
    random.Random(42).shuffle(records)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["x", "y", "value"])
        writer.writerows(records)
    print(f"Saved {len(records)} rows to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", default="https://www.wikipedia.org")
    args = parser.parse_args()
    create_dataset(args.destination, Path(__file__).resolve().parents[3] / "data" / "mystery_pattern.csv")
