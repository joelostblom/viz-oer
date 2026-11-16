"""Save the marathon finish-time subset used by the distribution chapters.

Run from the repository root:
    uv run python src/data_processing/candidates/prepare_marathon_finish_times.py \
        "/home/joel/Downloads/Respository London Marathon 18-23.csv"

Matches chapter 9's selection and time conversion exactly, keeping only the
finish time in minutes. The source has no year column; no year is inferred.
"""

import argparse
from pathlib import Path

import pandas as pd


OUTPUT = Path(__file__).resolve().parents[3] / 'data' / 'london_marathon_finish_times.csv'


def prepare_finish_times(source):
    runners = pd.read_csv(source).query('gender == 1 and agecat == "18-39"')
    durations = pd.to_timedelta(runners['fulltime'].str.split(' ').str[0])
    minutes = durations.dt.total_seconds().div(60).dropna()
    if minutes.empty or not minutes.gt(0).all():
        raise ValueError('Expected positive marathon finish times.')
    return minutes.rename('Time (minutes)').to_frame().reset_index(drop=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Original marathon CSV')
    args = parser.parse_args()
    data = prepare_finish_times(args.source.expanduser())
    data.to_csv(OUTPUT, index=False)
    print(f'Saved {len(data)} finish times to {OUTPUT}')
