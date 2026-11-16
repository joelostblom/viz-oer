"""Extract the uncertainty lecture's embedded figures without rasterizing slides.

Usage:
    uv run --with pillow python src/export_uncertainty_figures.py SOURCE.odp
"""

import argparse
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image


FIGURES = {
    "election-probabilities.png": (3, 0),
    "election-frequency-seats.png": (4, 0),
    "election-distributions.png": (7, 0),
    "election-scenarios.png": (7, 1),
    "unlabeled-penguin-intervals.png": (9, 0),
    "distribution-and-interval.png": (10, 0),
    "interval-definitions.png": (11, 0),
    "interval-overlap.png": (12, 0),
    "fitted-curves-and-band.png": (13, 0),
    "hypothetical-fitted-curves.gif": (13, 1),
    "hurricane-cone-and-paths.png": (14, 0),
}
NAMESPACES = {"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"}
HREF = "{http://www.w3.org/1999/xlink}href"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / "assets/images/uncertainty-lecture"
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.source) as archive:
        pages = ET.fromstring(archive.read("content.xml")).findall(
            ".//draw:page", NAMESPACES
        )
        for name, (slide, index) in FIGURES.items():
            images = list(dict.fromkeys(
                image.get(HREF)
                for image in pages[slide - 1].findall(".//draw:image", NAMESPACES)
            ))
            data = archive.read(images[index])
            if name == "interval-definitions.png":
                # Remove surrounding webpage prose; credit is retained in the caption.
                Image.open(BytesIO(data)).crop((35, 32, 810, 374)).save(output / name)
            else:
                # Preserve the original GIF frames and all other image bytes.
                (output / name).write_bytes(data)
            print(output / name)


if __name__ == "__main__":
    main()
