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
        self.song_visuals = 0
        self.song_videos = 0
        self.media_credits = 0
        self.song_media_sources: list[str] = []
        self.instrument_slides = 0
        self.instrument_media_sources: list[str] = []
        self.feature_pan_images = 0
        self.word_cloud_slides = 0
        self.word_cloud_terms = 0
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
        if "portal-story-instrument" in classes:
            self.instrument_slides += 1
        if "portal-story-word-cloud" in classes:
            self.word_cloud_slides += 1
        if "portal-story-cloud-activity" in classes or "portal-story-cloud-song" in classes:
            self.word_cloud_terms += 1
        if "portal-story-song-visual" in classes:
            self.song_visuals += 1
            self.song_media_sources.append(values.get("src", ""))
            if tag == "video":
                self.song_videos += 1
                assert "muted" in values, "Song videos must stay muted"
                assert "loop" in values, "Song videos must loop like lightweight GIFs"
                assert "playsinline" in values, "Song videos must play inline on mobile"
                assert values.get("poster"), "Song videos need a static poster"
        if "portal-story-media-credit" in classes:
            self.media_credits += 1
        if "portal-story-instrument-visual" in classes:
            self.instrument_media_sources.append(values.get("src", ""))
        if "portal-story-feature-pan" in classes:
            self.feature_pan_images += 1
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
    assert mobile.story_slides == 12, "Mobile Portal must render intro, four songs, three instruments, history, word cloud, join, and social stories"
    assert mobile.story_progress_segments == mobile.story_slides, "Every story needs a progress segment"
    assert mobile.song_visuals == 4, "Every song story needs a movie or MV visual"
    assert mobile.song_videos == 3, "Three song stories must use lightweight looping video"
    assert mobile.instrument_slides == 3, "The three harmonica types need one story each"
    assert len(mobile.instrument_media_sources) == 3, "Every harmonica story needs a real instrument photo"
    assert mobile.feature_pan_images == 1, "The revival photo must pan from left to right"
    assert mobile.word_cloud_slides == 1, "Activities and repertoire need one recruitment word-cloud story"
    assert mobile.word_cloud_terms == 66, "The word cloud must include all 27 activities and 39 songs"
    assert mobile.media_credits == 8, "Every song, instrument, and history visual needs a visible source credit"
    for source in mobile.song_media_sources:
        media = PUBLIC / source.split("?", 1)[0].lstrip("/")
        assert media.is_file() and media.stat().st_size > 1_000, f"Song visual is missing or empty: {source}"
    for source in mobile.instrument_media_sources:
        media = PUBLIC / source.split("?", 1)[0].lstrip("/")
        assert media.is_file() and media.stat().st_size > 1_000, f"Instrument photo is missing or empty: {source}"
    assert mobile.social_links == 4, "Social story must render all four official links"
    assert mobile.social_links_open_new_tab == 0, "Social links must work in embedded mobile browsers"
    assert screen.program_items == 4, "Projection screen must render all four songs"
    assert screen.qr_sources, "Projection screen is missing its fixed Portal QR Code"
    qr = PUBLIC / screen.qr_sources[0].split("?", 1)[0].lstrip("/")
    assert qr.is_file() and qr.stat().st_size > 500, "Portal QR asset is missing or empty"
    print("Portal output check passed.")


if __name__ == "__main__":
    main()
