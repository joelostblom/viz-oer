# Same mean and SD, different distributions

These are **synthetic teaching data**, inspired by Fig. 1 of Weissgerber,
Milic, Winham, and Garovic (2015), *Beyond Bar and Line Graphs: Time for a New
Data Presentation Paradigm*, PLOS Biology 13(4): e1002128.
<https://doi.org/10.1371/journal.pbio.1002128>

The values are newly constructed, not digitized or recovered from the paper.
Unlike the original mean ± SEM example, the accompanying visualization shows
**mean ± one sample standard deviation**. It includes no inferential tests.

## Data

`same_mean_sd.csv` has four columns:

- `dataset`: one of the five scenarios below.
- `group`: A or B, corresponding to the two groups within a panel.
- `observation`: an identifier within each dataset/group, not a pairing between groups.
- `value`: a synthetic measurement in arbitrary units.

In **every scenario**, group A has mean **12**, group B has mean **17**, and
both groups have sample SD **4** (using the `n - 1` denominator). These values
match to floating-point precision, rather than merely rounding to similar numbers.
This equality is within corresponding groups across scenarios; pooling A and B
would answer a different question, especially in the unequal-size scenario.

| Dataset | Group A | Group B |
|---|---|---|
| Symmetric | 24 symmetric, normal-shaped values | 24 symmetric, normal-shaped values |
| Outlier | Same symmetric values as the first panel | 23 tightly clustered values and one large outlier |
| Bimodal | Two separated clusters of 12 values | Two separated clusters of 12 values |
| Right-skewed | 24 values with a long upper tail | 24 values with a long upper tail |
| Unequal n | 24 symmetric values | 8 symmetric values |

The unequal-size panel demonstrates that an SD interval does not communicate
sample size. The other panels demonstrate differences in shape, clustering,
and outliers that the same mean and SD can hide.

## Construction

Normal and exponential quantiles provide predictable distribution shapes.
The bimodal example combines two narrow clusters; the outlier example combines
a narrow cluster with one distant value. Each group's values are then centered
and scaled to the target mean and sample SD. A fixed random seed shuffles their
row order. This creates controlled examples rather than random samples from
an unknown population.

The chart adds deterministic horizontal jitter solely to separate overlapping
points. It does not jitter the measured values or change the statistics. All
panels use the same vertical scale, and the SD intervals and means are calculated
from the saved observations by Altair/Vega-Lite.

## Regenerate

From the repository root:

```sh
uv run python src/data_processing/candidates/create_same_mean_sd_data.py
uv run python src/data_processing/candidates/same_mean_sd.py
```

The chart is exported to `_book/same_mean_sd.html`. Use `--output`
with an `.svg` or `.png` filename for a static figure. In a notebook or chapter
with the repository root as the working directory, use:

```python
from src.data_processing.candidates.same_mean_sd import same_mean_sd_chart

same_mean_sd_chart()
```
