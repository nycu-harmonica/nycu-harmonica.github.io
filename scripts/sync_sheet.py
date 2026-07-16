#!/usr/bin/env python3
"""竹韻口琴社網站資料同步腳本。

從社團共用 Google Sheet(公開可讀)下載各工作表 CSV,驗證欄位後產生
Hugo 所需的內容與資料檔,並更新 repo 內的 CSV 快照(fallback)。

只使用 Python 標準庫,無第三方依賴。

用法:
    python3 scripts/sync_sheet.py              # 線上同步,失敗自動改用快照
    python3 scripts/sync_sheet.py --offline    # 不連網,直接用 static/data/ 快照重建
    python3 scripts/sync_sheet.py --strict     # CI 用:抓取失敗或驗證錯誤時 exit 1
    python3 scripts/sync_sheet.py --only announcements,links
    python3 scripts/sync_sheet.py --root <repo 根目錄>

輸出:
    static/data/<tab>.csv                CSV 快照(僅線上抓取成功且驗證通過時覆寫)
    data/generated/<tab>.json            featured_events / officers / links / gallery_albums
    content/announcements/<slug>.md      公告頁(全部重建;_index.md 與手寫檔保留)
    content/gallery/<slug>/index.md      相簿頁 front matter(照片另由目錄管理)
    data/generated/last_sync.json        輸出或來源模式有變更時更新
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

TAIPEI = timezone(timedelta(hours=8))
GENERATED_MARK = '"generated": true'

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,60}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TRUE_WORDS = {"true", "1", "y", "yes", "是", "v"}
FALSE_WORDS = {"false", "0", "n", "no", "否", ""}
DRAFT_WORDS = {"draft", "草稿", "hidden", "隱藏"}
PUBLISHED_WORDS = {"", "published", "發布", "公開"}
ICON_ENUM = {"instagram", "facebook", "youtube", "email", "line", "link"}
SHOW_IN_ENUM = {"footer", "about", "join"}

# 表頭別名:Sheet 可用中文表頭,一律轉為正規英文欄名
HEADER_ALIASES = {
    "代號": "slug", "日期": "date", "標題": "title", "內文": "content",
    "置頂": "pinned", "連結": "link", "狀態": "status",
    "開始日期": "start", "結束日期": "end", "時間": "time_text",
    "地點": "location", "簡介": "summary",
    "排序": "order", "職稱": "role", "姓名": "name",
    "說明": "description", "封面": "cover",
    "名稱": "label", "網址": "url", "圖示": "icon", "顯示位置": "show_in",
    "key": "key",
}


class RowError(Exception):
    """單列驗證錯誤:跳過該列。"""


class TableError(Exception):
    """表級錯誤(缺欄位/唯一鍵重複):整個 tab 視為失敗,沿用舊快照。"""


class ParsedRows(list):
    """CSV rows that retain normalized headers even when the table is empty."""

    def __init__(self, values: list[dict], field_names: list[str]):
        super().__init__(values)
        self.field_names = field_names


# ---------------------------------------------------------------- 基礎工具

def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}", file=sys.stderr if level in ("warn", "error") else sys.stdout)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_newlines(text).encode("utf-8")).hexdigest()


def write_if_changed(path: Path, content: str) -> bool:
    """寫檔;內容相同則不動。回傳是否有變更。"""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def dump_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


# ---------------------------------------------------------------- 欄位驗證

def v_text(value: str, _row=None) -> str:
    return value.strip()


def v_slug(value: str, _row=None) -> str:
    value = value.strip().lower()
    if not SLUG_RE.match(value):
        raise RowError(f"slug 格式錯誤(僅小寫英數與連字號,3–61 字):{value!r}")
    return value


def v_date(value: str, _row=None) -> str:
    value = value.strip()
    if not DATE_RE.match(value):
        raise RowError(f"日期須為 YYYY-MM-DD:{value!r}")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise RowError(f"無效日期:{value!r}")
    return value


def v_url(value: str, _row=None) -> str:
    value = value.strip()
    if not (value.startswith("https://") or value.startswith("mailto:")):
        raise RowError(f"連結僅接受 https:// 或 mailto::{value!r}")
    return value


def v_bool(value: str, _row=None) -> bool:
    v = value.strip().lower()
    if v in TRUE_WORDS:
        return True
    if v in FALSE_WORDS:
        return False
    raise RowError(f"布林值無法解析:{value!r}(可用 TRUE/FALSE/是/否/Y/N/1/0)")


def v_int(value: str, _row=None) -> int:
    try:
        return int(value.strip())
    except ValueError:
        raise RowError(f"須為整數:{value!r}")


def v_icon(value: str, _row=None) -> str:
    v = value.strip().lower()
    if v not in ICON_ENUM:
        raise RowError(f"圖示須為 {sorted(ICON_ENUM)} 之一:{value!r}")
    return v


def v_show_in(value: str, _row=None):
    items = [s.strip().lower() for s in value.split(",") if s.strip()]
    bad = [s for s in items if s not in SHOW_IN_ENUM]
    if bad:
        raise RowError(f"顯示位置僅接受 {sorted(SHOW_IN_ENUM)}:{bad}")
    return items


def v_filename(value: str, _row=None) -> str:
    value = value.strip()
    if "/" in value or "\\" in value or value.startswith("."):
        raise RowError(f"檔名不可含路徑:{value!r}")
    return value


# 每個 tab 的欄位規格:(欄名, 必填, 驗證函式)
TAB_SPECS = {
    "announcements": {
        "unique": "slug",
        "fields": [
            ("slug", True, v_slug),
            ("date", True, v_date),
            ("title", True, v_text),
            ("content", True, v_text),
            ("pinned", False, v_bool),
            ("link", False, v_url),
            ("status", False, v_text),
        ],
    },
    "featured_events": {
        "unique": None,
        "fields": [
            ("title", True, v_text),
            ("start", True, v_date),
            ("end", False, v_date),
            ("time_text", False, v_text),
            ("location", False, v_text),
            ("summary", False, v_text),
            ("link", False, v_url),
            ("status", False, v_text),
        ],
    },
    "officers": {
        "unique": None,
        "fields": [
            ("order", True, v_int),
            ("role", True, v_text),
            ("name", True, v_text),
            ("status", False, v_text),
        ],
    },
    "gallery_albums": {
        "unique": "slug",
        "fields": [
            ("slug", True, v_slug),
            ("title", True, v_text),
            ("date", True, v_date),
            ("description", False, v_text),
            ("cover", False, v_filename),
            ("status", False, v_text),
        ],
    },
    "links": {
        "unique": "key",
        "fields": [
            ("key", True, v_slug),
            ("label", True, v_text),
            ("url", True, v_url),
            ("icon", False, v_icon),
            ("order", False, v_int),
            ("show_in", False, v_show_in),
        ],
    },
}


# ---------------------------------------------------------------- 解析

def normalize_header(name: str) -> str:
    name = (name or "").strip().lstrip("﻿")
    key = name.lower().replace(" ", "_").replace("-", "_")
    return HEADER_ALIASES.get(name, HEADER_ALIASES.get(key, key))


def parse_rows(csv_text: str) -> ParsedRows:
    reader = csv.DictReader(io.StringIO(normalize_newlines(csv_text)))
    if not reader.fieldnames:
        return ParsedRows([], [])
    header_map = {h: normalize_header(h) for h in reader.fieldnames}
    normalized_field_names = list(header_map.values())
    rows = []
    for raw in reader:
        row = {}
        extra_column_count = 0
        for k, v in raw.items():
            if k is None:
                values = v if isinstance(v, list) else [v]
                extra_column_count += len(values)
                continue
            row[header_map.get(k, k)] = (v or "").strip()
        if extra_column_count:
            row["__extra_columns__"] = extra_column_count
        if any(v for v in row.values()):
            rows.append(row)
    return ParsedRows(rows, normalized_field_names)


def validate_rows(tab: str, rows: list[dict]) -> tuple[list[dict], list[str]]:
    """回傳 (合法列, 錯誤訊息)。列級錯誤跳過該列;表級錯誤 raise TableError。"""
    spec = TAB_SPECS[tab]
    field_names = [f[0] for f in spec["fields"]]
    required = [f[0] for f in spec["fields"] if f[1]]

    present = set(getattr(rows, "field_names", rows[0].keys() if rows else []))
    missing_cols = [c for c in required if c not in present]
    if missing_cols:
        raise TableError(f"{tab}: 缺少必要欄位 {missing_cols}(表頭:{sorted(present)})")
    unexpected_cols = sorted(c for c in present if c not in field_names and not c.startswith("__"))
    if unexpected_cols:
        raise TableError(f"{tab}: 不允許的公開欄位 {unexpected_cols}")

    valid, errors, seen_unique = [], [], set()
    for i, row in enumerate(rows, start=2):  # Sheet 列號(含表頭)
        if row.get("__extra_columns__"):
            raise TableError(f"{tab}: 第 {i} 列有多餘欄位,請檢查未加引號的逗號")
        status = row.get("status", "").strip().lower()
        if status in DRAFT_WORDS:
            continue
        if status not in PUBLISHED_WORDS and status not in DRAFT_WORDS:
            errors.append(f"{tab} 第 {i} 列:狀態值 {row.get('status')!r} 無法辨識,已跳過")
            continue
        out, row_errs = {}, []
        for name, req, validator in spec["fields"]:
            raw_val = row.get(name, "")
            if not raw_val:
                if req:
                    row_errs.append(f"缺少必填欄位 {name}")
                continue
            try:
                out[name] = validator(raw_val, row)
            except RowError as e:
                row_errs.append(str(e))
        if not row_errs and "start" in out and "end" in out and out["end"] < out["start"]:
            row_errs.append(f"end({out['end']})早於 start({out['start']})")
        if row_errs:
            errors.append(f"{tab} 第 {i} 列:{';'.join(row_errs)},已跳過")
            continue
        uniq = spec["unique"]
        if uniq:
            if out[uniq] in seen_unique:
                raise TableError(f"{tab}: {uniq} 重複:{out[uniq]!r}")
            seen_unique.add(out[uniq])
        out.pop("status", None)
        valid.append(out)
    return valid, errors


# ---------------------------------------------------------------- 抓取

def fetch_csv(sheet_id: str, gid: str, timeout: int = 30) -> str | None:
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
        f"?format=csv&gid={gid}&_cb={int(time.time())}"
    )
    req = urllib.request.Request(url, headers={
        "Cache-Control": "no-cache",
        "User-Agent": "harmonica-nycu-site-sync/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        log("warn", f"下載失敗(gid={gid}):{e}")
        return None
    if not data.strip() or data.lstrip().startswith("<"):
        log("warn", f"回應不是 CSV(gid={gid}),Sheet 可能未設定公開讀取")
        return None
    return data


# ---------------------------------------------------------------- 輸出

def emit_json(rows: list, path: Path) -> bool:
    return write_if_changed(path, dump_json(rows))


def front_matter(fm: dict) -> str:
    return json.dumps(fm, ensure_ascii=False, sort_keys=True, indent=2)


def is_generated_file(path: Path) -> bool:
    try:
        return GENERATED_MARK in path.read_text(encoding="utf-8")
    except OSError:
        return False


def emit_announcements(rows: list[dict], content_dir: Path) -> bool:
    changed = False
    desired = {}
    for r in rows:
        fm = {
            "title": r["title"],
            "date": r["date"],
            "slug": r["slug"],
            "pinned": r.get("pinned", False),
            "generated": True,
        }
        if r.get("link"):
            fm["link"] = r["link"]
        body = r["content"].strip() + "\n"
        desired[f"{r['slug']}.md"] = front_matter(fm) + "\n\n" + body
    content_dir.mkdir(parents=True, exist_ok=True)
    for old in sorted(content_dir.glob("*.md")):
        if old.name == "_index.md" or old.name in desired:
            continue
        if is_generated_file(old):
            old.unlink()
            log("info", f"移除已下架公告:{old.name}")
            changed = True
    for name, text in sorted(desired.items()):
        if write_if_changed(content_dir / name, text):
            changed = True
    return changed


def emit_gallery(rows: list[dict], gallery_dir: Path) -> bool:
    changed = False
    gallery_dir.mkdir(parents=True, exist_ok=True)
    slugs = {r["slug"] for r in rows}
    for r in rows:
        album_dir = gallery_dir / r["slug"]
        if not album_dir.is_dir():
            log("warn", f"相簿 {r['slug']} 在資料表中,但 content/gallery/{r['slug']}/ 目錄不存在(照片尚未放入)")
        fm = {
            "title": r["title"],
            "date": r["date"],
            "generated": True,
        }
        if r.get("cover"):
            fm["cover"] = r["cover"]
        body = (r.get("description", "").strip() + "\n") if r.get("description") else ""
        text = front_matter(fm) + "\n\n" + body
        if write_if_changed(album_dir / "index.md", text):
            changed = True
    for album_dir in sorted(p for p in gallery_dir.iterdir() if p.is_dir()):
        if album_dir.name in slugs:
            continue
        idx = album_dir / "index.md"
        if idx.exists() and is_generated_file(idx):
            idx.unlink()
            log("warn", f"相簿目錄 {album_dir.name}/ 不在資料表中,已移除其生成頁(照片檔保留)")
            changed = True
        elif idx.exists():
            log("info", f"相簿 {album_dir.name}/ 為手寫頁,保留")
    return changed


# ---------------------------------------------------------------- 主流程

def load_sources(root: Path) -> dict:
    return json.loads((root / "scripts" / "sources.json").read_text(encoding="utf-8"))


def sync(root: Path, offline: bool, strict: bool, only: set[str] | None) -> int:
    sources = load_sources(root)
    sheet_id = sources.get("sheet_id", "")
    snapshot_dir = root / "static" / "data"
    generated_dir = root / "data" / "generated"

    placeholder = (not sheet_id) or sheet_id.startswith("REPLACE")
    if placeholder and not offline:
        log("info", "sources.json 的 sheet_id 尚未設定,自動改用離線模式(使用 CSV 快照)")
        offline = True

    any_changed = False
    fetch_failures: list[str] = []
    validation_errors: list[str] = []
    tab_stats: dict[str, dict] = {}
    online_tabs = 0
    snapshot_tabs = 0

    for tab in TAB_SPECS:
        if only and tab not in only:
            continue
        snapshot_path = snapshot_dir / f"{tab}.csv"

        csv_text = None
        if not offline:
            gid = str(sources["tabs"].get(tab, {}).get("gid", ""))
            if not gid or gid.startswith("REPLACE"):
                log("warn", f"{tab}: gid 未設定,改用快照")
                fetch_failures.append(tab)
            else:
                csv_text = fetch_csv(sheet_id, gid)
                if csv_text is None:
                    fetch_failures.append(tab)

        if csv_text is not None:
            # 先驗證表級結構,通過才覆寫快照
            try:
                rows_probe = parse_rows(csv_text)
                validate_rows(tab, rows_probe)
            except TableError as e:
                log("warn", f"{tab}: 表級驗證失敗({e}),沿用舊快照")
                fetch_failures.append(tab)
                csv_text = None
            else:
                if write_if_changed(snapshot_path, normalize_newlines(csv_text)):
                    log("info", f"{tab}: 快照已更新")

        if csv_text is None:
            if not snapshot_path.exists():
                msg = f"{tab}: 無可用資料(線上抓取失敗且無快照)"
                log("error", msg)
                validation_errors.append(msg)
                continue
            csv_text = snapshot_path.read_text(encoding="utf-8")
            snapshot_tabs += 1
        else:
            online_tabs += 1

        try:
            rows, errors = validate_rows(tab, parse_rows(csv_text))
        except TableError as e:
            msg = f"{tab}: 快照驗證失敗:{e}"
            log("error", msg)
            validation_errors.append(msg)
            continue
        for e in errors:
            log("warn", e)
        validation_errors.extend(errors)

        if tab == "announcements":
            rows.sort(key=lambda r: (r["date"], r["slug"]), reverse=True)
            changed = emit_announcements(rows, root / "content" / "announcements")
        elif tab == "gallery_albums":
            rows.sort(key=lambda r: (r["date"], r["slug"]), reverse=True)
            changed = emit_gallery(rows, root / "content" / "gallery")
            changed = emit_json(rows, generated_dir / "gallery_albums.json") or changed
        elif tab == "featured_events":
            rows.sort(key=lambda r: (r["start"], r["title"]))
            changed = emit_json(rows, generated_dir / "featured_events.json")
        elif tab == "officers":
            rows.sort(key=lambda r: (r["order"], r["name"]))
            changed = emit_json(rows, generated_dir / "officers.json")
        elif tab == "links":
            rows.sort(key=lambda r: (r.get("order", 999), r["key"]))
            changed = emit_json(rows, generated_dir / "links.json")
        else:  # pragma: no cover
            changed = False

        tab_stats[tab] = {"rows": len(rows), "hash": "sha256:" + content_hash(csv_text)}
        any_changed = any_changed or changed
        log("info", f"{tab}: {len(rows)} 筆有效資料{'(有變更)' if changed else ''}")

    if online_tabs and snapshot_tabs:
        source_mode = "mixed_fallback"
    elif online_tabs:
        source_mode = "google_sheet"
    else:
        source_mode = "repo_snapshot"

    last_sync_path = generated_dir / "last_sync.json"
    previous_source_mode = ""
    if last_sync_path.exists():
        try:
            previous_source_mode = json.loads(last_sync_path.read_text(encoding="utf-8")).get("source_mode", "")
        except (OSError, json.JSONDecodeError):
            pass

    if any_changed or previous_source_mode != source_mode:
        now = datetime.now(TAIPEI).replace(microsecond=0)
        last_sync = {"updated_at": now.isoformat(), "source_mode": source_mode, "tabs": tab_stats}
        write_if_changed(last_sync_path, dump_json(last_sync))
        log("info", f"輸出有變更,last_sync.json 已更新:{now.isoformat()}")
    else:
        log("info", "所有輸出無變更(不更新 last_sync.json)")

    if strict:
        if validation_errors:
            log("error", f"strict 模式:共 {len(validation_errors)} 個驗證問題")
            return 1
        if fetch_failures and not placeholder:
            log("error", f"strict 模式:以下 tab 線上抓取失敗:{fetch_failures}")
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="同步 Google Sheet 資料並產生 Hugo 內容")
    parser.add_argument("--offline", action="store_true", help="不連網,直接用 CSV 快照")
    parser.add_argument("--strict", action="store_true", help="有錯誤時以非零值結束(CI 用)")
    parser.add_argument("--only", default="", help="只處理指定 tab(逗號分隔)")
    parser.add_argument("--root", default="", help="repo 根目錄(預設由腳本位置推導)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    only = {t.strip() for t in args.only.split(",") if t.strip()} or None
    if only:
        unknown = only - set(TAB_SPECS)
        if unknown:
            parser.error(f"未知的 tab:{sorted(unknown)}")
    return sync(root, offline=args.offline, strict=args.strict, only=only)


if __name__ == "__main__":
    raise SystemExit(main())
