"""Prepare the two Gapminder time-series datasets used in Connections.

Run from the repository root:
    uv run python src/data_processing/candidates/create_trends_data.py

The chapter reads the generated CSVs directly, without teaching aggregation
syntax before Center & spread. Population is summed over countries. Regional
children_per_woman is the unweighted mean of the country values, matching
the original chapter's mean(children_per_woman) charts (not a population-
weighted regional fertility rate). pandas excludes missing fertility values
when calculating means, as Altair does.
"""

import argparse
from pathlib import Path

import pandas as pd


SOURCE = 'https://raw.githubusercontent.com/joelostblom/teaching-datasets/main/world-data-gapminder.csv'
DATA_DIR = Path(__file__).resolve().parents[3] / 'data'


def create_datasets(source=SOURCE):
    countries = pd.read_csv(source)
    world = (
        countries.groupby('year', as_index=False, sort=True)
        .agg(population=('population', 'sum'))
    )
    regions = (
        countries.groupby(['year', 'region'], as_index=False, sort=True)
        .agg(
            population=('population', 'sum'),
            children_per_woman=('children_per_woman', 'mean'),
        )
    )
    for name, data in [('gapminder_world_trends.csv', world),
                       ('gapminder_region_trends.csv', regions)]:
        path = DATA_DIR / name
        data.to_csv(path, index=False)
        print(f'Saved {len(data)} rows to {path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=SOURCE, help='Source CSV path or URL')
    args = parser.parse_args()
    create_datasets(args.source)
