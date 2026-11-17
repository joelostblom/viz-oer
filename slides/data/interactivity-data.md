# Interactivity example data

- `vega-cars.csv` is the existing automobile-specification snapshot used elsewhere
  in the textbook; see `communication-color-data.md` for its provenance.
- `vega-movies-interactivity.csv` contains the full Vega movies dataset (3,201 rows),
  before the interactivity chapter's explicit missing-value filters. This is
  distinct from `movies.csv`, the smaller textbook distribution-example dataset.
  Column-name spaces are replaced with underscores to retain the lecture's field
  names; values and rows are otherwise unchanged.
- `vega-sp500.csv` contains the Vega S&P 500 time series used for the overview/detail
  selection example.

The latter two are exported from the [Vega datasets collection](https://github.com/vega/vega-datasets)
through `altair.datasets.data`. Rendered chapters read these local snapshots rather
than retrieving data from a URL in the browser. To regenerate them:

```sh
uv run python src/data_processing/prepare_interactivity_data.py
```

Paired Python and R examples use the same local snapshots and missing-value filters:
cars for tooltips, selections, linked views, and variable switching; S&P 500 for
overview/detail navigation; movies for category and numeric controls; and
`vega-gapminder.csv` for the year-slider/animation comparison.
The latter contains fertility, life expectancy, population, and country over time;
its provenance is recorded in `communication-color-data.md`.
Car and movie identifiers are assigned after filtering and used as stable linking keys.
Plotly and Crosstalk provide browser-side R interactions; their versions are in `uvr.lock`.

The chapter adapts `lectures/8-figure-composition-Copy1.ipynb` from the DSCI 531
instructor materials. The composition/export chapter adapts the composition and
saving sections of `lectures/layouts-saving.ipynb`.
