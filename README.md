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
make slides   # Render the chapter 1 and chapter 2 presentations
```

Preview and book builds use the shared `activate-uvr` recipe fragment to activate the
project's R environment, then launch Quarto in the Python environment managed
by uv. For example, `make preview` is equivalent to:

```sh
. .uvr/activate
uv run quarto preview textbook
```

Press Ctrl+C to stop the preview.

### Reading and presentation views

Chapters 1 and 2 open as ordinary textbook pages. Their small **Present slides**
icons beside the chapter titles (screens with tooltips and accessible labels)
open Reveal.js decks generated from the same chapter `.qmd` files.
In the deck, use arrow keys to navigate, **F** for fullscreen, **S** for speaker
notes, **O** to toggle the slide overview, **M** for the menu, and **?** for
keyboard shortcuts. **Esc** dismisses an open menu, help overlay, or overview
first; from a normal slide it returns to the matching section of the reading view.
Esc also resumes a paused/black screen before allowing an exit.
The opening title uses the accent color; other slide titles are blue. Figures and tables
are left aligned, with captions hidden in the deck and retained in the chapter.
Only the title slide has a footer: **Press ? for shortcuts**. The bottom-left
hamburger icon is hidden; the menu remains available through **M**.
The hint fades away after five seconds each time the title slide is entered.
Hovering over its bottom-center area shows it again for as long as the pointer
stays there.
Slide changes and content reveals use quick 180 ms fades. Each slide opens with
only its heading; the next advance reveals its learning-outcomes block, chart,
table, or image as one fragment. Visuals stay intact rather than animating table
cells or individual chart marks. Revisiting a slide resets it to heading-only.
Reduced-motion preferences suppress the animation while keeping the same reveal
steps.

Chapter 1 includes the title, learning outcomes, all section/subsection headings,
both Anscombe tables, the Altair chart, and the Datasaurus animation. Chapter 2
also includes the exercise dataset, declarative/imperative charts and pseudocode,
arithmetic code examples, grammar implementations, margin images, and both
visualization-ecosystem diagrams.

Nested tab headings become separate slides. Exercise callout boxes are unpacked:
their selected visuals appear directly on slides, while prompts, hints, and
solutions remain in speaker notes. Notes label exercise, hint, and solution
sections, and keep explanatory footnotes inline. Sections without selected
content have heading-only slides with their explanation in the notes.

The chapter uses lightweight annotations:

- `chapter-slides: slides/1_why-visualize-data.html` enables its presentation link.
- A `.slide-outcomes` div wraps the learning outcomes.
- A `.slide-visual` div wraps each chart, image, or table selected for slides.
  It can be nested inside an exercise, tabset, or margin note. It can also contain
  code with its chart so they appear together as one fragment.
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

Add `slide-title="A classroom question"` to a `.slide-visual` div to give that
visual a dedicated slide title. Otherwise it uses the current heading, with
additional slides when multiple visual blocks would share a slide. Escape from
tab/exercise slides returns to the enclosing visible chapter section, rather
than a hidden tab or collapsed solution.

For a new local image or data file, also add its path to the staging list in
`CHAPTER_ASSETS` in `textbook/src/build_chapter_slides.py`. Chapter 1 stages the
Datasaurus image; chapter 2 stages `utils.py`. The knitr include and slide assets
are shared. Remote images retain their source URLs, and Mermaid diagrams are
rendered through Quarto as in the textbook.

`chapter-slides.lua` handles the two views. `_chapter-slides.yml` selects the
Reveal format and output location; `chapter-slides.css` controls slide layout.
`chapter-slides.js` implements Escape navigation and resets fragments when entering
a slide. Decks and chapters use matching HTML filenames, with decks one directory
deeper in `slides/`, so the return URL works for each chapter automatically.
`chapter-title-tools.js` places the chapter's presentation icon beside its title.
The chapter's normal render triggers `textbook/src/build_chapter_slides.py` as a Quarto
post-render hook. It copies the chapter and its required assets into a temporary
standalone project outside the book directory, renders the deck there, and copies the
finished presentation into `_book/slides/`. Isolation prevents the slide build
from changing Quarto's cached preview format for the reading page. This also works
with `make preview` updates and `make book`, without an extra manual slide build.
Each registered chapter executes twice when rendered: once for each output format.
An incremental render rebuilds only the deck for the chapter that was rendered.

Generated files:

- Reading view: `textbook/_book/1_why-visualize-data.html`
- Slide view: `textbook/_book/slides/1_why-visualize-data.html`
- Reading view: `textbook/_book/2_grammar-of-graphics.html`
- Slide view: `textbook/_book/slides/2_grammar-of-graphics.html`

Both are part of the published `_book` directory. The deck has its own generated
assets, so the reading pages are not overwritten. To render only the slide decks:

```sh
make slides
```

This activates the same R/Python environments as the other Make targets and runs
`uv run python textbook/src/build_chapter_slides.py --force`. `make book` and
`make preview` invoke the builder indirectly through the post-render hook in
`textbook/_quarto.yml`, so they do not need a separate `slides` prerequisite.

To build one presentation, use `--chapter`, for example:

```sh
. .uvr/activate
uv run python textbook/src/build_chapter_slides.py --chapter 2_grammar-of-graphics
```

To add another chapter, register its filename stem and assets in `CHAPTER_ASSETS`,
add its `chapter-slides` metadata link, and annotate its content. Restart an
existing preview after changing project configuration or the hook.

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
