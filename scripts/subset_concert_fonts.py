#!/usr/bin/env python3
"""Regenerate the /1151/ concert font subsets from data/concert1151.yaml.

Each subset keeps every character it already has and adds whatever the data
file now needs, so running it again never drops a glyph a template uses.

Source fonts (SIL OFL 1.1), download once:
  NotoSerifTC-Bold.otf / NotoSerifTC-Black.otf
    https://github.com/notofonts/noto-cjk/raw/main/Serif/SubsetOTF/TC/

Usage:
  uv run --with fonttools --with brotli --with pyyaml \\
    python scripts/subset_concert_fonts.py --sources /path/to/font/dir
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "static" / "fonts" / "1151"
DATA = ROOT / "data" / "concert1151.yaml"

# Headings written directly in layouts/concert/single.html that use the serif.
TEMPLATE_SERIF = "我們現場見製作名單演出人員各場工作人員第一二三場贊助單位"


def collect(data: dict) -> dict[str, str]:
    events = data["events"]
    credits = data.get("credits", {})

    serif = TEMPLATE_SERIF + "".join(data.get("kicker", []))
    serif += "".join(h["name"] + h["full"] for h in data["hosts"])
    serif += "".join(e["title"] + e["act"] for e in events)
    for group in credits.get("groups", []):
        serif += group["title"] + "".join(p["name"] for p in group["people"])
    officers = credits.get("officers", {})
    serif += officers.get("title", "")
    serif += "".join(c["name"] + "".join(p["name"] for p in c["people"]) for c in officers.get("clubs", []))
    serif += credits.get("members", {}).get("title", "")
    serif += credits.get("production", {}).get("title", "")
    serif += credits.get("thanks", {}).get("title", "") + "".join(credits.get("thanks", {}).get("orgs", []))
    serif += "".join(s["name"] for s in data.get("sponsors", []))

    return {
        "concert-title.woff2": data["title"] + "#" + data.get("hashtag", ""),
        "concert-serif.woff2": serif,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sources", type=Path, required=True, help="directory holding the source fonts")
    args = parser.parse_args()

    sources = {
        "concert-title.woff2": args.sources / "NotoSerifTC-Black.otf",
        "concert-serif.woff2": args.sources / "NotoSerifTC-Bold.otf",
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
