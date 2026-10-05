# Shared build-time HTML previews for Quarto R chunks.
# source("utils.R"); show_df(cars)
# Uses reticulate and the formatter in utils.py, with original R type labels.
show_df <- function(df, max_rows = 6L, index = TRUE) {
  if (!is.null(max_rows) &&
      (length(max_rows) != 1L || !is.numeric(max_rows) ||
       !is.finite(max_rows) || max_rows < 1 || max_rows != floor(max_rows))) {
    stop("max_rows must be a positive integer or NULL.")
  }

  # A list keeps even a single-column table's label from becoming a Python string.
  types <- unname(lapply(df, pillar::type_sum))
  preview <- reticulate::import("utils")$show_df(
    df,
    max_rows = if (is.null(max_rows)) NULL else as.integer(max_rows),
    index = index,
    dtypes = types
  )

  htmltools::HTML(preview$data)
}
