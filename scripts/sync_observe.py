#!/usr/bin/env python3
"""Manually refresh the last-good fallback from Harmonica Observe's source API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from sync_sheet import normalize_display_text


API_URL = "https://harmonica.observe.tw/api/source/198.json"
SOURCE_URL = "https://harmonica.observe.tw/source/198-bamboo-melody-harmonica-club/"
SOURCE_ID = 198
SOURCE_SLUG = "bamboo-melody-harmonica-club"
SOURCE_NAME = "陽明交大竹韻口琴社"
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_ITEMS = 3
MAX_TITLE_LENGTH = 140
TAIPEI = timezone(timedelta(hours=8))
ITEM_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class ObserveSyncError(Exception):
    """The remote payload is unavailable or unsafe to publish."""


def compact_text(value: object, *, max_length: int, truncate: bool = False) -> str:
    text = " ".join(str(value or "").split())
    if not text or any(char in text for char in "<>"):
        return ""
    text = normalize_display_text(text)
    if len(text) <= max_length:
        return text
    if not truncate:
        return ""
    return text[: max_length - 1].rstrip() + "…"


def valid_https_url(value: object) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or any(char.isspace() for char in url)
    ):
        return ""
    return url


def parse_timestamp(value: object, label: str) -> datetime:
    text = str(value or "").strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise ObserveSyncError(f"{label} 格式錯誤") from error
    if parsed.tzinfo is None:
        raise ObserveSyncError(f"{label} 缺少時區")
    return parsed


def expected_source() -> dict:
    return {
        "id": SOURCE_ID,
        "slug": SOURCE_SLUG,
        "name": SOURCE_NAME,
        "page_url": SOURCE_URL,
    }


def validate_source(value: object) -> dict:
    if not isinstance(value, dict):
        raise ObserveSyncError("API 缺少 source metadata")
    if (
        type(value.get("id")) is not int
        or value.get("id") != SOURCE_ID
        or value.get("slug") != SOURCE_SLUG
        or value.get("name") != SOURCE_NAME
        or value.get("pageUrl") != SOURCE_URL
    ):
        raise ObserveSyncError("API source metadata 不符合竹韻來源")
    return expected_source()


def normalize_item(row: object) -> dict[str, str] | None:
    if not isinstance(row, dict) or row.get("sourceName") != SOURCE_NAME:
        return None
    item_id = str(row.get("id") or "").strip()
    if not ITEM_ID_RE.fullmatch(item_id):
        return None
    title = compact_text(row.get("title"), max_length=MAX_TITLE_LENGTH, truncate=True)
    source = compact_text(row.get("sourceName"), max_length=80)
    platform = compact_text(row.get("platform"), max_length=40)
    link = valid_https_url(row.get("url"))
    try:
        published = parse_timestamp(row.get("publishedAt"), "publishedAt")
    except ObserveSyncError:
        return None
    if not all((title, source, platform, link)):
        return None
    return {
        "id": item_id,
        "title": title,
        "source": source,
        "platform": platform,
        "posted_at_local": published.astimezone(TAIPEI).strftime("%Y-%m-%d %H:%M"),
        "link": link,
    }


def snapshot_from_payload(payload: object, *, updated_at: datetime) -> dict:
    if not isinstance(payload, dict):
        raise ObserveSyncError("API 回應不是 JSON object")
    if type(payload.get("schemaVersion")) is not int or payload.get("schemaVersion") != 1:
        raise ObserveSyncError("API schemaVersion 不是 1")
    source = validate_source(payload.get("source"))
    source_generated_at = str(payload.get("generatedAt") or "").strip()
    parse_timestamp(source_generated_at, "generatedAt")
    rows = payload.get("items")
    if not isinstance(rows, list):
        raise ObserveSyncError("API 缺少 items")

    items: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_links: set[str] = set()
    for row in rows:
        item = normalize_item(row)
        if item is None or item["id"] in seen_ids or item["link"] in seen_links:
            continue
        items.append(item)
        seen_ids.add(item["id"])
        seen_links.add(item["link"])
        if len(items) == MAX_ITEMS:
            break
    if not items:
        raise ObserveSyncError("API 沒有符合公開條件的竹韻動態")
    return {
        "source_generated_at": source_generated_at,
        "updated_at": updated_at.astimezone(TAIPEI).replace(microsecond=0).isoformat(),
        "source_url": SOURCE_URL,
        "source": source,
        "items": items,
    }


def validate_existing_snapshot(value: object) -> bool:
    if not isinstance(value, dict) or value.get("source_url") != SOURCE_URL:
        return False
    if value.get("source") != expected_source():
        return False
    if not all(str(value.get(field) or "").strip() for field in ("source_generated_at", "updated_at")):
        return False
    try:
        parse_timestamp(value["source_generated_at"], "source_generated_at")
        parse_timestamp(value["updated_at"], "updated_at")
    except ObserveSyncError:
        return False
    items = value.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        return False
    seen_ids: set[str] = set()
    seen_links: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "id", "title", "source", "platform", "posted_at_local", "link"
        }:
            return False
        item_id = str(item.get("id") or "")
        link = str(item.get("link") or "")
        if item_id in seen_ids or link in seen_links:
            return False
        probe = {
            "id": item_id,
            "title": item.get("title"),
            "sourceName": item.get("source"),
            "platform": item.get("platform"),
            "publishedAt": str(item.get("posted_at_local") or "").replace(" ", "T") + ":00+08:00",
            "url": link,
        }
        if normalize_item(probe) != item:
            return False
        seen_ids.add(item_id)
        seen_links.add(link)
    return True


def load_existing_snapshot(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if validate_existing_snapshot(value) else None


def fetch_payload(url: str = API_URL, *, timeout: float = 15, opener=urllib.request.urlopen) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "nycu-harmonica-site-sync/1.0"})
    try:
        with opener(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if status < 200 or status >= 300:
                raise ObserveSyncError(f"API 回應 HTTP {status}")
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                raise ObserveSyncError("API 回應超過大小上限")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (TimeoutError, urllib.error.URLError, OSError) as error:
        raise ObserveSyncError(f"API 讀取失敗：{error}") from error
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ObserveSyncError("API 回應超過大小上限")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ObserveSyncError("API 回應不是有效 UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ObserveSyncError("API 回應不是 JSON object")
    return payload


def write_snapshot(path: Path, value: dict) -> bool:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def sync(path: Path, *, fetcher=fetch_payload, now: datetime | None = None) -> tuple[bool, str]:
    existing = load_existing_snapshot(path)
    try:
        snapshot = snapshot_from_payload(fetcher(), updated_at=now or datetime.now(TAIPEI))
    except ObserveSyncError as error:
        if existing is not None:
            return False, f"觀測站同步失敗，沿用 last-good 快照：{error}"
        raise
    if existing is not None and all(
        existing.get(field) == snapshot.get(field) for field in ("source_url", "source", "items")
    ):
        return False, "觀測站資料沒有變更。"
    return write_snapshot(path, snapshot), "觀測站 last-good 快照已更新。"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="手動更新臺灣口琴觀測站竹韻動態備援快照")
    parser.add_argument("--output", default="data/generated/observe_updates.json")
    parser.add_argument("--root", default="")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    try:
        _changed, message = sync(root / args.output)
    except ObserveSyncError as error:
        print(f"ERROR：觀測站同步失敗且沒有可用快照：{error}", file=sys.stderr)
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
