# Diamond weight and price

This is the complete `carat` and `price` column pair from `ggplot2::diamonds`
(53,940 observations), exported with ggplot2 4.0.3. No observations were sampled,
filtered, or aggregated.

- `carat`: diamond weight in carats (one carat is 0.2 grams).
- `price`: price in US dollars, as recorded in the source dataset.
- Documentation and original data source:
  <https://ggplot2.tidyverse.org/reference/diamonds.html>.

The joint-distributions chapter reads this local CSV in both languages so that
the Altair and ggplot examples use exactly the same observations. This is a
historical dataset, not current diamond prices.

Recreate the file from the project R environment:

```sh
Rscript textbook/src/data_processing/prepare_joint_diamonds.R
```
