"""Compare eruption-interval distributions for the ten Yellowstone geysers.

Requires pandas, numpy, and altair. Download bin_eruption.csv from:
https://datadryad.org/dataset/doi:10.5061/dryad.s1rn8pkbv

This script follows the documented column names and six-minute sampling grid.
The original CSV could not be downloaded in the preparation environment, so
its actual contents and the Altair rendering have not been verified here.

Rows must retain their original order and the complete six-minute grid.
Set TIME_COLUMN to a timestamp column, if available, to validate that grid and
exclude intervals spanning omitted timestamps as well as explicit missing cells.
Do not interpret the binary detections as eruption durations.
"""

import numpy as np
import pandas as pd

NAMES = {
    "BE": "Beehive", "CA": "Castle", "DE": "Depression", "DO": "Dome",
    "GR": "Grand", "LN": "Lion", "LS": "Little Squirt",
    "OF": "Old Faithful", "PT": "Plate", "PM": "Plume",
}
SAMPLE_MINUTES = 6
TIME_COLUMN = None  # Optional: exact name of an ISO-style timestamp column.
TARGET_BINS = 30


def eruption_intervals(raw, time_column=None):
    """Return intervals in sampling steps, without crossing known data gaps."""
    raw = raw.copy().reset_index(drop=True)
    raw.columns = raw.columns.astype(str).str.strip()
    missing = set(NAMES) - set(raw.columns)
    if missing:
        raise ValueError(f"Expected geyser columns {sorted(missing)}; found {list(raw.columns)}")

    breaks = pd.Series(False, index=raw.index)
    if time_column is not None:
        # Explicit UTC conversion also accepts timestamps with timezone offsets.
        time = pd.to_datetime(raw[time_column], errors="raise", utc=True)
        if time.isna().any() or not time.is_monotonic_increasing or time.duplicated().any():
            raise ValueError("Timestamps must be present, unique, and increasing.")
        breaks = time.diff().ne(pd.Timedelta(minutes=SAMPLE_MINUTES))

    parts = []
    for code, name in NAMES.items():
        signal = pd.to_numeric(raw[code], errors="raise")
        if (signal.notna() & ~signal.isin([0, 1])).any():
            raise ValueError(f"{code}: expected only 0, 1, or missing values.")

        # Every 1 marks a detected eruption; do not merge consecutive detections.
        segment = (signal.isna() | breaks).cumsum()
        rows = np.flatnonzero(signal.eq(1).fillna(False).to_numpy(dtype=bool))
        events = pd.DataFrame({"row": rows, "segment": segment.iloc[rows].to_numpy()})
        steps = events.groupby("segment", sort=False)["row"].diff().dropna()
        if steps.empty:
            raise ValueError(f"{name}: no complete intervals are available.")
        parts.append(pd.DataFrame({
            "geyser": name,
            "interval_steps": steps.to_numpy(dtype=int),
        }))

    intervals = pd.concat(parts, ignore_index=True)
    intervals["interval_hours"] = intervals["interval_steps"] * SAMPLE_MINUTES / 60
    return intervals


def histogram_table(intervals):
    """Bin separately by geyser, aligned with the six-minute resolution."""
    parts = []
    for name, group in intervals.groupby("geyser", sort=False):
        values = group["interval_steps"].to_numpy()
        width = max(1, int(np.ceil((values.max() - values.min() + 1) / TARGET_BINS)))
        start = (values.min() // width) * width
        stop = (values.max() // width + 1) * width
        edges = np.arange(start, stop + width, width)
        counts, _ = np.histogram(values, bins=edges)
        hours_per_step = SAMPLE_MINUTES / 60
        width_hours = width * hours_per_step

        parts.append(pd.DataFrame({
            "geyser": name,
            "start_hours": edges[:-1] * hours_per_step,
            "end_hours": edges[1:] * hours_per_step,
            "count": counts,
            "density": counts / (len(values) * width_hours),
            "mean_hours": group["interval_hours"].mean(),
            "n_intervals": len(values),
        }))
    return pd.concat(parts, ignore_index=True)


def make_chart(histograms):
    import altair as alt

    base = alt.Chart(histograms)
    bars = base.mark_bar(color="#287C8E", opacity=0.85).encode(
        x=alt.X("start_hours:Q", title="Interval between eruptions (hours)",
                scale=alt.Scale(zero=False)),
        x2="end_hours:Q",
        y=alt.Y("density:Q", title="Density (per hour)", scale=alt.Scale(zero=True)),
        tooltip=[
            alt.Tooltip("geyser:N", title="Geyser"),
            alt.Tooltip("start_hours:Q", title="From (hours)", format=".2f"),
            alt.Tooltip("end_hours:Q", title="To (hours)", format=".2f"),
            alt.Tooltip("count:Q", title="Intervals in bin"),
            alt.Tooltip("n_intervals:Q", title="Total intervals"),
        ],
    )
    means = base.transform_aggregate(
        mean_hours="max(mean_hours)", groupby=["geyser"]
    ).mark_rule(color="#C45130", strokeDash=[5, 4], strokeWidth=1.5).encode(
        x="mean_hours:Q",
        tooltip=alt.Tooltip("mean_hours:Q", title="Mean interval (hours)", format=".2f"),
    )
    return (
        (bars + means).properties(width=250, height=180)
        .facet(facet=alt.Facet("geyser:N", title=None, sort=list(NAMES.values())), columns=3)
        .resolve_scale(x="independent", y="independent")
        .properties(title=alt.TitleParams(
            text="Yellowstone geysers: distributions of eruption intervals",
            subtitle=[
                "Dashed lines: means. Each histogram has total area 1.",
                "Axes and bin widths vary by geyser; all complete intervals are retained.",
                "Source: Thompson et al. (2024), Dryad. Detections have six-minute resolution.",
            ], anchor="start",
        ))
        .configure_view(stroke=None)
        .configure_axis(labelFontSize=11, titleFontSize=11, gridColor="#eeeeee")
        .configure_header(labelFontSize=14, labelFontWeight="bold")
    )


if __name__ == "__main__":
    raw = pd.read_csv("bin_eruption.csv")
    intervals = eruption_intervals(raw, time_column=TIME_COLUMN)
    histograms = histogram_table(intervals)
    chart = make_chart(histograms)
    intervals.to_csv("yellowstone_eruption_intervals.csv", index=False)
    chart.save("yellowstone_geyser_histograms.html")
    print(intervals.groupby("geyser")["interval_hours"].agg(["count", "mean", "median"]).round(2))

# In a notebook or Quarto cell, put `chart` as the final expression to display it.
