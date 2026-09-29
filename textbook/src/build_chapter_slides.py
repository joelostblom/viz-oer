"""Quarto post-render hook: keep chapter 1's slide view up to date.

Invoked after book renders, including preview rebuilds. Slide rendering runs in
an isolated temporary project so it cannot change the book's preview-format
cache. Only the completed deck and its assets are copied into the book output.
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Build without waiting for a chapter render")
    args = parser.parse_args()
    chapter = "1_why-visualize-data"
    outputs = os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").splitlines()
    if not args.force and not any(Path(output).name == f"{chapter}.html" for output in outputs):
        return
    quarto = shutil.which("quarto")
    if quarto is None:
        raise RuntimeError("Quarto must be on PATH to build the chapter's slide view")
    # Resolve the textbook root independently of the caller's working directory.
    project = Path(__file__).resolve().parents[1]
    output_dir = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_book"))
    if not output_dir.is_absolute():
        output_dir = project / output_dir
    print("Building chapter 1 slide view…", flush=True)
    # Keep this outside the book project: preview can discover render requests
    # in child directories and otherwise treat the deck as a chapter rebuild.
    with TemporaryDirectory(prefix="viz-oer-chapter-slides-") as directory:
        staging = Path(directory)
        shutil.copy2(project / "_chapter-slides.yml", staging / "_quarto.yml")
        for name in (
            f"{chapter}.qmd", "chapter-slides.lua", "chapter-slides.css", "chapter-slides.js",
            "_extensions/r-wasm/live/_knitr.qmd", "img/DinoSequentialSmaller.gif",
        ):
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(project / name, destination)
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
