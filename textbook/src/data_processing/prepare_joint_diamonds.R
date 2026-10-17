# Export the two columns used in the joint-distributions chapter.
# Run explicitly; rendering the textbook never writes source data.
script_arg <- commandArgs(trailingOnly = FALSE)
script <- sub('^--file=', '', script_arg[startsWith(script_arg, '--file=')])
data_dir <- normalizePath(file.path(dirname(script), '..', '..', 'data'))

diamonds <- ggplot2::diamonds[c('carat', 'price')]
stopifnot(nrow(diamonds) == 53940, !anyNA(diamonds),
          all(diamonds$carat > 0), all(diamonds$price > 0))
write.csv(diamonds, file.path(data_dir, 'diamonds-carat-price.csv'),
          row.names = FALSE, quote = FALSE)
cat('Exported', nrow(diamonds), 'rows from ggplot2',
    as.character(packageVersion('ggplot2')), '\n')
