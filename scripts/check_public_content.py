#!/usr/bin/env python3
"""Reject officer-only fields and secret-shaped values in published site data."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_HEADERS = {
    "dept_year",
    "discord",
    "drive_folder_id",
    "email",
    "oauth",
    "owner",
    "owner_mention",
    "token",
}
FORBIDDEN_PATTERNS = {
    "Discord mention": re.compile(r"<@!?\d+>"),
    "private/shared path": re.compile(r"(?:^|[(/'\"`])(?:private|shared)/"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]+"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]+"),
}


def public_text_files() -> list[Path]:
    roots = [ROOT / "static" / "data", ROOT / "data" / "generated", ROOT / "content"]
    return sorted(
        path
        for base in roots
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in {".csv", ".json", ".md"}
    )


def main() -> int:
    errors: list[str] = []

    for path in sorted((ROOT / "static" / "data").glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            headers = {header.strip().lower() for header in (next(csv.reader(handle), []))}
        forbidden = sorted(headers & FORBIDDEN_HEADERS)
        if forbidden:
            errors.append(f"{path.relative_to(ROOT)}: forbidden public columns {forbidden}")

    for path in sorted((ROOT / "data" / "generated").glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        stack = [value]
        found_keys = set()
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                found_keys.update(str(key).lower() for key in current)
                stack.extend(current.values())
            elif isinstance(current, list):
                stack.extend(current)
        forbidden = sorted(found_keys & FORBIDDEN_HEADERS)
        if forbidden:
            errors.append(f"{path.relative_to(ROOT)}: forbidden public keys {forbidden}")

    for path in public_text_files():
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)}: contains {label}")

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    print(f"Public content check passed ({len(public_text_files())} files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
