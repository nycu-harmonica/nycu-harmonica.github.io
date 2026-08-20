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
        self.qr_sources: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if values.get("data-program-item"):
            self.program_items += 1
        if tag == "img" and "portal-qr" in (values.get("src") or ""):
            self.qr_sources.append(values["src"])


def parse(relative_path: str) -> PortalParser:
    path = PUBLIC / relative_path
    assert path.is_file(), f"Missing Portal output: {relative_path}"
    parser = PortalParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def main() -> None:
    mobile = parse("p/index.html")
    screen = parse("p/screen/index.html")
    assert mobile.program_items == 4, "Mobile Portal must render all four songs"
    assert screen.program_items == 4, "Projection screen must render all four songs"
    assert screen.qr_sources, "Projection screen is missing its fixed Portal QR Code"
    qr = PUBLIC / screen.qr_sources[0].split("?", 1)[0].lstrip("/")
    assert qr.is_file() and qr.stat().st_size > 500, "Portal QR asset is missing or empty"
    print("Portal output check passed.")


if __name__ == "__main__":
    main()
