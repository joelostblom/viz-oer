# Save Census state boundaries locally for the Geospatial chapter.
# Run from the repository root:
# Rscript src/data_processing/prepare_geospatial_us_states.R

script <- sub('^--file=', '', grep('^--file=', commandArgs(), value = TRUE)[1])
destination <- file.path(dirname(normalizePath(script)), '..', '..', 'data',
                         'geospatial-us-states-2024.geojson')

states_sf <- tigris::states(cb = TRUE, resolution = '20m', year = 2024,
                            progress_bar = FALSE) |>
    dplyr::filter(STUSPS %in% c(state.abb, 'DC')) |>
    dplyr::select(GEOID, STUSPS, NAME) |>
    sf::st_transform(4326)

stopifnot(nrow(states_sf) == 51, !anyDuplicated(states_sf$STUSPS),
          all(c(state.abb, 'DC') %in% states_sf$STUSPS))
sf::st_write(states_sf, destination, driver = 'GeoJSON', delete_dsn = TRUE,
             layer_options = 'RFC7946=YES', quiet = TRUE)
cat('Saved', nrow(states_sf), 'Census state boundaries to', normalizePath(destination), '\n')
