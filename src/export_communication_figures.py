"""Extract the selected original figures from the communication lecture ODP.

Usage:
    uv run python src/export_communication_figures.py "/path/to/Copy of DSCI 531 - Lec 5.odp"

No office application is required: the PNGs are copied directly from the ODP.
The course-administration page, overplotting figures, hidden climate example,
blank final page, and duplicate animation layers are intentionally omitted.
"""

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

# Source slide number, zero-based image index, and descriptive output filename.
# Images that originally overlap are separate assets so comparisons stay visible.
FIGURES = (
    (2, 0, "iraq-bloody-toll.png"),
    (2, 1, "iraq-deaths-on-decline.png"),
    (3, 0, "minard-napoleon-campaign.png"),
    (3, 1, "napoleon-survival-summary.png"),
    (4, 0, "pie-bar-comparison.png"),
    (4, 1, "pie-bar-alternatives.png"),
    (4, 2, "many-category-pie.png"),
    (4, 3, "three-dimensional-donut.png"),
    (5, 1, "donut-chart-election.png"),
    (6, 2, "one-series-one-color.png"),
    (6, 1, "highlight-one-series.png"),
    (6, 0, "too-many-highlights.png"),
    (7, 1, "highlight-a-line.png"),
    (7, 0, "consistent-group-colors.png"),
    (8, 0, "horizontal-category-labels.png"),
    (9, 0, "horror-film-counts.png"),
    (9, 1, "horror-film-context.png"),
    (10, 0, "iphone-cumulative-sales.png"),
    (10, 1, "iphone-quarterly-context.png"),
    (10, 2, "position-length-slope.png"),
    (11, 2, "trend-mean.png"),
    (11, 0, "trend-linear-regression.png"),
    (11, 1, "trend-loess.png"),
    (12, 0, "spurious-correlation.png"),
    (12, 1, "correlation-cartoon.png"),
    (14, 0, "three-dimensional-cylinders.png"),
    (15, 0, "banana-chart.png"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "assets/images/communication-lecture",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": args.source.name,
        "sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "figures": [],
    }
    with zipfile.ZipFile(args.source) as archive:
        document = ET.fromstring(archive.read("content.xml"))
        pages = document.findall("office:body/office:presentation/draw:page", NS)
        for slide, index, filename in FIGURES:
            images = pages[slide - 1].findall(".//draw:image", NS)
            member = images[index].get("{" + NS["xlink"] + "}href")
            content = archive.read(member)
            (args.output / filename).write_bytes(content)
            manifest["figures"].append({
                "file": filename, "slide": slide, "member": member,
                "sha256": hashlib.sha256(content).hexdigest(),
            })
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Extracted {len(FIGURES)} figures to {args.output}")


if __name__ == "__main__":
    main()
