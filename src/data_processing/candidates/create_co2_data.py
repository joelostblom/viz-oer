"""Download and combine Law Dome and Scripps atmospheric CO2 records.

Run from the repository root:
    uv run python src/data_processing/candidates/create_co2_data.py

Based on the sources and 1958 handoff in:
https://github.com/sio-co2o2/keelingcurve_notebooks/blob/main/notebooks/create_graphic_icecore_start_1700_ce_keelingcurve.ipynb

Use ice-core gas ages (not ice ages) before 1958, then the non-seasonally-
adjusted, gap-filled monthly series used by the notebook. Append newer daily
measurements from the same Scripps file to reach the latest available date.
See data/atmospheric_co2.md for provenance and interpretation.
"""

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


BASE_URL = 'https://raw.githubusercontent.com/sio-co2o2/keelingcurve_notebooks/main'
ICECORE_URL = f'{BASE_URL}/icecore_data/Law_Dome_GHG_2000years_co2_by_age.csv'
MODERN_URL = f'{BASE_URL}/preliminary_data/mlo/mlo_full_record_now_span.csv'
OUTPUT = Path(__file__).resolve().parents[3] / 'data' / 'atmospheric_co2.csv'


def decimal_year_to_date(value):
    """Convert elapsed fraction of a calendar year to a date, including leap years."""
    year = int(value)
    start = datetime(year, 1, 1)
    duration = (datetime(year + 1, 1, 1) - start).total_seconds()
    # Source decimal years are rounded. Round to seconds before taking the date
    # so an intended midnight does not become the previous day due to float error.
    elapsed = round((value - year) * duration)
    return (start + timedelta(seconds=elapsed)).date()


def merge_records(icecore, modern, as_of):
    """Return only date and CO2 (ppm), retaining separate same-year ice samples."""
    ice = icecore[['CO2 Age (year AD)', 'CO2 (ppm)']].rename(
        columns={'CO2 Age (year AD)': 'year', 'CO2 (ppm)': 'co2'}
    ).dropna()
    ice = ice.loc[(ice['year'] >= 1700) & (ice['year'] < 1958)]

    monthly = modern[['date_filled', 'co2_filled']].rename(
        columns={'date_filled': 'year', 'co2_filled': 'co2'}
    ).dropna()
    monthly = monthly.loc[monthly['year'] >= 1958]
    if monthly.empty:
        raise ValueError('No valid gap-filled monthly CO2 observations in the source.')

    daily = modern[['date', 'co2']].rename(columns={'date': 'year'}).dropna()
    daily = daily.loc[daily['year'] > monthly['year'].max()]

    combined = pd.concat([ice, monthly, daily], ignore_index=True)
    combined = combined.sort_values('year', kind='stable')
    combined['date'] = combined['year'].map(decimal_year_to_date)
    combined = combined.loc[combined['date'] <= as_of, ['date', 'co2']]
    if combined.empty or not combined['co2'].gt(0).all():
        raise ValueError('Expected nonempty CO2 observations with positive ppm values.')
    return combined.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', type=date.fromisoformat, default=date.today(),
                        help='Last allowed observation date, YYYY-MM-DD (default: today)')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()

    icecore = pd.read_csv(ICECORE_URL, comment='#', skipinitialspace=True)
    modern = pd.read_csv(MODERN_URL, comment='"')
    data = merge_records(icecore, modern, args.as_of)
    data.to_csv(args.output, index=False)
    print(f'Saved {len(data)} observations to {args.output}')
    print(f'Date range: {data.date.min()} to {data.date.max()}')
    print(f'Latest CO2: {data.iloc[-1].co2:.2f} ppm')


if __name__ == '__main__':
    main()
