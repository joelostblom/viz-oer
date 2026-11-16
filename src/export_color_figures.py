"""Extract the selected original figures from the color lecture ODP.

Usage:
    uv run python src/export_color_figures.py "/path/to/Copy of DSCI 531 - Lec 6.odp"

The original PNGs and checker-shadow GIF are copied without re-encoding.
Administrative, title-only, decorative, blank, and duplicate layers are omitted.
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
# Repeated/cropped views of the same image are exported once.
FIGURES = (
    (3, 0, "dress-photograph.png"),
    (3, 1, "dress-lighting-context.png"),
    (4, 0, "checker-shadow.png"),
    (5, 0, "checker-shadow-reveal.gif"),
    (6, 0, "microscopy-boundary.png"),
    (6, 2, "distance-rainbow.png"),
    (7, 1, "distance-grayscale.png"),
    (7, 2, "distance-viridis.png"),
    (8, 0, "rainbow-monochrome.png"),
    (8, 4, "viridis-monochrome.png"),
    (8, 3, "rainbow-cvd-simulation.png"),
    (8, 7, "viridis-cvd-simulation.png"),
    (10, 0, "rgb-color-model.png"),
    (10, 1, "hsl-color-model.png"),
    (11, 1, "hue-saturation-lightness.png"),
    (12, 3, "numerical-palette-comparison.png"),
    (12, 4, "categorical-palette-comparison.png"),
    (14, 0, "sequential-lightness.png"),
    (14, 1, "uniform-sequential-lightness.png"),
    (15, 0, "nonuniform-lightness.png"),
    (16, 0, "palette-rendering-comparison.png"),
    (17, 0, "texas-color-sequence.png"),
    (18, 0, "cyclic-palettes.png"),
    (19, 0, "diverging-palettes.png"),
    (20, 0, "categorical-palettes.png"),
    (21, 0, "too-many-country-colors-bars.png"),
    (21, 1, "too-many-country-colors-scatter.png"),
    (22, 0, "land-water-unintuitive.png"),
    (22, 1, "land-water-intuitive.png"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parents[1] / "assets/images/color-lecture",
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
