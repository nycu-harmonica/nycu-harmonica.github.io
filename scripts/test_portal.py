#!/usr/bin/env python3
"""Smoke-test the built performance Portal and its fixed QR asset."""

from html.parser import HTMLParser
from pathlib import Path
import hashlib
import struct


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
        self.ensemble_slides = 0
        self.ensemble_videos = 0
        self.ensemble_media_sources: list[str] = []
        self.instrument_media_sources: list[str] = []
        self.feature_pan_images = 0
        self.keyword_story_slides = 0
        self.activity_terms = 0
        self.song_terms = 0
        self.keyword_terms_with_3d_position = 0
        self.keyword_terms_left = 0
        self.keyword_terms_right = 0
        self.faq_slides = 0
        self.end_story_images = 0
        self.end_story_image_sources: list[str] = []
        self.product_links: list[dict[str, str | None]] = []
        self.social_links = 0
        self.social_links_open_new_tab = 0
        self.has_story_player = False
        self.qr_sources: list[str] = []
        self._inside_story_progress = 0
        self._inside_link_list = 0
        self.story_titles: list[str] = []
        self.story_descriptions: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if values.get("data-program-item"):
            self.program_items += 1
        if "data-story-player" in values:
            self.has_story_player = True
        classes = (values.get("class") or "").split()
        if "portal-story-slide" in classes:
            self.story_slides += 1
            self.story_titles.append(values.get("data-story-title", ""))
            self.story_descriptions.append(values.get("data-story-description", ""))
        if "portal-story-ensemble" in classes:
            self.ensemble_slides += 1
        if "portal-story-ensemble-visual" in classes:
            self.ensemble_videos += 1
            self.ensemble_media_sources.append(values.get("src", ""))
            assert tag == "video", "The ensemble visual must be a video"
            assert "muted" in values, "The ensemble video must stay muted"
            assert "loop" in values, "The ensemble video must loop like a lightweight GIF"
            assert "playsinline" in values, "The ensemble video must play inline on mobile"
            assert values.get("poster"), "The ensemble video needs a static poster"
        if "portal-story-instrument" in classes:
            self.instrument_slides += 1
        if "portal-story-keywords" in classes:
            self.keyword_story_slides += 1
        if "portal-story-faq" in classes:
            self.faq_slides += 1
        if "portal-story-end-visual" in classes:
            self.end_story_images += 1
            self.end_story_image_sources.append(values.get("src", ""))
        if tag == "a" and values.get("href", "").startswith(("https://harmonica.tw/", "https://shopee.tw/", "https://dming.co/")):
            self.product_links.append(values)
        if "portal-story-keyword-term-activity" in classes:
            self.activity_terms += 1
        if "portal-story-keyword-term-song" in classes:
            self.song_terms += 1
        if "portal-story-keyword-term" in classes:
            style = values.get("style", "")
            if "--keyword-x:" in style and "--keyword-y:" in style:
                self.keyword_terms_with_3d_position += 1
        if "portal-story-keyword-side-left" in classes:
            self.keyword_terms_left += 1
        if "portal-story-keyword-side-right" in classes:
            self.keyword_terms_right += 1
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


def webp_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    marker = data.find(b"\x9d\x01\x2a")
    assert marker >= 0 and len(data) >= marker + 7, f"Cannot read WebP dimensions: {path}"
    width, height = struct.unpack_from("<HH", data, marker + 3)
    return width & 0x3FFF, height & 0x3FFF


def main() -> None:
    mobile = parse("p/index.html")
    screen = parse("p/screen/index.html")
    mobile_html = (PUBLIC / "p" / "index.html").read_text(encoding="utf-8")
    assert mobile.has_story_player, "Mobile Portal is missing its story player"
    assert mobile.story_slides == 17, "Mobile Portal must render intro, four songs, ensemble intro, three instruments, history, two keyword stories, three FAQs, join, and social stories"
    assert mobile.story_progress_segments == mobile.story_slides, "Every story needs a progress segment"
    assert mobile.song_visuals == 4, "Every song story needs a movie or MV visual"
    assert mobile.song_videos == 3, "Three song stories must use lightweight looping video"
    assert mobile.instrument_slides == 3, "The three harmonica types need one story each"
    assert mobile.ensemble_slides == 1, "Harmonica ensemble needs an introduction before the instrument stories"
    assert mobile.ensemble_videos == 1, "The ensemble introduction needs a matching performance video"
    assert mobile.story_titles.index("口琴重奏") < mobile.story_titles.index("半音階口琴"), "Ensemble introduction must precede instrument details"
    assert "portal-story-ensemble-stats" not in mobile_html, "The ensemble story must not show the removed 4/3/1 statistics"
    assert len(mobile.instrument_media_sources) == 3, "Every harmonica story needs a real instrument photo"
    assert mobile.feature_pan_images == 1, "The revival photo must pan from left to right"
    assert mobile.keyword_story_slides == 2, "Activities and repertoire need separate keyword stories"
    assert mobile.activity_terms == 27, "The activity story must include all 27 activities"
    assert mobile.song_terms == 39, "The song story must include all 39 repertoire ideas"
    assert mobile.keyword_terms_with_3d_position == 66, "Every keyword needs a deterministic 3D flight path"
    assert mobile.keyword_terms_left == mobile.keyword_terms_right == 33, "Keyword paths must be evenly balanced between the left and right sides"
    assert mobile.faq_slides == 3, "The join CTA must be preceded by three FAQ stories"
    assert mobile.end_story_images == 4, "Stories 14–17 must each have a real background image"
    end_story_hashes: set[str] = set()
    for source in mobile.end_story_image_sources:
        media = PUBLIC / source.lstrip("/")
        assert media.is_file() and media.stat().st_size > 15_000, f"End-story image must be a high-resolution local asset: {source}"
        end_story_hashes.add(hashlib.sha256(media.read_bytes()).hexdigest())
        width, height = webp_dimensions(media)
        assert width >= 540 and height >= 960, f"End-story image is too small: {source} ({width}x{height})"
        assert abs(width / height - 9 / 16) < 0.002, f"End-story image must be portrait 9:16: {source} ({width}x{height})"
    assert len(end_story_hashes) == len(mobile.end_story_image_sources), "Stories 14–17 must not reuse the same image"
    assert mobile.story_titles.index("沒有口琴，要先買嗎？") < mobile.story_titles.index("下一段旋律，換你加入"), "FAQ stories must precede the join CTA"
    assert mobile.media_credits == 9, "Every song, ensemble, instrument, and history visual needs a visible source credit"
    for source in mobile.song_media_sources:
        media = PUBLIC / source.split("?", 1)[0].lstrip("/")
        assert media.is_file() and media.stat().st_size > 1_000, f"Song visual is missing or empty: {source}"
    for source in mobile.instrument_media_sources:
        media = PUBLIC / source.split("?", 1)[0].lstrip("/")
        assert media.is_file() and media.stat().st_size > 1_000, f"Instrument photo is missing or empty: {source}"
    for source in mobile.ensemble_media_sources:
        media = PUBLIC / source.split("?", 1)[0].lstrip("/")
        assert media.is_file() and media.stat().st_size > 1_000, f"Ensemble video is missing or empty: {source}"
    assert mobile.social_links == 4, "Social story must render all four official links"
    assert mobile.social_links_open_new_tab == 0, "Social links must work in embedded mobile browsers"
    assert len(mobile.product_links) == 3, "FAQ must link all three reference chromatic harmonicas"
    assert all(link.get("target") == "_blank" for link in mobile.product_links), "Product prices must open in a new tab"
    assert all({"noopener", "noreferrer"}.issubset(set((link.get("rel") or "").split())) for link in mobile.product_links), "New-tab product links must be isolated from the Portal"
    assert all(price in mobile_html for price in ("2,500 元", "4,200 元", "7,000 元")), "FAQ must show all three requested reference prices"
    assert all(store in mobile_html for store in ("黃石樂器", "音和樂器", "DMing Studio")), "Product links must be labelled with the three shops"
    assert all(model in mobile_html for model in ("JDR GM-0648", "JDR EVO-0648S", "Suzuki SCX-64")), "Product links must retain each harmonica model"
    assert "join-form-portrait.webp" not in mobile_html, "Join story must not reuse the form header group photo"
    assert "activity-center-portrait.webp" not in mobile_html, "Lesson-location FAQ must not reuse the revival group photo"
    assert "activity-center-map-portrait.webp" in mobile_html, "Lesson-location FAQ must show the unique activity-center map"
    assert "送你一個小口琴吊飾" in mobile_html, "Join story must describe the actual harmonica charm gift"
    join_description = mobile.story_descriptions[mobile.story_titles.index("下一段旋律，換你加入")]
    assert "500 元" not in join_description and "1,000 元" not in join_description, "Join story must leave numeric pricing to the fee FAQ"
    assert mobile_html.index("一學期社費 500 元") < mobile_html.index("送你一個小口琴吊飾"), "Fee information must appear before the gift information"
    assert "和弦口琴、倍低音口琴，社團都有新買的社團用琴" in mobile_html, "FAQ must explain which ensemble instruments the club provides"
    assert "開學後每週二晚上，在學生活動中心 1 樓聯誼廳" in mobile_html, "FAQ must show the regular lesson time and location"
    assert "送你一支口琴" not in mobile_html, "Join story must not claim that new members receive an instrument"
    assert screen.program_items == 4, "Projection screen must render all four songs"
    assert screen.qr_sources, "Projection screen is missing its fixed Portal QR Code"
    qr = PUBLIC / screen.qr_sources[0].split("?", 1)[0].lstrip("/")
    assert qr.is_file() and qr.stat().st_size > 500, "Portal QR asset is missing or empty"
    portal_js = (ROOT / "assets" / "js" / "portal.js").read_text(encoding="utf-8")
    assert "navigator.share" not in portal_js, "Share must copy the current story URL directly"
    assert "navigator.clipboard?.writeText" in portal_js, "Share needs a direct clipboard path"
    print("Portal output check passed.")


if __name__ == "__main__":
    main()
