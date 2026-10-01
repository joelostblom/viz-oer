"""Quarto post-render hook: use sidebar titles for chapter cross-references.

Only link contents are replaced; the rest of the generated HTML is preserved.
Uses the Python standard library and runs for full builds and preview renders.
"""

from html import escape
from html.parser import HTMLParser
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit


class Links(HTMLParser):
    """Collect anchor text, chapter-title text, and their source positions."""

    def __init__(self, source):
        super().__init__()
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.links = []
        self.current = None
        self.title_depth = 0
        self.feed(source)

    def source_position(self):
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.current = {
                "href": attrs.get("href", ""),
                "classes": attrs.get("class", "").split(),
                "start": self.source_position() + len(self.get_starttag_text()),
                "text": [], "title": [],
            }
            self.title_depth = 0
        elif tag == "span" and self.current is not None:
            if self.title_depth or "chapter-title" in attrs.get("class", "").split():
                self.title_depth += 1

    def handle_data(self, text):
        if self.current is not None:
            self.current["text"].append(text)
            if self.title_depth:
                self.current["title"].append(text)

    def handle_endtag(self, tag):
        if tag == "span" and self.title_depth:
            self.title_depth -= 1
        if tag == "a" and self.current is not None:
            self.current["end"] = self.source_position()
            self.links.append(self.current)
            self.current = None
            self.title_depth = 0


def rewrite_chapter_links(source, page):
    links = Links(source).links

    def page_key(href):
        url = urlsplit(urljoin(page.resolve().as_uri(), href))
        return url._replace(query="", fragment="").geturl()

    titles = {
        page_key(link["href"]): " ".join("".join(link["title"]).split())
        for link in links if "sidebar-link" in link["classes"] and link["title"]
    }
    # Work backwards so replacements do not invalidate earlier source positions.
    for link in reversed(links):
        text = "".join(link["text"]).strip()
        if "quarto-xref" not in link["classes"] or not re.fullmatch(r"Chapter\s+\d+", text):
            continue
        title = titles.get(page_key(link["href"]))
        if title:
            source = source[:link["start"]] + escape(title, quote=False) + source[link["end"]:]
    return source


def main():
    project = Path(__file__).resolve().parents[1]
    for output in os.environ.get("QUARTO_PROJECT_OUTPUT_FILES", "").splitlines():
        page = project / output  # Absolute output paths also work with Path's / operator.
        if page.suffix != ".html":
            continue
        source = page.read_text(encoding="utf-8")
        updated = rewrite_chapter_links(source, page)
        if updated != source:
            page.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
