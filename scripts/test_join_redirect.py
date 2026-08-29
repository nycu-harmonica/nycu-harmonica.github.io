#!/usr/bin/env python3
"""Verify the generated /join/ page redirects to the official signup form."""

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
JOIN_PAGE = ROOT / "public" / "join" / "index.html"
TARGET = "https://forms.gle/Ri8PC9mMGS4WPEua8"


class JoinRedirectParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refresh: str | None = None
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta" and (values.get("http-equiv") or "").lower() == "refresh":
            self.refresh = values.get("content")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")


def main() -> None:
    assert JOIN_PAGE.is_file(), "Missing generated /join/ page"
    html = JOIN_PAGE.read_text(encoding="utf-8")
    parser = JoinRedirectParser()
    parser.feed(html)
    assert parser.refresh == f"0; url={TARGET}", "Meta refresh target is incorrect"
    assert TARGET in parser.links, "Missing manual signup-form fallback link"
    assert f"window.location.replace({TARGET!r})" in html or f'window.location.replace("{TARGET}")' in html, (
        "JavaScript redirect target is incorrect"
    )
    print("Join redirect check passed.")


if __name__ == "__main__":
    main()
