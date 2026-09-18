# viz-oer

An interactive open educational resource for learning data visualization.

## Previewing and building the textbook

Install the Python dependencies with `uv sync`. Altair currently comes from
the `feat/to_html-should-work-as_save_html` branch on GitHub, which fixes
VegaFusion HTML output through reticulate. The resolved commit is pinned in
`uv.lock`.

From the repository root:

```sh
make preview  # Start the live preview
make book     # Render the textbook
```

Preview and book builds use the shared `activate-uvr` recipe fragment to activate the
project's R environment, then launch Quarto in the Python environment managed
by uv. For example, `make preview` is equivalent to:

```sh
. .uvr/activate
uv run quarto preview textbook
```

Press Ctrl+C to stop the preview.

### Dataframe previews

The shared `textbook/utils.py` module provides `show_df()` for HTML previews
with column names, a separate datatype header row, and the first and last three
rows separated by an ellipsis. Short dataframes are shown in full; truncated
previews also show the full row and column counts.

Import it in a chapter's Python setup chunk:

```python
from utils import show_df

show_df(cars)                     # pandas dataframe
show_df(cars, max_rows=10, index=False)
```

For R dataframes and tibbles, source the companion helper in an R setup chunk:

```r
source("utils.R")

show_df(cars)
show_df(cars, max_rows = 10, index = FALSE)
show_df(cars, max_rows = NULL)  # Show all rows
```

The R helper captures the original column types with `pillar::type_sum()` before
reticulate converts the data for the shared Python formatter. Its datatype row
uses familiar tibble labels such as `dbl`, `int`, `chr`, `fct`, and `date`.
Both helpers leave the original table unchanged.

The R helper runs during document rendering and requires desktop R/Python via
reticulate; it is not a webR helper. In Python chunks, `show_df(r.cars)` remains
available, but reports the converted pandas types instead of R's original types.
Both helper files are declared as book-wide resources. Chapters with their own
`resources` list should also include `utils.py` there so that the live extension
mounts it for browser Python exercises.

### Execution caching

Chunk caching is disabled in `textbook/_quarto.yml`. These chapters use knitr
for both R and Python, with Python executed through reticulate. Reusing a cached
Python chunk's output does not recreate its imports, dataframes, or chart objects
in a fresh Python session. If a later chunk changes and is re-executed, this can
cause errors such as `NameError: name 'pd' is not defined` or a missing `points`
object. A fully cached render can succeed, making the problem seem intermittent.

Keep the default `cache: false` for chapters whose Python chunks depend on one
another. This makes chapter rendering do more work, but keeps the execution state
consistent. Existing `*_cache/` directories can remain; they are ignored while
caching is disabled. Restart a running preview after changing this setting.

For a one-off render that bypasses caching explicitly:

```sh
. .uvr/activate
uv run quarto render textbook/6_order.qmd --no-cache
```
