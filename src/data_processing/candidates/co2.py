"""Plot the combined atmospheric CO2 record from 1700 to the latest observation.

Run from the repository root:
    uv run python src/data_processing/candidates/co2.py

Exports an interactive chart to _book/co2.html. Use --output to
choose another path or format, for example --output /tmp/opencode/co2.svg.
Import atmospheric_co2_chart() to reuse the chart in a notebook or chapter.
"""

import argparse
from pathlib import Path

import altair as alt
import pandas as pd


TEXTBOOK = Path(__file__).resolve().parents[3]
DATA = TEXTBOOK / 'data' / 'atmospheric_co2.csv'


def atmospheric_co2_chart(data_path=DATA):
    data = pd.read_csv(data_path, parse_dates=['date']).sort_values('date', kind='stable')
    last_date = data['date'].max().strftime('%Y-%m-%d')
    return (
        alt.Chart(data)
        .mark_line(color='#265b8e', strokeWidth=1.5, clip=True)
        .encode(
            x=alt.X('date:T').title('Year').scale(domain=['1700-01-01', last_date]),
            y=alt.Y('co2:Q').title('Atmospheric CO₂ (ppm)').scale(zero=False),
            tooltip=[
                alt.Tooltip('date:T').title('Date').format('%Y-%m-%d'),
                alt.Tooltip('co2:Q').title('CO₂ (ppm)').format('.2f'),
            ],
        )
        .properties(
            width=900,
            height=360,
            title=alt.Title(
                text=f'Atmospheric CO₂, 1700–{last_date[:4]}',
                subtitle=[
                    'Law Dome ice-core gas ages before 1958; Scripps Mauna Loa record from 1958.',
                    f'Seasonal cycle retained. Latest available observation: {last_date}.',
                    'Sources: Scripps Institution of Oceanography at UC San Diego; Rubino et al. (2019), CSIRO.',
                ],
                anchor='start',
            ),
        )
        .interactive()
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=TEXTBOOK / '_book' / 'co2.html')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    chart = atmospheric_co2_chart()
    chart.save(args.output)
    print(f'Saved chart to {args.output}')
