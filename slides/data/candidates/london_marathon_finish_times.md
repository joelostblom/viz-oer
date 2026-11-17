# London Marathon finish times

`london_marathon_finish_times.csv` contains the same observations used in the
bin-width exercise in `binned.qmd`. It is an extract from
the author-provided file `Respository London Marathon 18-23.csv`.

- Keep rows where `gender == 1` and `agecat == "18-39"`, matching the male
  18–39 sample described in Binned.
- Interpret the first whitespace-separated part of `fulltime` as a duration,
  then convert seconds to minutes.
- Keep only the column `Time (minutes)`; discard missing finish times.
- Do not bin, average, smooth, or otherwise alter the observations.

The author has confirmed that the source contains only results from the
2023 London Marathon, despite the `18-23` filename. The original file has no
year column; the year is established by the author's confirmation.

The saved extract has 12,805 observations. It allows the density-bandwidth
exercise in Smoothed to run without accessing a personal Downloads folder.
The selectable density curves are computed from these observations during render;
the CSV stores the observations themselves, not the curves.

To regenerate from the original file:

```sh
uv run python src/data_processing/candidates/prepare_marathon_finish_times.py \
    "/path/to/Respository London Marathon 18-23.csv"
```

The discussion of target finish times refers to *Reference-Dependent Preferences:
Evidence from Marathon Runners*:
<https://doi.org/10.1287/mnsc.2015.2417>. That article motivates the interpretation;
it is not the source of this author-provided London Marathon file.
