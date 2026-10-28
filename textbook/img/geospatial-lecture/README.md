# Geospatial lecture figures

These original images were extracted from Joel Ostblom's supplied
`lec4-maps.odp` lecture deck. They support the Geospatial chapter's introductory
map-type and projection discussion, choropleth interpretation, geographic
aggregation, inset scales, and cartograms.

The original PNG bytes, labels, and resolution are preserved. The projection
animation is the original 211-frame GIF. `manifest.json` records the source
slide, archive member, source and image SHA-256 checksums, and URLs credited on
each source slide.

## Credits and interpretation

- Slides 3/5 and 6: Mercator and Equal Earth imagery, credited to
  <https://map-projections.net/compare.php?p1=equalearth&p2=mercator-84>.
- Slide 4: the globe-to-flat-map animation, preserved from the supplied lecture.
  The slide's projection reference is Statistics Canada; the animation's
  original creator is not separately identified in the deck.
- Slide 11: Alaska and Hawaii repositioned without shrinking Alaska relative
  to the contiguous states. The image appears in Claus Wilke's projection
  discussion: <https://clauswilke.com/dataviz/geospatial-data.html#projections>.
- Slides 12–13: Mark Newman's 2012 election illustrations, CC BY 2.0.
  The distorted image on slide 13 is the **population** cartogram, not the
  electoral-vote cartogram. Its pixels exactly match `statepop1024.png` from
  the archived original page:
  <https://web.archive.org/web/20240000000000id_/http://www-personal.umich.edu/~mejn/election/2012/>.
- Slides 14–15: Financial Times tile and circle cartograms showing the 2012
  election result, with area representing **electoral votes**. The article
  explains these examples and their tradeoffs:
  <https://www.ft.com/content/3685bf9e-a4cc-11e6-8b69-02899e8bd9d1>.
- Slides 18–20: Claus Wilke's population-density and median-income figures,
  using the 2015 five-year American Community Survey:
  <https://clauswilke.com/dataviz/geospatial-data.html#choropleth-mapping>.
  The county and state income figures have different legend cutpoints; the
  chapter explicitly explains that their colors are not directly comparable.
- Slide 21: the lecture's choropleth, point-map, and proportional-symbol
  comparison, credited to <https://www.youtube.com/watch?v=LPcEttrNV_E>.

The title/learning-goal pages and duplicate Mercator image are omitted.
The existing executable chapter examples cover the remaining projection,
proportional-symbol, and map/bar-chart comparisons.

## Regenerating

From the repository root:

```sh
uv run python textbook/src/export_geospatial_figures.py /path/to/lec4-maps.odp
```

The exporter uses only Python's standard library. Rendering the chapter uses
the extracted local assets and does not require the original ODP or LibreOffice.
