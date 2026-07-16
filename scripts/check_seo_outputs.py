#!/usr/bin/env python3
"""Validate built RSS, sitemap, robots, and canonical discovery outputs."""

from __future__ import annotations

import csv
import email.utils
from html.parser import HTMLParser
import io
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"


class CanonicalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "link":
            return
        values = dict(attrs)
        if "canonical" in (values.get("rel") or "").split():
            self.canonical = values.get("href")


def canonical_from_html(path: Path) -> str:
    parser = CanonicalParser()
    parser.feed(path.read_text(encoding="utf-8"))
    assert parser.canonical, f"Missing canonical URL: {path.relative_to(PUBLIC)}"
    return parser.canonical


BASE_URL = canonical_from_html(PUBLIC / "index.html")
assert BASE_URL.endswith("/"), f"Home canonical URL must end with /: {BASE_URL}"


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


def check_rss(relative_path: str) -> None:
    root = parse_xml(relative_path)
    channel = root.find("channel")
    assert root.tag == "rss" and channel is not None, f"Invalid RSS structure: {relative_path}"
    require_official_url(channel.findtext("link"), relative_path)
    atom_link = channel.find("{http://www.w3.org/2005/Atom}link")
    require_official_url(atom_link.get("href") if atom_link is not None else None, relative_path)
    if relative_path == "index.xml":
        assert (channel.findtext("title") or "").endswith("公開內容"), "Home RSS title is inaccurate"
        assert channel.findtext("description") == "竹韻口琴社公告與相簿更新", "Home RSS description is inaccurate"
    items = channel.findall("item")
    assert items, f"RSS has no items: {relative_path}"

    urls: list[str] = []
    for item in items:
        url = require_official_url(item.findtext("link"), relative_path)
        assert item.findtext("guid") == url, f"RSS guid/link mismatch: {url}"
        published = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
        assert published.year > 1, f"RSS contains an invalid publication date: {url}"
        urls.append(url)
    assert len(urls) == len(set(urls)), f"RSS contains duplicate items: {relative_path}"


def published_urls() -> set[str]:
    urls: set[str] = set()
    output = subprocess.check_output(
        ["hugo", "list", "published"], cwd=ROOT, text=True, encoding="utf-8"
    )
    for row in csv.DictReader(io.StringIO(output)):
        url = require_official_url(row["permalink"], row["path"])
        relative = url[len(BASE_URL) :].strip("/")
        html_path = PUBLIC / relative / "index.html" if relative else PUBLIC / "index.html"
        assert html_path.is_file(), f"Missing built HTML page: {html_path.relative_to(PUBLIC)}"
        assert canonical_from_html(html_path) == url, f"Canonical mismatch: {html_path.relative_to(PUBLIC)}"
        urls.add(url)
    assert urls, "No published HTML pages found"
    return urls


def check_sitemap() -> None:
    root = parse_xml("sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = root.findall("sm:url", namespace)
    urls = [require_official_url(entry.findtext("sm:loc", namespaces=namespace), "sitemap.xml") for entry in entries]
    assert len(urls) == len(set(urls)), "Sitemap contains duplicate URLs"
    assert set(urls) == published_urls(), "Sitemap URLs do not match published canonical HTML pages"
    for entry in entries:
        lastmod = entry.findtext("sm:lastmod", namespaces=namespace)
        assert not lastmod or not lastmod.startswith("0001-"), "Sitemap contains an invalid lastmod"


def check_robots() -> None:
    lines = {line.strip() for line in (PUBLIC / "robots.txt").read_text(encoding="utf-8").splitlines()}
    assert "User-agent: *" in lines, "robots.txt is missing User-agent: *"
    assert f"Sitemap: {BASE_URL}sitemap.xml" in lines, "robots.txt is missing the canonical sitemap URL"


def main() -> None:
    check_rss("index.xml")
    check_rss("announcements/index.xml")
    check_sitemap()
    check_robots()
    print("SEO output check passed.")


if __name__ == "__main__":
    main()
