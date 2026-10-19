# Color lecture figures

These original figures were extracted from Joel Ostblom's supplied
`Copy of DSCI 531 - Lec 6.odp` lecture deck for the Color chapter.
The PNGs and animated checker-shadow GIF are copied without re-encoding.
Original labels and embedded credits are preserved. Transparent figures are
displayed on white in the chapter and slideshow so their black labels remain
readable in the book's dark theme.

Repeated images, overlapping alternatives, administrative/title-only slides,
the decorative "Color School" interlude, and the blank final slide are omitted.
Repeated views of the same figure use one image asset.

## Credits carried from the slides

- The checker-shadow illustration and animation credit Edward H. Adelson.
- The RGB and HSL models credit SharkD and are licensed
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/):
  [RGB source](https://commons.wikimedia.org/w/index.php?curid=9803320) and
  [HSL source](https://commons.wikimedia.org/w/index.php?curid=9801661).
- The hue/saturation/lightness swatches and numerical/categorical comparisons
  refer to the [Seaborn palette tutorial](https://seaborn.pydata.org/tutorial/color_palettes.html).
- The palette/lightness reference diagrams refer to the
  [Matplotlib colormap guide](https://matplotlib.org/stable/users/explain/colors/colormaps.html).

Source slide numbers, archive members, and source/image checksums are recorded
in `manifest.json`.

To regenerate the images:

```sh
uv run python textbook/src/export_color_figures.py "/path/to/Copy of DSCI 531 - Lec 6.odp"
```

The exporter uses only Python's standard library. Book rendering uses the
committed image assets and does not need the original ODP or LibreOffice.
