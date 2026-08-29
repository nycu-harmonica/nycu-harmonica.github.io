#!/usr/bin/env python3
"""Validate built RSS, sitemap, robots, and canonical discovery outputs."""

from __future__ import annotations

import csv
import email.utils
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import subprocess
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"


class SEOParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.h1_parts: list[list[str]] = []
        self.json_ld_parts: list[list[str]] = []
        self._inside_title = False
        self._h1_depth = 0
        self._json_ld_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self._inside_title = True
        elif tag == "h1":
            self._h1_depth += 1
            self.h1_parts.append([])
        elif tag == "meta":
            key = values.get("name") or values.get("property")
            if key and values.get("content") is not None:
                self.meta[key.lower()] = values["content"] or ""
        elif tag == "link" and "canonical" in (values.get("rel") or "").split():
            if values.get("href"):
                self.canonicals.append(values["href"] or "")
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._json_ld_depth += 1
            self.json_ld_parts.append([])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._inside_title = False
        elif tag == "h1" and self._h1_depth:
            self._h1_depth -= 1
        elif tag == "script" and self._json_ld_depth:
            self._json_ld_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self.title_parts.append(data)
        if self._h1_depth and self.h1_parts:
            self.h1_parts[-1].append(data)
        if self._json_ld_depth and self.json_ld_parts:
            self.json_ld_parts[-1].append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def h1s(self) -> list[str]:
        return [" ".join("".join(parts).split()) for parts in self.h1_parts]

    @property
    def json_ld(self) -> list[dict]:
        return [json.loads("".join(parts)) for parts in self.json_ld_parts]


def seo_from_html(path: Path) -> SEOParser:
    parser = SEOParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def canonical_from_html(path: Path) -> str:
    parser = seo_from_html(path)
    assert len(parser.canonicals) == 1, (
        f"Expected one canonical URL in {path.relative_to(PUBLIC)}, got {parser.canonicals}"
    )
    return parser.canonicals[0]


BASE_URL = canonical_from_html(PUBLIC / "index.html")
assert BASE_URL.endswith("/"), f"Home canonical URL must end with /: {BASE_URL}"
RSS_METADATA = {
    "index.xml": ("陽明交大竹韻口琴社網站更新", "竹韻口琴社網站更新"),
}
RETIRED_OUTPUTS = {
    "announcements/index.html",
    "announcements/index.xml",
    "announcements/2026-06-26-club-revival/index.html",
    "announcements/2026-07-15-site-launch/index.html",
    "events/index.html",
    "events/index.xml",
    "gallery/index.html",
    "gallery/index.xml",
}
RETIRED_PATHS = ("/announcements/", "/events/", "/gallery/")


def parse_xml(relative_path: str) -> ET.Element:
    path = PUBLIC / relative_path
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise AssertionError(f"Invalid XML: {relative_path}: {exc}") from exc


def require_official_url(url: str | None, source: str) -> str:
    assert url, f"Missing URL in {source}"
    assert url.startswith(BASE_URL), f"Non-canonical URL in {source}: {url}"
    return url


def require_html_description(description: str, source: str) -> None:
    assert description.strip(), f"RSS item has an empty description: {source}"
    try:
        fragment = ET.fromstring(f"<root>{description}</root>")
    except ET.ParseError as exc:
        raise AssertionError(f"RSS item description is invalid HTML: {source}: {exc}") from exc
    assert any(isinstance(element.tag, str) for element in fragment), (
        f"RSS item description has no HTML element and may be double-escaped: {source}"
    )


def check_rss(relative_path: str) -> None:
    root = parse_xml(relative_path)
    channel = root.find("channel")
    assert root.tag == "rss" and channel is not None, f"Invalid RSS structure: {relative_path}"
    require_official_url(channel.findtext("link"), relative_path)
    atom_link = channel.find("{http://www.w3.org/2005/Atom}link")
    atom_href = require_official_url(
        atom_link.get("href") if atom_link is not None else None, relative_path
    )
    assert atom_link is not None
    assert atom_link.get("rel") == "self", f"RSS Atom link must use rel=self: {relative_path}"
    assert atom_link.get("type") == "application/rss+xml", (
        f"RSS Atom link has an invalid media type: {relative_path}"
    )
    assert atom_href == f"{BASE_URL}{relative_path}", (
        f"RSS self URL mismatch in {relative_path}: {atom_href}"
    )
    expected_title, expected_description = RSS_METADATA[relative_path]
    assert channel.findtext("title") == expected_title, f"RSS title is inaccurate: {relative_path}"
    assert channel.findtext("description") == expected_description, (
        f"RSS description is inaccurate: {relative_path}"
    )
    items = channel.findall("item")
    if not items:
        assert relative_path == "index.xml", f"RSS has no items: {relative_path}"
        return

    urls: list[str] = []
    for item in items:
        url = require_official_url(item.findtext("link"), relative_path)
        assert item.findtext("guid") == url, f"RSS guid/link mismatch: {url}"
        published = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
        assert published.year > 1, f"RSS contains an invalid publication date: {url}"
        require_html_description(item.findtext("description") or "", url)
        urls.append(url)
    assert len(urls) == len(set(urls)), f"RSS contains duplicate items: {relative_path}"
    if relative_path == "index.xml":
        assert all("/gallery/" not in url for url in urls), "Home RSS must not contain retired gallery URLs"


def check_retired_routes() -> None:
    for relative_path in RETIRED_OUTPUTS:
        assert not (PUBLIC / relative_path).exists(), f"Retired route was built: {relative_path}"
    for html_path in PUBLIC.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        for retired_path in RETIRED_PATHS:
            assert retired_path not in text, (
                f"Internal link points to retired route {retired_path}: {html_path.relative_to(PUBLIC)}"
            )


def published_pages() -> dict[str, tuple[Path, SEOParser]]:
    pages: dict[str, tuple[Path, SEOParser]] = {}
    output = subprocess.check_output(
        ["hugo", "list", "published"], cwd=ROOT, text=True, encoding="utf-8"
    )
    for row in csv.DictReader(io.StringIO(output)):
        url = require_official_url(row["permalink"], row["path"])
        relative = url[len(BASE_URL) :].strip("/")
        html_path = PUBLIC / relative / "index.html" if relative else PUBLIC / "index.html"
        assert html_path.is_file(), f"Missing built HTML page: {html_path.relative_to(PUBLIC)}"
        parser = seo_from_html(html_path)
        assert len(parser.canonicals) == 1, f"Expected one canonical URL: {html_path.relative_to(PUBLIC)}"
        canonical = parser.canonicals[0]
        assert canonical == url, f"Canonical mismatch: {html_path.relative_to(PUBLIC)}"
        parts = urlsplit(canonical)
        assert not parts.query and not parts.fragment, f"Canonical must omit query and fragment: {canonical}"
        pages[url] = (html_path, parser)
    assert pages, "No published HTML pages found"
    return pages


def check_page_metadata(pages: dict[str, tuple[Path, SEOParser]]) -> None:
    titles: dict[str, str] = {}
    headings: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    for url, (path, parser) in pages.items():
        source = str(path.relative_to(PUBLIC))
        assert parser.title, f"Missing title: {source}"
        assert len(parser.h1s) == 1 and parser.h1s[0], f"Expected one non-empty H1: {source}"
        description = parser.meta.get("description", "").strip()
        assert description, f"Missing meta description: {source}"
        assert parser.title != parser.h1s[0], f"Title and H1 must be distinct: {source}"
        assert parser.meta.get("og:title") == parser.title, f"Open Graph title mismatch: {source}"
        assert parser.meta.get("og:description") == description, f"Open Graph description mismatch: {source}"
        assert parser.meta.get("twitter:title") == parser.title, f"Twitter title mismatch: {source}"
        assert parser.meta.get("twitter:description") == description, f"Twitter description mismatch: {source}"
        assert parser.meta.get("og:url") == url, f"Open Graph URL mismatch: {source}"
        assert parser.meta.get("og:image", "").startswith(BASE_URL), f"Missing official preview image: {source}"

        for value, seen, label in (
            (parser.title, titles, "title"),
            (parser.h1s[0], headings, "H1"),
            (description, descriptions, "description"),
        ):
            assert value not in seen, f"Duplicate {label} in {source} and {seen.get(value)}: {value}"
            seen[value] = source


def check_home_structured_data(pages: dict[str, tuple[Path, SEOParser]]) -> None:
    _, home = pages[BASE_URL]
    assert len(home.json_ld) == 1, "Homepage must contain one JSON-LD graph"
    graph = home.json_ld[0]
    assert graph.get("@context") == "https://schema.org", "Homepage JSON-LD context is incorrect"
    by_type = {item.get("@type"): item for item in graph.get("@graph", [])}
    organization = by_type.get("Organization")
    website = by_type.get("WebSite")
    assert organization and website, "Homepage JSON-LD must contain Organization and WebSite"
    assert organization.get("name") == "國立陽明交通大學竹韻口琴社"
    assert organization.get("alternateName") == [
        "陽明交大竹韻口琴社",
        "交大口琴社",
        "Bamboo Melody Harmonica Club",
    ]
    assert organization.get("url") == BASE_URL
    assert organization.get("email") == "bmhc1968@gmail.com"
    assert organization.get("logo", {}).get("url") == f"{BASE_URL}images/bamboo-logo.webp"
    assert organization.get("sameAs") == [
        "https://www.instagram.com/nycu_harmonica/",
        "https://www.facebook.com/nycubmhc/",
        "https://www.youtube.com/channel/UClIoDAYl9-jVnBpC4nFtHGw",
    ]
    assert website.get("publisher", {}).get("@id") == organization.get("@id")


def check_sitemap(pages: dict[str, tuple[Path, SEOParser]]) -> None:
    root = parse_xml("sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = root.findall("sm:url", namespace)
    urls = [require_official_url(entry.findtext("sm:loc", namespaces=namespace), "sitemap.xml") for entry in entries]
    assert len(urls) == len(set(urls)), "Sitemap contains duplicate URLs"
    indexable = {
        url
        for url, (_, parser) in pages.items()
        if "noindex" not in parser.meta.get("robots", "").lower().replace(" ", "").split(",")
    }
    assert set(urls) == indexable, "Sitemap URLs do not match indexable canonical HTML pages"
    assert f"{BASE_URL}join/" not in urls, "/join/ is noindex and must not appear in sitemap"
    for entry in entries:
        lastmod = entry.findtext("sm:lastmod", namespaces=namespace)
        assert not lastmod or not lastmod.startswith("0001-"), "Sitemap contains an invalid lastmod"


def check_robots() -> None:
    lines = {line.strip() for line in (PUBLIC / "robots.txt").read_text(encoding="utf-8").splitlines()}
    assert "User-agent: *" in lines, "robots.txt is missing User-agent: *"
    assert f"Sitemap: {BASE_URL}sitemap.xml" in lines, "robots.txt is missing the canonical sitemap URL"


def main() -> None:
    check_retired_routes()
    for relative_path in RSS_METADATA:
        check_rss(relative_path)
    pages = published_pages()
    check_page_metadata(pages)
    check_home_structured_data(pages)
    check_sitemap(pages)
    check_robots()
    print("SEO output check passed.")


if __name__ == "__main__":
    main()
