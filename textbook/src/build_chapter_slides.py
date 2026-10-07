"""Quarto post-render hook: keep registered chapter slide views up to date.

Invoked after book renders, including preview rebuilds. Slide rendering runs in
an isolated temporary project so it cannot change the book's preview-format
cache. Only the completed deck and its assets are copied into the book output.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

CHAPTER_ASSETS = {
    "0_chapter-key": (),
    "1_why-visualize-data": (),
    "2_grammar-of-graphics": (),
    "3_individual-observations": ("data",),
    "4_magnitude": (),
    "5_groups": (
        "data/income_lifeexp_alcohol.csv", "data/simpsons_paradox_data_l.csv",
    ),
    "6_connections": (
        "data/co-emissions-per-capita.csv", "data/gapminder_world_from_1850.csv",
        "data/gapminder_regions_from_1850.csv", "data/gapminder_world_trends.csv",
        "data/movie_scores.csv",
    ),
    "7_summaries": (
        "data/meditation-stress-sample.csv", "data/same_mean_sd.csv",
    ),
    "8_counts": ("data/meditation-stress-sample.csv",),
    "9_binned-distributions": (
        "data/movies.csv", "data/london_marathon_finish_times.csv",
    ),
    "10_smoothed-distributions": (
        "data/movies.csv", "data/london_marathon_finish_times.csv",
    ),
}
SHARED_ASSETS = (
    "illustrative-chart-actions.lua",
    "chapter-slides.lua", "chapter-slides.css", "chapter-slides.js",
    "chapter-slide-tabs.js",
    "chapter-slide-options.lua", "tokyo-night.theme",
    "_extensions/r-wasm/live/_knitr.qmd",
    "utils.py", "utils.R",
)


class ImageSources(HTMLParser):
    """Find images in raw HTML without mistaking comments for markup."""

    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            attrs = dict(attrs)
            source = attrs.get("src") or attrs.get("data-src")
            if source:
                self.sources.append(source)


def discover_local_images(quarto, project, source):
    """Parse chapter images without executing cells or copying remote URLs."""
    markdown = source.read_text(encoding="utf-8")
    # Pandoc expects {.python}, whereas Quarto executable cells use {python}.
    # Normalize these fences so examples containing Markdown/HTML stay code.
    markdown = re.sub(
        r"^([ \t]*(?:`{3,}|~{3,}))\{([A-Za-z][\w.+-]*)(?:[ ,][^}\n]*)?\}[^\n]*$",
        lambda match: match[1] + "{." + match[2] + "}",
        markdown, flags=re.MULTILINE,
    )
    ast = json.loads(subprocess.check_output(
        [quarto, "pandoc", "--from", "markdown", "--to", "json"],
        input=markdown, text=True, cwd=project,
    ))
    references = []

    def collect(node):
        if isinstance(node, list):
            for child in node:
                collect(child)
        elif isinstance(node, dict):
            kind = node.get("t")
            if kind in ("Code", "CodeBlock"):
                return
            content = node.get("c", [])
            if kind == "Image":
                references.append(content[2][0])
            elif kind in ("RawInline", "RawBlock") and content[0] == "html":
                parser = ImageSources()
                parser.feed(content[1])
                parser.close()
                references.extend(parser.sources)
            collect(content)

    collect(ast["blocks"])
    images = set()
    project = project.resolve()
    for reference in references:
        url = urlsplit(reference)
        if url.scheme or url.netloc or not url.path:
            continue
        path = Path(unquote(url.path))
        image = (project / str(path).lstrip("/")) if path.is_absolute() else source.parent / path
        # Normalize .. while preserving a referenced symlink's filename in the
        # staged project; resolving it would copy the target under another name.
        image = Path(os.path.abspath(image))
        if not image.is_relative_to(project) or not image.resolve().is_relative_to(project):
            raise ValueError(f"Image path leaves the textbook project in {source.name}: {reference}")
        if not image.is_file():
            raise FileNotFoundError(f"Missing image referenced in {source.name}: {reference} (expected {image})")
        images.add(image.relative_to(project).as_posix())
    return sorted(images)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Build without waiting for a chapter render")
    parser.add_argument("--chapter", choices=CHAPTER_ASSETS, help="Build only this chapter")
    args = parser.parse_args()
    chapters = [args.chapter] if args.chapter else list(CHAPTER_ASSETS)
    outputs = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").splitlines()
    if not args.force and not args.chapter:
        rendered = {Path(output).stem for output in outputs}
        chapters = [chapter for chapter in chapters if chapter in rendered]
    if not chapters:
        return
    quarto = shutil.which("quarto")
    if quarto is None:
        raise RuntimeError("Quarto must be on PATH to build the chapter's slide view")
    # Resolve the textbook root independently of the caller's working directory.
    project = Path(__file__).resolve().parents[1]
    output_dir = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_book"))
    if not output_dir.is_absolute():
        output_dir = project / output_dir
    for chapter in chapters:
        build_chapter(quarto, project, output_dir, chapter)


def build_chapter(quarto, project, output_dir, chapter):
    print(f"Building slide view: {chapter}…", flush=True)
    # Keep this outside the book project: preview can discover render requests
    # in child directories and otherwise treat the deck as a chapter rebuild.
    with TemporaryDirectory(prefix="viz-oer-chapter-slides-") as directory:
        staging = Path(directory)
        shutil.copy2(project / "_chapter-slides.yml", staging / "_quarto.yml")
        images = discover_local_images(quarto, project, project / f"{chapter}.qmd")
        assets = dict.fromkeys((f"{chapter}.qmd", *SHARED_ASSETS, *CHAPTER_ASSETS[chapter], *images))
        for name in assets:
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if (project / name).is_dir():
                shutil.copytree(project / name, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(project / name, destination)
        # Make presentation-only cell options available before any chapter code
        # executes, without modifying the shared include used by the book.
        setup = staging / "_extensions/r-wasm/live/_knitr.qmd"
        setup.write_text(
            setup.read_text(encoding="utf-8") + "\n"
            + (project / "_slide-chunks.qmd").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        # Decks are standalone renders. Resolve chapter/figure references back
        # to the reading view rather than leaving unresolved book crossrefs.
        references = {}
        for stem in CHAPTER_ASSETS:
            source = (project / f"{stem}.qmd").read_text(encoding="utf-8")
            source = re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL)
            heading = re.search(r"^# (.+?)(?:\s+\{[^}]*\})?\s*$", source, re.MULTILINE)
            title = heading.group(1) if heading else stem
            identifiers = re.findall(r"\{[^}]*#((?:sec|fig|tbl)-[\w-]+)", source)
            identifiers += re.findall(r"^#\| label: ((?:fig|tbl)-[\w-]+)", source, re.MULTILINE)
            for identifier in identifiers:
                prefix = identifier.split("-", 1)[0]
                text = title if prefix == "sec" else f"{'Figure' if prefix == 'fig' else 'Table'} in {title}"
                references[identifier] = {"text": text, "url": f"../{stem}.html#{identifier}"}
        (staging / "slide-references.json").write_text(json.dumps(references), encoding="utf-8")
        # Do not carry the outer project's profile or bookkeeping into the
        # standalone render. R/Python environment activation is retained.
        env = {key: value for key, value in os.environ.items()
               if key != "QUARTO_PROFILE" and not key.startswith(
                   ("QUARTO_PROJECT_", "QUARTO_RENDER_", "QUARTO_PREVIEW_")
               )}
        subprocess.run(
            [quarto, "render", f"{chapter}.qmd", "--to", "revealjs"],
            cwd=staging, env=env, check=True,
        )
        shutil.copytree(staging / "_output", output_dir / "slides", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
