# Seattle weather: EDA teaching example

- Source: the [`seattle-weather.csv` example in vega-datasets](https://github.com/vega/vega-datasets/blob/main/data/seattle-weather.csv).
- Upstream project: <https://github.com/vega/vega-datasets>.
- Coverage: 1,461 daily records, 2012-01-01 through 2015-12-31.
- Source SHA-256 for this snapshot: `0845078a290b48e3149ab8639966824110a251db4e06fc144c06ebb534af23be`.
- Variables: date, precipitation (mm), maximum and minimum temperature (°C), wind speed (m/s), and a weather category.
- `seattle-weather-complete.csv` preserves the source values in these six columns.
- `seattle-weather-sensor.csv` is a **teaching modification**, not a record of an actual sensor failure. Minimum and maximum temperatures at or below 0.6°C are replaced with missing values. No rows or weather categories are removed; other fields retain their source values.
- The complete version is retained solely to reveal the known mechanism and demonstrate its effect. In ordinary missing-data problems, the unobserved values would not be available for this comparison.
- The source weather categories describe the day; this example does not establish how they were assigned or whether they were measured independently of the numerical fields.

To recreate both CSVs explicitly (never during a chapter render):

```sh
python textbook/src/data_processing/prepare_eda_weather.py
```

The script checks the schema, record count, date uniqueness, endpoints, and absence of empty source values, and prints the downloaded source's SHA-256 and the numbers of removed measurements.
