#!/usr/bin/env python3
"""Reject half-width punctuation in visible Chinese production HTML text."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
CJK = "\\u3400-\\u4dbf\\u4e00-\\u9fff\\uf900-\\ufaff"
CJK_LEFT_CONTEXT = CJK + "）】」』》〉"
CJK_RIGHT_CONTEXT = CJK + "（【「『《〈"
HALF_WIDTH = re.compile(
    rf"(?<=[{CJK_LEFT_CONTEXT}])[,;:!?|~]|[,;:!?|~](?=[{CJK_RIGHT_CONTEXT}])|"
    rf"(?<=[{CJK}])\([^()\n]*\)|\([^()\n]*[{CJK}][^()\n]*\)|\([^()\n]*\)(?=[{CJK}])"
)
IGNORED_TAGS = {"script", "style", "code", "pre", "svg"}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ignored_depth = 0
        self.issues: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in IGNORED_TAGS:
            self.ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in IGNORED_TAGS and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.ignored_depth or not HALF_WIDTH.search(data):
            return
        text = " ".join(data.split())
        self.issues.append((self.getpos()[0], text[:120]))


def sitemap_html_paths() -> list[Path]:
    root = ET.parse(PUBLIC / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    paths = []
    for location in root.findall("sm:url/sm:loc", namespace):
        relative = urlparse(location.text or "").path.strip("/")
        paths.append(PUBLIC / relative / "index.html" if relative else PUBLIC / "index.html")
    return paths


def main() -> int:
    failures = []
    for path in sitemap_html_paths():
        parser = VisibleTextParser()
        parser.feed(path.read_text(encoding="utf-8"))
        failures.extend((path.relative_to(PUBLIC), line, text) for line, text in parser.issues)
    for path, line, text in failures:
        print(f"{path}:{line}: half-width punctuation in Chinese text: {text}")
    if failures:
        return 1
    print("Typography check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
