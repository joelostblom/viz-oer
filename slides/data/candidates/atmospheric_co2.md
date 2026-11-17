# Atmospheric CO₂ from 1700 onward

`atmospheric_co2.csv` contains just two columns:

- `date`: calendar date in ISO format (`YYYY-MM-DD`).
- `co2`: atmospheric CO₂ concentration in parts per million (ppm).

## Sources and preparation

The preparation follows the sources and 1958 handoff in Scripps'
[1700-to-present Keeling Curve notebook](https://github.com/sio-co2o2/keelingcurve_notebooks/blob/main/notebooks/create_graphic_icecore_start_1700_ce_keelingcurve.ipynb).

1. **Before 1958:** use `CO2 Age (year AD)` and `CO2 (ppm)` from the
   [Law Dome dataset](https://raw.githubusercontent.com/sio-co2o2/keelingcurve_notebooks/main/icecore_data/Law_Dome_GHG_2000years_co2_by_age.csv).
   The date is the estimated age of the trapped gas, not the age of the ice.
   Retain records from 1700 through 1957. The first available record in that
   interval is 1703; no observation is invented for 1700. Unlike the notebook's
   plotting-boundary workaround, this CSV does not include the preceding 1694 record.
2. **From 1958:** use `date_filled` and `co2_filled` from the
   [Scripps combined Mauna Loa file](https://raw.githubusercontent.com/sio-co2o2/keelingcurve_notebooks/main/preliminary_data/mlo/mlo_full_record_now_span.csv).
   This is the notebook's gap-filled monthly series. It retains the seasonal
   cycle; it is **not** `co2_seas_adj` or a seasonally adjusted fit. Missing
   monthly values have already been filled by Scripps using their fitted series.
3. **Latest observations:** append nonmissing `date`/`co2` observations later
   than the last gap-filled monthly value. These newer daily baseline averages
   are in the same source file but are omitted by the notebook's choice of columns.
4. Drop missing date/value pairs, sort chronologically, and exclude observations
   after the requested cutoff date (today by default). The record ends at the
   latest available observation, not necessarily today; the script does not extrapolate.

Decimal years are converted using the actual length of each calendar year,
including leap years, and rounded to the nearest second before extracting the
date to avoid floating-point boundary errors. Integer ice-core gas ages are
represented as January 1 for plotting; this does not imply day-level dating
precision. Multiple ice-core samples assigned to the same year are retained
without averaging. The series therefore has irregular spacing and changes
from historical ice-core records to monthly, then recent daily observations.

Recent Scripps values are preliminary and may be revised. This is a combined
ice-core/Mauna Loa record, not a spatially averaged global CO₂ series.

## Regenerate

From the repository root:

```sh
uv run python src/data_processing/candidates/create_co2_data.py
uv run python src/data_processing/candidates/co2.py
```

The first command refreshes the CSV from the upstream sources. The second
exports the Altair chart to `_book/co2.html` with pan/zoom and tooltips.

## Attribution

Data are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Credit the **Scripps Institution of Oceanography at UC San Diego** and the
ice-core data authors:

- Rubino, M., Etheridge, D., Thornton, D., Allison, C., Francey, R., Langenfelds, R.,
  Steele, P., Trudinger, C., Spencer, D., Curran, M., Van Ommen, T., and Smith, A.
  (2019). *Law Dome Ice Core 2000-Year CO₂, CH₄, N₂O and δ¹³C-CO₂*. v1. CSIRO.
  <https://doi.org/10.25919/5bfe29ff807fb>.
- Keeling, C. D., Piper, S. C., Bacastow, R. B., Wahlen, M., Whorf, T. P.,
  Heimann, M., and Meijer, H. A. (2001). *Exchanges of atmospheric CO₂ and ¹³CO₂
  with the terrestrial biosphere and oceans from 1978 to 2000. I. Global aspects*.
  SIO Reference Series 01-06. <https://escholarship.org/uc/item/09v319r9>.

See also the [upstream data and graphics license](https://github.com/sio-co2o2/keelingcurve_notebooks/blob/main/LICENSE.md)
and [Scripps data archive](https://doi.org/10.6075/J08W3BHW).
