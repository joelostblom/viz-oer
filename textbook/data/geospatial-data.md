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
- `geospatial-us-states-2024.geojson`: 2024 US Census cartographic state
  boundaries at 1:20 million, obtained with
  `tigris::states(cb = TRUE, resolution = '20m', year = 2024)`. The snapshot
  retains the 50 states and DC, their `GEOID`, `STUSPS`, and `NAME` attributes,
  and WGS84 geometry. Source:
  <https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip>.
  The R inset maps apply `tigris::shift_geometry()` to this local file.

The two Natural Earth files use WGS84 longitude/latitude (`EPSG:4326`); coordinates are rounded to
five decimal places while retaining the source ring winding. Natural Earth data
are public domain: <https://www.naturalearthdata.com/about/terms-of-use/>.

These files are prepared GeoJSON copies of the zipped shapefile downloads
linked above. The US Census boundaries are public-domain US government data.
Natural Earth also distributes GeoJSON exports through its
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

The Altair and ggplot tabs use these same boundaries and statistical tables.
Country maps use Natural Earth's historical GDP/population attributes, not a
separate GDP snapshot. Both language versions use the 2021 Canadian population
counts and 2012 US election results.

For the R US inset maps, the 2012 results are joined directly to the shifted
Census features using `NAME` and `name`. All 51 regions must match, totaling
538 electoral votes: Democratic 332 and Republican 206. The 2024 boundary date
does not change the election year or its electoral-vote allocation. Symbol
locations are computed inside the shifted polygons so that all R map layers
share the same display coordinates.

The R examples read boundaries with `sf::st_read()`, retain the geometry column
for `geom_sf()`, and convert the ggplots with `ggplotly()`. The converted maps
contain their projected geometry and do not need supporting geographic files
from Plotly's CDN. No example depends on a live boundary-data download.

## Recreating the snapshots

From the repository root:

```sh
uv run python textbook/src/data_processing/prepare_geospatial_data.py
```

This refreshes the Natural Earth and Vega data.

With the project's R environment activated, regenerate the Census snapshot with:

```sh
Rscript textbook/src/data_processing/prepare_geospatial_us_states.R
```

To also recover the original population/election tables, provide the
instructor notebook:

```sh
uv run python textbook/src/data_processing/prepare_geospatial_data.py --lecture /path/to/lectures/4-geoviz.ipynb
```

Importing reads saved chart specifications, not truncated dataframe previews or changing live
web tables. The importer checks the Canadian population total and the US
electoral-vote totals before writing the snapshots.
