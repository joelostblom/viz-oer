# Communication, color, and trends example data

These CSV snapshots preserve the datasets used in the original DSCI 531
communication and color lectures. They are exported through the
[`vega_datasets` Python package](https://github.com/vega/vega_datasets) from
the [Vega datasets collection](https://github.com/vega/vega-datasets).

- `vega-cars.csv`: automobile specifications, including year, horsepower, and
  origin; used for trendlines in chapter 16 and car examples in chapters 18–19.
- `vega-iris.csv`: Fisher's iris measurements and species; used for color
  scales in chapter 14. The R examples use the equivalent built-in `iris` data.
- `vega-gapminder.csv`: country-level development indicators; used to compute
  the correlation matrix in chapter 14 and to compare years interactively in chapter 19.
- `vega-wheat.csv`: historical wheat prices; used for highlighting and
  annotations in chapter 14.
- `vega-stocks.csv`: stock-price series; used for ordering legends and direct
  labeling in chapter 14.

The full diamond carat/price data used in chapters 12 and 13 are in
`diamonds-carat-price.csv`; their provenance is recorded in
`diamonds-carat-price.md`.

To regenerate the Vega snapshots, run:

```sh
uv run --with vega-datasets python textbook/src/data_processing/prepare_communication_color_data.py
```

Regeneration can access the network. Ordinary chapter rendering only reads the
committed CSVs and does not regenerate them.
