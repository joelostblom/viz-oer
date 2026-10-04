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
make slides   # Render the chapter key and all developed chapters (1–10)
```

Preview and book builds use the shared `activate-uvr` recipe fragment to activate the
project's R environment, then launch Quarto in the Python environment managed
by uv. For example, `make preview` is equivalent to:

```sh
. .uvr/activate
uv run quarto preview textbook
```

Press Ctrl+C to stop the preview.

### GitHub Actions publishing

The publishing and PR-preview workflows share
`.github/actions/setup-book/action.yml`. They use `uv.lock` and `uvr.lock`,
rather than the older `environment.yaml` Conda environment:

- uv 0.10.4 restores Python and packages with `uv sync --locked`, including the
  pinned Altair Git revision. `.python-version` selects the Python version.
- uvr 0.4.6 installs the R version recorded in `uvr.lock` and restores its
  packages with `uvr sync --frozen --install-system-deps`.
- Quarto 1.10.18 matches the tested local renderer. A current Chrome installation
  is explicitly selected via `QUARTO_CHROMIUM` for Mermaid diagrams.
- `RETICULATE_PYTHON` explicitly selects `.venv/bin/python` so Python chunks
  cannot accidentally run in a separate reticulate-managed environment.
- Both workflows activate `.uvr/activate` and run
  `uv run --locked quarto render textbook`. The post-render hook builds the
  slide decks as part of the same publication.

Python and R downloads are cached. When changing dependencies, commit both the
manifest and its lockfile; if frozen R installation reports a stale lock, run
`uvr lock`, review the changes, then run `uvr sync --frozen` locally.

Production publishes `textbook/_book` to the existing `gh-pages` branch, matching
the repository's Pages setting (**Deploy from a branch**, `gh-pages`, `/`).
The production deployment removes obsolete pages and assets, while preserving
the complete `pull<number>/` and `diff<number>/` PR snapshots. It uses
`JamesIves/github-pages-deploy-action` with cleanup exclusions and non-forced
pushes. Obsolete chapter URLs such as `1_intro.html` are removed rather than
redirected.
Same-repository PRs also publish preview/diff directories; fork PRs render for
validation but skip publishing because their tokens lack write access.
Push to `main` to publish, or use **Actions → Render and Publish → Run workflow**
after workflow changes have reached GitHub.

### Reading and presentation views

Figures in the reading view are left-aligned and use margin captions by default
(`fig-align: left`, `fig-cap-location: margin`). Figure captions display a bold
**Figure N** label on its own line, followed by the caption text. The
`figure-captions.js` helper aligns captions moved out of exercise callouts with
their figures and updates positioning after resizing, chart loading, or
expanding/collapsing an exercise. On narrow screens, Quarto's in-flow caption
layout is used. Table captions remain below their tables.
`figure-caption-links.lua` preserves links and cross-references when Quarto
moves figure captions into a callout's margin, by keeping the caption contents
inside a single HTML wrapper.

The reading view offers Quarto's built-in light/dark theme toggle in the book
sidebar. The default dark theme uses Darkly
with a small `textbook/tokyo-night.scss` customization matching the slide palette.
Dark-mode code highlighting reuses `textbook/tokyo-night.theme` from the slides;
light mode uses Quarto's default Arrow highlighting.
Cosmo remains available as the optional light theme.
Quarto remembers the reader's choice. Custom callouts also adapt to dark mode.
The slide decks retain their separate dark presentation theme.

The chapter key and all developed chapters (1–10) open as ordinary textbook pages. Their small **Present slides**
icons beside the chapter titles (screens with tooltips and accessible labels)
open Reveal.js decks generated from the same chapter `.qmd` files.
In the deck, use arrow keys to navigate, **F** for fullscreen, **S** for speaker
notes, **O** to toggle the slide overview, **M** for the menu, and **?** for
keyboard shortcuts. **Esc** dismisses an open menu, help overlay, or overview
first; from a normal slide it returns to the matching section of the reading view.
Esc also resumes a paused/black screen before allowing an exit. **Q** is an
alias for Esc, with the same behavior for overlays, overview, and returning to
the chapter.
To export, close any open shortcut help, press **E** for PDF-export mode, then
use the browser's print dialog to **Save as PDF**. Press **E** again to return
to normal presentation mode.
The opening title uses the accent color; other slide titles are blue. Figures and tables
are left aligned, with captions hidden in the deck and retained in the chapter.
Only the title slide has a footer: **Press ? for shortcuts**. The bottom-left
hamburger icon is hidden; the menu remains available through **M**.
The hint fades away after three seconds each time the title slide is entered.
Hovering over its bottom-center area shows it again for as long as the pointer
stays there.
Slide changes and content reveals use quick 180 ms fades. Each slide opens with
only its heading; the next advance reveals its learning-outcomes block, chart,
table, or image as one fragment. Visuals stay intact rather than animating table
cells or individual chart marks. Revisiting a slide resets it to heading-only.
Reduced-motion preferences suppress the animation while keeping the same reveal
steps.

The chapter-key deck is a compact five-slide test deck: title, presentation
shortcuts, learning outcomes, exercises, and coding content. It demonstrates
grouped heading/code reveals and delayed Python/R output, with exercise hints
and solutions in speaker notes.

Chapter 1 includes the title, learning outcomes, all section/subsection headings,
both Anscombe tables, the Altair chart, and the Datasaurus animation. Chapter 2
also includes the exercise dataset, declarative/imperative charts and pseudocode,
arithmetic code examples and grammar implementations.

Chapters 3–10 have first-draft decks covering their key principles, selected
exercise visuals, diagrams/animations, and Altair/ggplot examples. Short examples
show source and output together; longer examples show the chart with explanations
in speaker notes. Language-tab headings are skipped where examples have their
own descriptive slide titles. Deep dives and margin notes are excluded. The
placeholder chapters (11–17) have no decks yet.

Charts and static plots are constrained to the slide canvas, including tall
faceted charts, without changing the chart specifications used in the book.
`#| slide-chart-columns: 5` can reflow a faceted Altair chart into five columns
only in slides; chapter 5 uses this to keep its regional comparison readable.
Speaker-note chapter and figure references link back to the reading view.

Nested tab headings follow the same slide-placement rules as other headings.
Exercise callout boxes are unpacked:
their selected visuals appear directly on slides, while prompts, hints, and
solutions remain in speaker notes. Notes label exercise, hint, and solution
sections, and keep explanatory footnotes inline. Sections without selected
content have heading-only slides with their explanation in the notes.

The chapter uses lightweight annotations:

- `chapter-slides: slides/1_why-visualize-data.html` enables its presentation link.
- A `.slide-outcomes` div wraps the learning outcomes.
  Optionally mark shorter `.slide-bullet` spans within it to show just those
  excerpts; the complete outcomes remain in speaker notes and the textbook.
- A `.slide-visual` div wraps each chart, image, or table selected for slides.
  It can be nested inside an exercise or tabset. It can also contain
  code with its chart so they appear together as one fragment.
- `.slide-text` selects plain text without adding bullet points.
- `.slide-bullet` selects bullet text: plain paragraphs become bullets, and
  existing lists retain their type, numbering, and nesting.
- `.slide-subbullet` adds a nested bullet beneath the preceding selected bullet,
  with its own reveal step. It must follow a bullet on the same slide/column.
  All three classes support inline spans and block divs and share the same
  selection, fragment, and speaker-note handling.
- Plain chapter headings start new slides, including subsections.
- Add `.slide-with-content` to a heading to start a new slide and reveal that
  heading together with its first selected text or visual block.
  Combine it with `.slide-fragment` to reveal a heading and its first selected
  block together on the current slide. Each heading/content pair gets its own
  animation step.
- A heading with `.slide-fragment` stays on the current slide and reveals as a
  subheading. Subsequent selected content stays there until the next plain heading
  or an explicit `slide-title` starts a new slide. This also works on tab headings.
- Executable R/Python cells can select code, output, or both with `slide-show`.
- Other content after a heading becomes speaker notes for that slide.
- `.deep-dive` blocks are excluded entirely from presentations, including their
  headings, selected content, and speaker notes. They remain in the textbook.
- `.column-margin` blocks are likewise excluded entirely from presentations.
- Add `.slide-skip` to a heading, for example `### Details {.slide-skip}`, to omit
  only that heading and its slide break. Following content uses the preceding
  slide and the normal selection rules (including automatic visual continuation
  slides). The heading remains visible in the textbook.
  On a div, `.slide-skip` excludes the entire block from slides and notes.

#### Headings: placement and animation

Prefer **heading annotations for headings**, and **wrappers for selecting and
grouping content**. Keep real headings outside text-selection and `.slide-visual`
wrappers so their slide placement is explicit.

| Intent | Heading markup |
|---|---|
| New slide; heading appears first | `### Title` |
| New slide; heading and first selected block reveal together | `### Title {.slide-with-content}` |
| Same slide; heading reveals separately | `### Title {.slide-fragment}` |
| Same slide; heading and first selected block reveal together | `### Title {.slide-fragment .slide-with-content}` |

With `.slide-with-content`, the heading and its first selected block share one
advance. Later blocks retain their own reveal steps. Multiple heading/content
pairs on the same slide reveal in sequence, rather than all at once.

For separate heading and text reveals:

```markdown
## A new slide

[First point]{.slide-bullet}

### A heading on the same slide {.slide-fragment}

[Another point]{.slide-bullet}

## The next slide
```

The subheading and selected text reveal separately. In the textbook, these
remain ordinary headings and paragraphs.

For a heading and its bullets to reveal together on the current slide:

```markdown
### Imperative instruction {.slide-fragment .slide-with-content}

::: {.slide-bullet}

**"Loop over the dataframe and plot observations in each group."**

**Focus**: Explicit instructions for constructing the chart.

:::
```

Remove `.slide-fragment` from the heading to start a new slide instead, while
keeping the heading and bullets in the same animation step. The same heading
annotations work when the next selected block is `.slide-visual` rather than
`.slide-bullet` or `.slide-text`.

#### Executable code and output

For executable cells in the current knitr-based chapters:

````markdown
```{python}
#| echo: false
#| slide-show: both

print(1 + 1)
```
````

Use `slide-show: code` for source only, `output` for results only, or `both`
for source and results together as one fragment. No `.slide-visual` wrapper is
needed. These choices override `echo`, `output`, and `include` visibility only
in slides; the example above still hides source in the textbook. Execution and
dependencies are retained, and `eval: false` is respected. Cells without
`slide-show` retain their existing behavior. Static code can still be selected
with a `.slide-visual` wrapper.
Use `#| slide-title: A descriptive title` on a cell with `slide-show` to give
its selected code/output a dedicated slide. This is useful when the chapter's
language-tab headings have `.slide-skip`.

Add `#| slide-output-fragment: true` alongside `#| slide-show: both` to reveal
the source first and all of that cell's output together on the next advance.
This is useful for asking students to predict the answer. The output still
executes during rendering; only its presentation is delayed. The option also
works for cells inside a `.slide-visual` wrapper and does not affect the book.

Slide code uses the custom `textbook/tokyo-night.theme`: dark background, purple
keywords, green strings, orange numbers, and blue functions. It is configured
only in the presentation template.
Slide text and headings use the OS interface font (`system-ui`); code uses
`ui-monospace` with platform-appropriate fallbacks. No Ubuntu webfont download
is needed. The font stacks are set in `_chapter-slides.yml` and
`chapter-slides.css`.

#### Selecting text

To select an excerpt from a paragraph:

```markdown
Visualization helps us [**recognize patterns** more quickly]{.slide-bullet}
than a table of raw numbers.
```

The entire paragraph appears normally in the textbook and remains available in
speaker notes, where the selected passages are bold to make them easy to locate.
Only the marked phrase appears on the slide, as a bulleted fade-in fragment
under the current heading. Formatting and links inside the brackets are retained.
Multiple marked spans become separate fragments, in reading order.
For bullet and subbullet selections, the first letter of each paragraph or list
item is automatically
capitalized in slides, including excerpts starting with bold text or a link.
The rest of the capitalization is preserved; chapter text and speaker notes
retain their original wording. Leading code identifiers and formulas stay literal.

For a whole paragraph or a group of bullets, use a div instead:

```markdown
::: {.slide-bullet}
Visualization supports both exploration and communication.
:::
```

The block appears normally in the chapter and becomes one bulleted slide fragment.
Its paragraphs and list items are also bold in speaker notes.
Each paragraph becomes a bullet; existing lists retain their type, numbering,
and nesting without adding an extra bullet level. These
are project-specific annotations implemented by `chapter-slides.lua`, not native
Quarto selection syntax. Place inline selections after their section heading.

For plain slide text, use `.slide-text` instead:

```markdown
::: {.slide-text}
What else might explain this association?
:::
```

To reveal supporting detail as a subbullet of the preceding bullet:

```markdown
[Compare observations within groups.]{.slide-bullet}

[Income may be related to both variables.]{.slide-subbullet}

[The pooled trend may differ from the within-group trend.]{.slide-subbullet}
```

Each child reveals separately beneath the parent; the chapter still displays
the original text normally. A `.slide-subbullet` div can select a whole block,
including several paragraphs or list items that should reveal together. It
attaches to the last item of the preceding selected list. Plain `.slide-text`
paragraphs are not parent bullets. Existing bullet annotations were migrated
from `.slide-text` to `.slide-bullet` when this distinction was introduced.

Warning-callout headings are preserved in slides (including headings used by
Quarto as the callout title). Use `.slide-bullet` or `.slide-text` to select the
warning's visible explanation; its remaining prose becomes speaker notes.

#### Visuals and grouped fragments

These wrappers do not hide or duplicate material in the reading view. Code
executes normally before slide selection, so data-loading cells remain available
to later chart cells. To add another visual to a chapter deck, wrap it in:

```markdown
::: {.slide-visual}

![Caption](img/example.svg)

:::
```

For two items inside one visual block, `slide-layout="columns"` places the items
side by side in slides. Chapter 4 uses this for its circle/bar comparison. The
book keeps the items' original layout.

Add `slide-title="A classroom question"` to a `.slide-visual` div to give that
visual a dedicated, presentation-only slide title. Use this when there is no
corresponding source heading; do not repeat the title as a heading inside the
wrapper. Otherwise it uses the current heading, with
additional slides when multiple visual blocks would share a slide (except after
a `.slide-fragment` heading, which explicitly keeps content together). Add
`.slide-with-content` to a titled `.slide-visual` block to reveal its generated
title and content together, including when it also has `.slide-columns`.
Escape from
tab/exercise slides returns to the enclosing visible chapter section, rather
than a hidden tab or collapsed solution.

Use a `.slide-fragment` div to reveal a group of content blocks together on the
current slide, particularly when there is no source heading:

````markdown
::: {.slide-fragment slide-title="Adding strings"}

```python
"one" + "two"
```

:::
````

The optional title and the block's content appear together as one fragment;
this does not start a new slide. You can also combine `.slide-visual` and
`.slide-fragment` on the same div. For real source headings, prefer the heading
annotations in the table above.

A `.slide-bullet` div nested inside a `.slide-fragment` block still converts plain
paragraphs to bullets and preserves existing lists. It shares the outer block's
animation. Existing markup with a heading inside a `.slide-fragment` or
`.slide-visual` wrapper remains supported for compatibility, but heading
annotations are the recommended approach for new content.

#### Two-column comparisons

For a two-example comparison like chapter 2's syntax examples, add
`.slide-columns` to the enclosing tabset. Use a plain heading for the first
example, a `.slide-fragment` heading for the second, and one `.slide-visual`
block per example. Slides put the first heading and example in the left column
and the second in the right column. Each chart stays below its code, with long
code lines wrapping as needed. The book retains its normal tabs and stacked
code/output layout.

Both examples must belong to the same slide: a second plain heading starts
another slide, so mark it `.slide-fragment`. Add `.slide-with-content` to reveal
that heading together with its chart, as in chapter 5's comparison:

```markdown
::: {.panel-tabset .slide-columns}

### Overall

<!-- Selected visual or cell with slide-show: output -->

### By group {.slide-fragment .slide-with-content}

<!-- Selected visual or cell with slide-show: output -->

:::
```

Cells inside this comparison should omit `slide-title`, which starts a dedicated
slide. An output-only cell already reveals as a fragment; `slide-output-fragment`
is useful when delaying a result after displayed code, and is unnecessary here.

To put a **full-width title above both columns**, place a plain heading before
the tabset and make both column headings fragments:

```markdown
## Simpson's paradox

::: {.panel-tabset .slide-columns}

### Overall {.slide-fragment .slide-with-content}

<!-- Selected visual or cell with slide-show: output -->

### By group {.slide-fragment .slide-with-content}

<!-- Selected visual or cell with slide-show: output -->

:::
```

The main title appears first. Each column heading and its first selected block
then reveal together, left column followed by right column. `slide-widths` works
with this layout too. The book retains its normal headings and tabs. Chapter 5
uses this full-width-title layout for its aggregation comparison.

This layout currently supports two columns. The former `.slide-comparison`
name remains supported as a compatibility alias; use `.slide-columns` for new
content.

Set `slide-widths` on that same tabset to adjust the left/right proportions:

```markdown
::: {.panel-tabset .slide-columns slide-widths="40,60"}
```

The two positive numbers are relative weights: `40,60` gives 40%/60% of the
available column space after the gap, and `2,3` gives the same split. Omitting
the option gives equal columns. This setting affects only the presentation.

You can also start a two-column slide with a titled `.slide-visual` block,
then supply the right column as a titled `.slide-fragment` block:

````markdown
::: {.slide-visual slide-title="Adding numbers" .slide-columns}

```python
1 + 2
```

:::

::: {.slide-fragment slide-title="Adding strings"}

```python
"one" + "two"
```

:::
````

The second title and its content reveal together in the right column. Optional
`slide-widths="40,60"` goes on the first block alongside `.slide-columns`.

Local images referenced in the chapter's Markdown or raw HTML are discovered
and staged automatically by `textbook/src/build_chapter_slides.py`. Adding or
renaming an image in the `.qmd` needs no staging-list edit: rebuild the deck
(`make slides` or the normal book/preview render) and reload it. The discovery
supports reference-style Markdown images, project-root-relative paths such as
`/img/example.svg`, and URL-encoded paths. Commented-out images and code examples
are ignored. A missing referenced file produces an error identifying its path.

Data files and other runtime dependencies still go in `CHAPTER_ASSETS`, since
they can be loaded dynamically by Python/R code. That list accepts individual
files or directories; chapter 3 stages its declared `data` directory. The knitr
include, slide assets, `utils.py`, and `utils.R` are shared. Remote images retain
their source URLs, and Mermaid diagrams are rendered through Quarto as in the
textbook. New image files must still be committed for CI to access them.

Image-discovery regression checks can be run with:

```sh
uv run --locked python -m unittest discover -s textbook/tests
```

`chapter-slides.lua` handles the two views. `_chapter-slides.yml` selects the
Reveal format and output location; `chapter-slides.css` controls slide layout.
`chapter-slide-options.lua` preserves tab-heading annotations before Quarto
processes tabsets. The builder appends `_slide-chunks.qmd` to the staged knitr
include to implement presentation-only cell visibility.
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

- Reading view: `textbook/_book/0_chapter-key.html`
- Slide view: `textbook/_book/slides/0_chapter-key.html`
- Reading view: `textbook/_book/1_why-visualize-data.html`
- Slide view: `textbook/_book/slides/1_why-visualize-data.html`
- Reading view: `textbook/_book/2_grammar-of-graphics.html`
- Slide view: `textbook/_book/slides/2_grammar-of-graphics.html`

Chapters 3–10 follow the same pattern, for example
`textbook/_book/slides/9_binned-distributions.html`.

All decks are part of the published `_book` directory. Each deck has its own generated
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
