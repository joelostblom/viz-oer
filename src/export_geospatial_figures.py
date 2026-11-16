"""Extract the original map illustrations and animation from lec4-maps.odp.

Usage:
    uv run python src/export_geospatial_figures.py /path/to/lec4-maps.odp

Images are copied directly from the ODP, retaining their original labels,
resolution, and GIF animation. No office application is needed for extraction
or for rendering the textbook with the checked-in assets.
"""

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

# Source slide number, zero-based image index, and descriptive output filename.
# Repeated projections and the point/bar-chart examples already implemented in
# the chapter are represented by their existing executable charts instead.
FIGURES = (
    (3, 0, "mercator-world.png"),
    (4, 1, "projection-animation.gif"),
    (6, 0, "equal-earth-world.png"),
    (11, 0, "alaska-true-relative-size.png"),
    (12, 0, "election-2012-geographic.png"),
    (13, 0, "election-2012-cartogram.png"),
    (14, 0, "election-2012-tile-cartogram.png"),
    (15, 0, "election-2012-circle-cartogram.png"),
    (18, 0, "county-population-density.png"),
    (19, 0, "county-median-income.png"),
    (20, 0, "state-median-income.png"),
    (21, 0, "choropleth-point-symbol-comparison.png"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "assets/images/geospatial-lecture",
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
            page = pages[slide - 1]
            images = page.findall(".//draw:image", NS)
            member = images[index].get("{" + NS["xlink"] + "}href")
            content = archive.read(member)
            (args.output / filename).write_bytes(content)
            paragraphs = ["".join(paragraph.itertext()) for paragraph in page.findall(".//text:p", NS)]
            credits = sorted(set(re.findall(r"https?://[^\s<>]+", "\n".join(paragraphs))))
            manifest["figures"].append({
                "file": filename, "slide": slide, "member": member,
                "sha256": hashlib.sha256(content).hexdigest(), "slide_credit_urls": credits,
            })
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Extracted {len(FIGURES)} figures to {args.output}")


if __name__ == "__main__":
    main()
