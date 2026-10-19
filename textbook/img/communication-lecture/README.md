# Communication lecture figures

These original PNG images were extracted from Joel Ostblom's supplied
`Copy of DSCI 531 - Lec 5.odp` lecture deck. Images are used in the
Communication chapter, with the trendline comparison figures in Trends.
Original labels, embedded credits, and chart details are preserved.

Several source slides reveal images by layering them over earlier examples.
Extracting the underlying figures keeps both stages available for comparison.
Duplicate layers are exported once. The administrative opening page,
overplotting examples, hidden climate example, and blank final page are omitted.
The LOESS animation already available in `img/loess-local-regression.gif`
continues to illustrate the local-fitting process in Trends.

The source slide and archive member for every image, plus source and image
checksums, are recorded in `manifest.json`.

To regenerate these assets from the ODP:

```sh
uv run python textbook/src/export_communication_figures.py "/path/to/Copy of DSCI 531 - Lec 5.odp"
```

The exporter uses only Python's standard library. Rendering the book uses the
committed images and does not require the original ODP or LibreOffice.
