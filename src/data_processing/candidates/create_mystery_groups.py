"""Instructor utility: a synthetic Simpson reversal with a faceting surprise.

    uv run --with qrcode python src/data_processing/candidates/create_mystery_groups.py

An optional first argument changes the destination. Students receive only
data/mystery_groups.csv; qrcode is an instructor-side dependency.
"""

import argparse
import csv
import math
import random
from pathlib import Path
from statistics import correlation

import qrcode


def make_records(destination):
    rng = random.Random(42)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    qr.add_data(destination)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    n = len(matrix)
    if n > 33:
        raise ValueError("Use a shorter destination that fits a QR code of at most 33 modules.")
    points = [(x, n - 1 - row) for row, cells in enumerate(matrix)
              for x, dark in enumerate(cells) if dark]
    if correlation(*zip(*points)) > 0:
        # A quarter turn preserves QR decoding and reverses covariance's sign.
        points = [(y, n - 1 - x) for x, y in points]

    # With default 300px panels over 0..40, a .75-unit spacing is 5.625px,
    # close to the default filled-square side sqrt(30) ~= 5.477px.
    # Birch sorts second, so the default shape range assigns it a square.
    offset = 20 - 0.75 * (n - 1) / 2
    records = [{"x": x * 0.75 + offset, "y": y * 0.75 + offset, "site": "Birch"}
               for x, y in points]
    # These clusters strengthen Birch's negative correlation while staying
    # outside the QR code's four-module quiet zone. The dataset is deliberately
    # constructed, not a claim about naturally occurring sensor measurements.
    for mean_x, mean_y in [(1.5, 38.5), (38.5, 1.5)]:
        for _ in range(30):
            records.append({
                "x": round(rng.uniform(mean_x - 1, mean_x + 1), 3),
                "y": round(rng.uniform(mean_y - 1, mean_y + 1), 3), "site": "Birch",
            })

    # Negatively associated clouds whose group means move up and to the right.
    for site, mean in [("Alder", 7), ("Cedar", 25), ("Willow", 33)]:
        count = 0
        while count < 950:
            z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
            x = mean + 9 * z1
            y = mean + 9 * (-0.7 * z1 + math.sqrt(1 - 0.7**2) * z2)
            if 0 <= x <= 40 and 0 <= y <= 40:
                records.append({"x": round(x, 3), "y": round(y, 3), "site": site})
                count += 1
    # Fix the shared default domains without custom axis/scale settings.
    records.extend({"x": x, "y": y, "site": site} for x, y, site in [
        (0, 12, "Alder"), (12, 0, "Alder"), (28, 40, "Willow"), (40, 28, "Willow"),
    ])
    rng.shuffle(records)
    return records


def summarize(records):
    subsets = {"Overall": records}
    subsets.update({site: [row for row in records if row["site"] == site]
                    for site in sorted({row["site"] for row in records})})
    results = {}
    for name, rows in subsets.items():
        r = correlation([row["x"] for row in rows], [row["y"] for row in rows])
        results[name] = r
        print(f"{name:8s}: n={len(rows):4d}, Pearson r={r:+.6f}")
    if results["Overall"] <= 0 or any(r >= 0 for name, r in results.items() if name != "Overall"):
        raise ValueError("The generated data did not produce the intended Simpson reversal.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", default="https://www.wikipedia.org")
    args = parser.parse_args()
    records = make_records(args.destination)
    summarize(records)
    output = Path(__file__).resolve().parents[3] / "data" / "mystery_groups.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["x", "y", "site"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {output}")
