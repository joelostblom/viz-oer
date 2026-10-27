# Geospatial chapter data and lecture assets

The Geospatial chapter adapts `lectures/4-geoviz.ipynb` from the DSCI 532
instructor materials. Data and assets were imported on 2026-10-25. All chapter
data are local snapshots; rendering does not scrape Wikipedia or download map
boundaries. OpenStreetMap tiles in the GeoPandas `explore()` example still
require a network connection.

## Boundaries

- `geospatial-world-countries.geojson`: 177 Natural Earth Admin 0 features at
  1:110 million, including Antarctica (excluded in the chapter's comparisons).
  Selected source attributes retain population/GDP estimates and reference years.
  Source: <https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip>.
- `geospatial-world-regions.geojson`: 294 Natural Earth Admin 1 features at
  1:50 million, covering selected countries. It includes all 13 Canadian provinces
  and territories, and all 50 US states plus the District of Columbia. Selected
  attributes retain names, country codes, representative point coordinates, and
  Wikipedia links. Geometries are simplified with a 0.025-degree tolerance and
  topology preservation for overview maps; they are not suitable for precise
  measurements or detailed local boundary work.
  Source: <https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_1_states_provinces.zip>.

Both files use WGS84 longitude/latitude (`EPSG:4326`); coordinates are rounded to
five decimal places while retaining the source ring winding. Natural Earth data
are public domain: <https://www.naturalearthdata.com/about/terms-of-use/>.

These files are prepared GeoJSON copies of the zipped shapefile downloads
linked above. Natural Earth also distributes GeoJSON exports through its
project repository: <https://github.com/nvkelso/natural-earth-vector/tree/master/geojson>.
Our preparation selects attributes and simplifies the regional geometry for
these examples; the local files are not byte-for-byte copies of those repository
exports. GeoPandas can also read the source shapefiles directly.

## Tables

- `geospatial-canada-population-2021.csv`: the 13 regional population counts
  saved in the original notebook, corresponding to the 2021 census. Total:
  36,991,981. Names retain `Québec` to match the boundary data. The notebook's
  source was <https://en.wikipedia.org/wiki/Population_of_Canada_by_province_and_territory>.
- `geospatial-us-election-2012.csv`: 2012 winning party and electoral-vote
  allocation, recovered from the notebook's saved chart data. The District of
  Columbia is normalized to its boundary name and retained with three Democratic
  electoral votes. The total is 538: Democratic 332, Republican 206. These are
  electoral-vote allocations, not popular-vote counts. Original table sources:
  <https://en.wikipedia.org/wiki/United_States_Electoral_College> and
  <https://en.wikipedia.org/wiki/2012_United_States_elections>.
- `geospatial-earthquakes.csv`: longitude, latitude, depth in kilometers,
  magnitude, and place from the historical USGS sample distributed by Vega.
  Source: <https://raw.githubusercontent.com/vega/vega-datasets/main/data/earthquakes.json>.

The Altair and Plotly R tabs use these same boundaries and statistical tables.
Country maps use Natural Earth's historical GDP/population attributes, not a
separate GDP snapshot. Both language versions use the 2021 Canadian population
counts and 2012 US election results.

## Browser geometry

`plotly-geo/world_110m.json` and `plotly-geo/usa_110m.json` are the TopoJSON files
from <https://cdn.plot.ly/world_110m.json> and
<https://cdn.plot.ly/usa_110m.json>. The R examples set
`config(topojsonURL = 'data/plotly-geo/')` to use these local files rather than
requesting geography from the CDN.

## Recreating the snapshots

From the repository root:

```sh
uv run python textbook/src/data_processing/prepare_geospatial_data.py
```

This refreshes Natural Earth and Vega data and Plotly's supporting TopoJSON.
To also recover the original population/election tables, provide the
instructor notebook:

```sh
uv run python textbook/src/data_processing/prepare_geospatial_data.py --lecture /path/to/lectures/4-geoviz.ipynb
```

Importing reads saved chart specifications, not truncated dataframe previews or changing live
web tables. The importer checks the Canadian population total and the US
electoral-vote totals before writing the snapshots.
