"""Save local snapshots of the Vega datasets used by the interactivity chapter."""

from pathlib import Path

from altair.datasets import data


def main():
    destination = Path(__file__).resolve().parents[2] / "data"
    data.movies().rename(columns=lambda name: name.replace(" ", "_")).to_csv(
        destination / "vega-movies-interactivity.csv", index=False
    )
    data.sp500().to_csv(destination / "vega-sp500.csv", index=False)


if __name__ == "__main__":
    main()
