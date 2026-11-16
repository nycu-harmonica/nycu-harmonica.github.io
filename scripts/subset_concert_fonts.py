#!/usr/bin/env python3
"""Regenerate the /1151/ concert font subsets from data/concert1151.yaml.

Each subset keeps every character it already has and adds whatever the data
file now needs, so running it again never drops a glyph a template uses.

Source fonts (SIL OFL 1.1), download once:
  NotoSerifTC-Bold.otf / NotoSerifTC-Black.otf
    https://github.com/notofonts/noto-cjk/raw/main/Serif/SubsetOTF/TC/
  PottaOne-Regular.ttf
    https://github.com/google/fonts/raw/main/ofl/pottaone/PottaOne-Regular.ttf

Usage:
  uv run --with fonttools --with brotli --with pyyaml \\
    python scripts/subset_concert_fonts.py --sources /path/to/font/dir
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "static" / "fonts" / "1151"
DATA = ROOT / "data" / "concert1151.yaml"

# Headings written directly in layouts/concert/single.html that use the serif.
TEMPLATE_SERIF = "三場演出節目搶先看我們現場見製作名單參與社員各場工作人員第一二三場"


def event_dates(event: dict) -> str:
    d = date.fromisoformat(event["date"])
    return f"{d.month}/{d.day:02d}"


def collect(data: dict) -> dict[str, str]:
    events = data["events"]
    credits = data.get("credits", {})

    hand = "0123456789/:–-"
    for e in events:
        hand += event_dates(e) + e["title"] + e["start"] + e["end"] + e["location"]

    serif = TEMPLATE_SERIF + "".join(data.get("kicker", []))
    serif += "".join(h["name"] + h["full"] for h in data["hosts"])
    serif += "".join(e["title"] + e["act"] for e in events)
    for group in credits.get("groups", []):
        serif += group["title"] + "".join(p["name"] for p in group["people"])
    officers = credits.get("officers", {})
    serif += officers.get("title", "")
    serif += "".join(p["name"] for c in officers.get("clubs", []) for p in c["people"])
    serif += credits.get("members", {}).get("title", "")

    return {
        "concert-title.woff2": data["title"],
        "concert-serif.woff2": serif,
        "concert-hand.woff2": hand,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sources", type=Path, required=True, help="directory holding the source fonts")
    args = parser.parse_args()

    sources = {
        "concert-title.woff2": args.sources / "NotoSerifTC-Black.otf",
        "concert-serif.woff2": args.sources / "NotoSerifTC-Bold.otf",
        "concert-hand.woff2": args.sources / "PottaOne-Regular.ttf",
    }
    texts = collect(yaml.safe_load(DATA.read_text(encoding="utf-8")))

    for name, text in texts.items():
        out = FONT_DIR / name
        chars = {c for c in text if not c.isspace()}
        if out.exists():
            chars |= {chr(u) for u in TTFont(out).getBestCmap()}
        options = subset.Options()
        options.flavor = "woff2"
        font = subset.load_font(str(sources[name]), options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(text="".join(sorted(chars)))
        subsetter.subset(font)
        missing = sorted(c for c in chars if ord(c) not in font.getBestCmap())
        subset.save_font(font, str(out), options)
        note = f"; not in source: {''.join(missing)}" if missing else ""
        print(f"{name}: {len(chars)} chars, {out.stat().st_size // 1024} KB{note}")


if __name__ == "__main__":
    main()
