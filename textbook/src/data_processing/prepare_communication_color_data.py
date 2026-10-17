"""Export the Vega example datasets used in the communication/color lectures.

Run explicitly from the repository root with:
    uv run --with vega-datasets python textbook/src/data_processing/prepare_communication_color_data.py

Rendering the textbook reads these snapshots without downloading datasets.
"""

from pathlib import Path

from vega_datasets import data


def main():
    destination = Path(__file__).resolve().parents[2] / "data"
    for name in ("cars", "iris", "gapminder", "wheat", "stocks"):
        frame = getattr(data, name)()
        path = destination / f"vega-{name}.csv"
        frame.to_csv(path, index=False)
        print(f"Exported {name}: {len(frame)} rows to {path.name}")


if __name__ == "__main__":
    main()
