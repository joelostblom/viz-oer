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
```

Preview and book builds use the shared `activate-uvr` recipe fragment to activate the
project's R environment, then launch Quarto in the Python environment managed
by uv. For example, `make preview` is equivalent to:

```sh
. .uvr/activate
uv run quarto preview textbook
```

Press Ctrl+C to stop the preview.
