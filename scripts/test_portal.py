#!/usr/bin/env python3
"""Smoke-test the built performance Portal and its fixed QR asset."""

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"


class PortalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.program_items = 0
        self.story_slides = 0
        self.story_progress_segments = 0
        self.social_links = 0
        self.social_links_open_new_tab = 0
        self.has_story_player = False
        self.qr_sources: list[str] = []
        self._inside_story_progress = 0
        self._inside_link_list = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if values.get("data-program-item"):
            self.program_items += 1
        if "data-story-player" in values:
            self.has_story_player = True
        classes = (values.get("class") or "").split()
        if "portal-story-slide" in classes:
            self.story_slides += 1
        if "portal-story-progress" in classes:
            self._inside_story_progress += 1
        elif tag == "span" and self._inside_story_progress:
            self.story_progress_segments += 1
        if "portal-story-link-list" in classes:
            self._inside_link_list += 1
        elif tag == "a" and self._inside_link_list and values.get("href", "").startswith("http"):
            self.social_links += 1
            if values.get("target") == "_blank":
                self.social_links_open_new_tab += 1
        if tag == "img" and "portal-qr" in (values.get("src") or ""):
            self.qr_sources.append(values["src"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._inside_story_progress:
            self._inside_story_progress -= 1
        if tag == "nav" and self._inside_link_list:
            self._inside_link_list -= 1


def parse(relative_path: str) -> PortalParser:
    path = PUBLIC / relative_path
    assert path.is_file(), f"Missing Portal output: {relative_path}"
    parser = PortalParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def main() -> None:
    mobile = parse("p/index.html")
    screen = parse("p/screen/index.html")
    assert mobile.has_story_player, "Mobile Portal is missing its story player"
    assert mobile.story_slides == 9, "Mobile Portal must render intro, four songs, two features, join, and social stories"
    assert mobile.story_progress_segments == mobile.story_slides, "Every story needs a progress segment"
    assert mobile.social_links == 4, "Social story must render all four official links"
    assert mobile.social_links_open_new_tab == 0, "Social links must work in embedded mobile browsers"
    assert screen.program_items == 4, "Projection screen must render all four songs"
    assert screen.qr_sources, "Projection screen is missing its fixed Portal QR Code"
    qr = PUBLIC / screen.qr_sources[0].split("?", 1)[0].lstrip("/")
    assert qr.is_file() and qr.stat().st_size > 500, "Portal QR asset is missing or empty"
    print("Portal output check passed.")


if __name__ == "__main__":
    main()
