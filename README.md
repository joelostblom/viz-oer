# viz-oer

An interactive open educational resource for learning data visualization.

## Previewing and building the textbook

Install the Python dependencies with `uv sync`. Altair currently comes from
the `feat/to_html-should-work-as_save_html` branch on GitHub, which fixes
VegaFusion HTML output through reticulate. The resolved commit is pinned in
`uv.lock`.

From the repository root:

```sh
make preview  # Start the live preview
make book     # Render the textbook
make slides   # Render only the chapter 1 presentation
```

Preview and book builds use the shared `activate-uvr` recipe fragment to activate the
project's R environment, then launch Quarto in the Python environment managed
by uv. For example, `make preview` is equivalent to:

```sh
. .uvr/activate
uv run quarto preview textbook
```

Press Ctrl+C to stop the preview.

### Chapter 1: reading and presentation views

Chapter 1 opens as an ordinary textbook page. Its small **Present slides** icon
beside the chapter title (a screen, with a tooltip and accessible label)
opens a Reveal.js deck generated from the same `1_why-visualize-data.qmd` file.
In the deck, use arrow keys to navigate, **F** for fullscreen, **S** for speaker
notes, **O** to toggle the slide overview, and **Esc** to return to the matching
section of the reading view (including when the overview is open).
The opening title is purple; other slide titles are blue. Figures and tables
are left aligned, with captions hidden in the deck and retained in the chapter.
There is no presentation footer. The custom Escape shortcut exits the deck
without disabling Reveal's normal overview shortcut.
Slide changes and content reveals use quick 180 ms fades. Each slide opens with
only its heading; the next advance reveals its learning-outcomes block, chart,
table, or image as one fragment. Visuals stay intact rather than animating table
cells or individual chart marks. Revisiting a slide resets it to heading-only.
Reduced-motion preferences suppress the animation while keeping the same reveal
steps.

The pilot includes the title, learning outcomes, all section/subsection
headings, both Anscombe tables, the Altair chart, and the Datasaurus animation.
The section prose becomes speaker notes. Sections without a visual have a
heading-only slide with their explanation in the notes.

The chapter uses lightweight annotations:

- `chapter-slides: slides/1_why-visualize-data.html` enables its presentation link.
- A `.slide-outcomes` div wraps the learning outcomes.
- A `.slide-visual` div wraps each chart, image, or table selected for slides.
- A `.slide-text` span selects a phrase/sentence within a paragraph; a
  `.slide-text` div selects a whole paragraph, list, or block.
- All chapter headings become slide headings, including subsections.
- Other content after a heading becomes speaker notes for that slide.

To reuse part of a paragraph without writing it twice:

```markdown
Visualization helps us [**recognize patterns** more quickly]{.slide-text}
than a table of raw numbers.
```

The entire paragraph appears normally in the textbook and remains available in
speaker notes, where the selected passages are bold to make them easy to locate.
Only the marked phrase appears on the slide, as a bulleted fade-in fragment
under the current heading. Formatting and links inside the brackets are retained.
Multiple marked spans become separate fragments, in reading order.
The first letter of each selected paragraph or list item is automatically
capitalized in slides, including excerpts starting with bold text or a link.
The rest of the capitalization is preserved; chapter text and speaker notes
retain their original wording. Leading code identifiers and formulas stay literal.

For a whole paragraph or a group of bullets, use a div instead:

```markdown
::: {.slide-text}
Visualization supports both exploration and communication.
:::
```

The block appears normally in the chapter and becomes one bulleted slide fragment.
Its paragraphs and list items are also bold in speaker notes.
Each paragraph becomes a bullet; existing lists are used directly without adding
an extra bullet level. These
are project-specific annotations implemented by `chapter-slides.lua`, not native
Quarto selection syntax. Place inline selections after their section heading.

These wrappers do not hide or duplicate material in the reading view. Code
executes normally before slide selection, so data-loading cells remain available
to later chart cells. To add another visual to this pilot deck, wrap it in:

```markdown
::: {.slide-visual}

![Caption](img/example.svg)

:::
```

For a new local image or data file, also add its path to the staging list in
`textbook/src/build_chapter_slides.py`. The pilot currently stages the Datasaurus image and
the shared knitr setup include; the chart data come from Altair's dataset loader.

`chapter-slides.lua` handles the two views. `_chapter-slides.yml` selects the
Reveal format and output location; `chapter-slides.css` controls slide layout.
`chapter-slides.js` implements Escape navigation using the chapter URL specified
in the slide template and resets fragments when entering a slide.
`chapter-title-tools.js` places the chapter's presentation icon beside its title.
The chapter's normal render triggers `textbook/src/build_chapter_slides.py` as a Quarto
post-render hook. It copies the chapter and its required assets into a temporary
standalone project outside the book directory, renders the deck there, and copies the
finished presentation into `_book/slides/`. Isolation prevents the slide build
from changing Quarto's cached preview format for the reading page. This also works
with `make preview` updates and `make book`, without an extra manual slide build.
The pilot executes chapter 1 twice: once for each output format.

Generated files:

- Reading view: `textbook/_book/1_why-visualize-data.html`
- Slide view: `textbook/_book/slides/1_why-visualize-data.html`

Both are part of the published `_book` directory. The deck has its own generated
assets, so the reading page is not overwritten. To render only the pilot deck:

```sh
make slides
```

This activates the same R/Python environments as the other Make targets and runs
`uv run python textbook/src/build_chapter_slides.py --force`. `make book` and
`make preview` invoke the builder indirectly through the post-render hook in
`textbook/_quarto.yml`, so they do not need a separate `slides` prerequisite.

Other chapters are unaffected. Expanding the pilot requires registering another
chapter and its assets in the build hook/template and setting its return link, as well as adding
the chapter annotations. Restart an existing preview after changing project
configuration or the hook.

### Synchronized language tabs

Tabsets sharing `group="language"` still switch languages together.
`textbook/tabset-scroll.js` keeps the clicked tab bar at its current screen
position when panels above it change height, including delayed chart/image
resizing. It releases that position when the reader scrolls or interacts again.

### Dataframe previews

The shared `textbook/utils.py` module provides `show_df()` for HTML previews
with column names, a separate datatype header row, and the first and last three
rows separated by an ellipsis. Short dataframes are shown in full; truncated
previews also show the full row and column counts.

Import it in a chapter's Python setup chunk:

```python
from utils import show_df

show_df(cars)                     # pandas dataframe
show_df(cars, max_rows=10, index=False)
```

For R dataframes and tibbles, source the companion helper in an R setup chunk:

```r
source("utils.R")

show_df(cars)
show_df(cars, max_rows = 10, index = FALSE)
show_df(cars, max_rows = NULL)  # Show all rows
```

The R helper captures the original column types with `pillar::type_sum()` before
reticulate converts the data for the shared Python formatter. Its datatype row
uses familiar tibble labels such as `dbl`, `int`, `chr`, `fct`, and `date`.
Both helpers leave the original table unchanged.

The R helper runs during document rendering and requires desktop R/Python via
reticulate; it is not a webR helper. In Python chunks, `show_df(r.cars)` remains
available, but reports the converted pandas types instead of R's original types.
Both helper files are declared as book-wide resources. Chapters with their own
`resources` list should also include `utils.py` there so that the live extension
mounts it for browser Python exercises.

### Execution caching

Chunk caching is disabled in `textbook/_quarto.yml`. These chapters use knitr
for both R and Python, with Python executed through reticulate. Reusing a cached
Python chunk's output does not recreate its imports, dataframes, or chart objects
in a fresh Python session. If a later chunk changes and is re-executed, this can
cause errors such as `NameError: name 'pd' is not defined` or a missing `points`
object. A fully cached render can succeed, making the problem seem intermittent.

Keep the default `cache: false` for chapters whose Python chunks depend on one
another. This makes chapter rendering do more work, but keeps the execution state
consistent. Existing `*_cache/` directories can remain; they are ignored while
caching is disabled. Restart a running preview after changing this setting.

For a one-off render that bypasses caching explicitly:

```sh
. .uvr/activate
uv run quarto render textbook/6_order.qmd --no-cache
```
