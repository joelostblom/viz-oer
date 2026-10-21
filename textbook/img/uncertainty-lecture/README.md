# Uncertainty lecture figures

These figures were extracted from `Copy of DSCI 531 - Lec 7.odp`, supplied by
Joel Ostblom, for the opening of `17_uncertainty.qmd`. Embedded images are retained
at their original resolution. The hypothetical-outcome GIF retains its animation.
The lecture's administrative opening and unrelated interactivity speaker notes
were not imported.

| File | Slide | Attribution / source information |
|:--|:--|:--|
| `election-probabilities.png` | 3 | The slide credits Justin H. Gross, Washington Post, http://wapo.st/2fCYvDW. Historical 2016 forecast comparison. |
| `election-frequency-seats.png` | 4 | Same credit. Theater seats re-express the forecast probabilities as frequencies; the first panel uses 286 per 1,000 versus the rounded 28% on slide 3. |
| `election-distributions.png` | 7 | FiveThirtyEight's 2020 presidential election forecast, https://projects.fivethirtyeight.com/2020-election-forecast/. Historical screenshot; exact capture date not recorded in the deck. |
| `election-scenarios.png` | 7 | Same forecast; screenshot includes 10 Trump wins, 89 Biden wins, and one no-majority scenario per 100. |
| `unlabeled-penguin-intervals.png` | 9 | Penguin body-mass chart embedded in the lecture. The deck does not specify the interval calculation; retained as an interpretation exercise, not labeled as a CI. |
| `distribution-and-interval.png` | 10 | Schematic embedded in the lecture; original source and interval definition not recorded. |
| `interval-definitions.png` | 11 | Claus O. Wilke, *Fundamentals of Data Visualization*, Figure 16.5, https://clauswilke.com/dataviz/visualizing-uncertainty.html#fig:cocoa-data-vs-CI. Data credit: Brady Brelinski, Manhattan Chocolate Society. Cropped to the chart at pixel box (35, 32, 810, 374), removing surrounding webpage text. |
| `interval-overlap.png` | 12 | Schematic embedded in the lecture; original source and statistical assumptions not recorded. The chapter explicitly cautions against generalizing its printed p-values. |
| `fitted-curves-and-band.png` | 13 | Wilke, Figure 16.18, https://clauswilke.com/dataviz/visualizing-uncertainty.html#fig:mpg-uncertain. Spline fits to Motor Trend car data; alternative fits are posterior draws. |
| `hypothetical-fitted-curves.gif` | 13 | Wilke, Figure 16.22, https://clauswilke.com/dataviz/visualizing-uncertainty.html#fig:mpg-uncertain-HOP-animated. |
| `hurricane-cone-and-paths.png` | 14 | Comparison embedded in the lecture; slide notes link to https://www.youtube.com/watch?v=byDZlMwi7kU. Original image attribution not specified in the deck. |

Additional links retained from the slide notes:

- https://www.youtube.com/watch?v=-Zc47NNGwm4 (frequency framing / uncertainty communication).
- https://idl.cs.washington.edu/papers/when-ish-is-my-bus/ (uncertainty visualization research).

Extraction preserves existing third-party figures; it does not assign them a new
license or establish that they share the textbook's license.

To repeat the extraction from the original deck:

```sh
uv run --with pillow python textbook/src/export_uncertainty_figures.py \
    "/path/to/Copy of DSCI 531 - Lec 7.odp"
```
