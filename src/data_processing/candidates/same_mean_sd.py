"""Compare identical mean ± SD summaries with different underlying distributions.

Run from the repository root:
    uv run python src/data_processing/candidates/same_mean_sd.py
    uv run python src/data_processing/candidates/same_mean_sd.py --output /tmp/opencode/same-mean-sd.svg

Import same_mean_sd_chart() to use the visualization in a notebook or chapter.
The CSV contains synthetic teaching data inspired by Weissgerber et al. (2015),
Fig. 1, https://doi.org/10.1371/journal.pbio.1002128.
"""

import argparse
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd


TEXTBOOK = Path(__file__).resolve().parents[3]
DATA = TEXTBOOK / 'data' / 'same_mean_sd.csv'
SCENARIOS = ['Symmetric', 'Outlier', 'Bimodal', 'Right-skewed', 'Unequal n']
GROUPS = ['A', 'B']


def same_mean_sd_chart(data_path=DATA):
    data = pd.read_csv(data_path)
    # Horizontal jitter separates nearby points; measured values are unchanged.
    # Use a local seed so repeated renders have the same point positions.
    data['group_position'] = data['group'].map({'A': 0, 'B': 1})
    data['jittered_position'] = data['group_position'] + np.random.default_rng(123).uniform(-0.18, 0.18, len(data))
    y = alt.Y('value:Q').title('Value').scale(domain=[0, 40]).axis(tickCount=5)

    def group_axis(field):
        return alt.X(f'{field}:Q').title('Group').scale(domain=[-0.5, 1.5]).axis(
            values=[0, 1], labelExpr="datum.value === 0 ? 'A' : 'B'", grid=False,
        )

    x = group_axis('group_position')
    color = alt.Color('group:N').scale(
        domain=GROUPS, range=['#2780e3', '#d55e00']
    ).legend(None)
    base = alt.Chart(data).encode(x=x, color=color)

    intervals = base.mark_errorbar(extent='stdev', ticks=True).encode(y=y)
    means = base.mark_point(filled=True, size=70).encode(
        y=alt.Y('mean(value):Q').title('Value').scale(domain=[0, 40]).axis(tickCount=5),
        tooltip=[
            alt.Tooltip('group:N').title('Group'),
            alt.Tooltip('mean(value):Q').title('Mean').format('.2f'),
            alt.Tooltip('stdev(value):Q').title('Sample SD').format('.2f'),
        ],
    )
    summaries = (
        (intervals + means)
        .properties(width=135, height=220)
        .facet(
            column=alt.Column('dataset:N').sort(SCENARIOS).title(None),
            title='Mean ± one sample SD: identical in every panel',
        )
    )

    observations = base.mark_circle(size=40, opacity=0.8).encode(
        y=y,
        x=group_axis('jittered_position'),
        tooltip=[
            alt.Tooltip('dataset:N').title('Dataset'),
            alt.Tooltip('group:N').title('Group'),
            alt.Tooltip('observation:O').title('Observation'),
            alt.Tooltip('value:Q').title('Value').format('.2f'),
        ],
    )
    counts = (
        alt.Chart(data)
        .transform_aggregate(n='count()', groupby=['dataset', 'group', 'group_position'])
        .transform_calculate(label='"n = " + datum.n')
        .mark_text(color='#555', fontSize=11)
        .encode(x=x, y=alt.YDatum(38).scale(domain=[0, 40]), text='label:N')
    )
    distributions = (
        (observations + counts)
        .properties(width=135, height=220)
        .facet(
            column=alt.Column('dataset:N').sort(SCENARIOS).title(None),
            title='Individual observations: different shapes and sample sizes',
        )
    )

    return (
        alt.vconcat(summaries, distributions, spacing=30)
        .resolve_scale(y='shared', color='shared')
        .properties(title=alt.Title(
            text='The same summaries can hide different distributions',
            subtitle=[
                'Group A: mean 12, SD 4. Group B: mean 17, SD 4. Error bars show SD, not SEM or confidence intervals.',
                'Synthetic examples inspired by Weissgerber et al. (2015), PLOS Biology, doi:10.1371/journal.pbio.1002128.',
            ],
            anchor='start',
        ))
        .configure_view(stroke=None)
        .configure_header(labelFontSize=13, labelFontWeight='bold')
        .configure_axis(labelFontSize=11, titleFontSize=12)
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=TEXTBOOK / '_book' / 'same_mean_sd.html')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    chart = same_mean_sd_chart()
    chart.save(args.output)
    print(f'Saved chart to {args.output}')
