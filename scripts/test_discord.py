#!/usr/bin/env python3
"""Smoke-test the built Discord invitation landing page."""

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "public" / "discord" / "index.html"


class DiscordParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_card = False
        self.api_url = ""
        self.join_urls: list[str] = []
        self.has_online = False
        self.has_members = False
        self.has_copy = False

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if "data-discord-card" in values:
            self.has_card = True
            self.api_url = values.get("data-api-url", "")
        if tag == "a" and "data-discord-join" in values:
            self.join_urls.append(values.get("href", ""))
        self.has_online |= "data-discord-online" in values
        self.has_members |= "data-discord-members" in values
        self.has_copy |= "data-copy-invite" in values


def main() -> None:
    assert OUTPUT.is_file(), "Missing /discord/ output"
    html = OUTPUT.read_text(encoding="utf-8")
    parser = DiscordParser()
    parser.feed(html)

    assert parser.has_card, "Discord invitation card is missing"
    assert parser.api_url.startswith("https://discord.com/api/v10/invites/"), "Discord live API is missing"
    assert parser.join_urls == ["https://discord.gg/uEQDCbnY8P"], "Discord invite must use the approved permanent URL"
    assert parser.has_online and parser.has_members, "Discord live counters are missing"
    assert parser.has_copy, "Discord invite copy action is missing"
    assert "data-discord-status" in html, "Discord live status message is missing"
    print("Discord invitation output check passed.")


if __name__ == "__main__":
    main()
