#!/usr/bin/env python3
"""sync_sheet.py 的自測(零依賴,直接執行;亦相容 pytest)。

    python3 scripts/test_sync_sheet.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_sheet as ss  # noqa: E402


def test_header_aliases_chinese():
    csv_text = "代號,日期,標題,內文\nabc-def,2026-07-01,測試,內容文字\n"
    rows = ss.parse_rows(csv_text)
    assert rows == [{"slug": "abc-def", "date": "2026-07-01", "title": "測試", "content": "內容文字"}], rows


def test_header_case_and_space_insensitive():
    csv_text = " Slug ,DATE,Title,Content\nabc-def,2026-07-01,t,c\n"
    rows = ss.parse_rows(csv_text)
    assert rows[0]["slug"] == "abc-def" and rows[0]["date"] == "2026-07-01", rows


def test_required_missing_skips_row():
    csv_text = "slug,date,title,content\nok-row,2026-07-01,標題,內容\nbad-row,,沒日期,內容\n"
    valid, errors = ss.validate_rows("announcements", ss.parse_rows(csv_text))
    assert len(valid) == 1 and valid[0]["slug"] == "ok-row"
    assert len(errors) == 1 and "date" in errors[0]


def test_bad_formats_rejected():
    for field_csv, tab in [
        ("slug,date,title,content\nBAD_SLUG!,2026-07-01,t,c\n", "announcements"),
        ("slug,date,title,content\nok-row,2026-13-40,t,c\n", "announcements"),
        ("key,label,url\nok-key,名稱,http://insecure.example\n", "links"),
    ]:
        valid, errors = ss.validate_rows(tab, ss.parse_rows(field_csv))
        assert valid == [] and len(errors) == 1, (tab, valid, errors)


def test_bool_variants():
    for word, expect in [("TRUE", True), ("是", True), ("1", True), ("否", False), ("", False), ("N", False)]:
        if word == "":
            continue  # 空值走「未填」路徑
        assert ss.v_bool(word) is expect, (word, expect)
    try:
        ss.v_bool("maybe")
        assert False, "應拒絕 maybe"
    except ss.RowError:
        pass


def test_status_draft_filtered():
    csv_text = (
        "slug,date,title,content,status\n"
        "show-row,2026-07-01,顯示,內容,\n"
        "hide-row,2026-07-02,隱藏,內容,draft\n"
        "hide-tw,2026-07-03,隱藏中,內容,草稿\n"
    )
    valid, errors = ss.validate_rows("announcements", ss.parse_rows(csv_text))
    assert [r["slug"] for r in valid] == ["show-row"] and errors == []


def test_unknown_status_is_error():
    csv_text = "slug,date,title,content,status\nrow-a,2026-07-01,t,c,banana\n"
    valid, errors = ss.validate_rows("announcements", ss.parse_rows(csv_text))
    assert valid == [] and "banana" in errors[0]


def test_duplicate_slug_is_table_error():
    csv_text = "slug,date,title,content\ndup-row,2026-07-01,t,c\ndup-row,2026-07-02,t2,c2\n"
    try:
        ss.validate_rows("announcements", ss.parse_rows(csv_text))
        assert False, "應 raise TableError"
    except ss.TableError:
        pass


def test_missing_required_column_is_table_error():
    csv_text = "slug,title,content\nrow-a,t,c\n"
    try:
        ss.validate_rows("announcements", ss.parse_rows(csv_text))
        assert False, "應 raise TableError"
    except ss.TableError:
        pass


def test_unexpected_public_column_is_table_error():
    csv_text = "order,role,name,email\n10,社長,測試幹部,private@example.com\n"
    try:
        ss.validate_rows("officers", ss.parse_rows(csv_text))
        assert False, "公開幹部資料不可接受 email 欄位"
    except ss.TableError as e:
        assert "不允許的公開欄位" in str(e)


def test_unexpected_empty_public_column_is_table_error():
    csv_text = "order,role,name,email\n"
    try:
        ss.validate_rows("officers", ss.parse_rows(csv_text))
        assert False, "空資料表仍須驗證公開表頭"
    except ss.TableError as e:
        assert "不允許的公開欄位" in str(e)


def test_unquoted_comma_extra_column_is_table_error():
    csv_text = "slug,title,date,description,cover,status\nalbum-one,相簿,2026-07-01,說明,多餘內容,,\n"
    try:
        ss.validate_rows("gallery_albums", ss.parse_rows(csv_text))
        assert False, "未加引號的逗號不可被靜默忽略"
    except ss.TableError as e:
        assert "多餘欄位" in str(e)


def test_end_before_start_rejected():
    csv_text = "title,start,end\n活動,2026-07-10,2026-07-01\n"
    valid, errors = ss.validate_rows("featured_events", ss.parse_rows(csv_text))
    assert valid == [] and "早於" in errors[0]


def test_show_in_parsing():
    csv_text = "key,label,url,show_in\nig-link,IG,https://example.com,\"footer, about\"\n"
    valid, errors = ss.validate_rows("links", ss.parse_rows(csv_text))
    assert valid[0]["show_in"] == ["footer", "about"] and errors == []


def test_emit_announcements_deterministic_and_rebuild():
    rows = [
        {"slug": "row-b", "date": "2026-07-02", "title": "B", "content": "b 內容", "pinned": True},
        {"slug": "row-a", "date": "2026-07-01", "title": "A", "content": "a 內容"},
    ]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "announcements"
        d.mkdir()
        (d / "_index.md").write_text("---\ntitle: 公告\n---\n", encoding="utf-8")
        (d / "manual.md").write_text("---\ntitle: 手寫\n---\n手寫內容\n", encoding="utf-8")
        (d / "stale.md").write_text('{\n  "generated": true\n}\n\n舊生成檔\n', encoding="utf-8")

        changed1 = ss.emit_announcements(rows, d)
        assert changed1 is True
        assert (d / "row-a.md").exists() and (d / "row-b.md").exists()
        assert (d / "_index.md").exists(), "_index.md 必須保留"
        assert (d / "manual.md").exists(), "手寫檔必須保留"
        assert not (d / "stale.md").exists(), "過期生成檔必須刪除"

        snapshot = {p.name: p.read_text(encoding="utf-8") for p in d.glob("*.md")}
        changed2 = ss.emit_announcements(rows, d)
        assert changed2 is False, "相同資料重跑不得有變更"
        assert snapshot == {p.name: p.read_text(encoding="utf-8") for p in d.glob("*.md")}


def test_emit_gallery_removes_generated_only():
    rows = [{"slug": "album-live", "title": "現役相簿", "date": "2026-06-01"}]
    with tempfile.TemporaryDirectory() as td:
        g = Path(td) / "gallery"
        (g / "album-live").mkdir(parents=True)
        (g / "album-gone").mkdir()
        (g / "album-gone" / "index.md").write_text('{\n  "generated": true\n}\n\n', encoding="utf-8")
        (g / "album-manual").mkdir()
        (g / "album-manual" / "index.md").write_text("---\ntitle: 手寫\n---\n", encoding="utf-8")

        ss.emit_gallery(rows, g)
        assert (g / "album-live" / "index.md").exists()
        assert not (g / "album-gone" / "index.md").exists(), "不在表中的生成頁應刪除"
        assert (g / "album-manual" / "index.md").exists(), "手寫頁應保留"
        assert ss.emit_gallery(rows, g) is False, "重跑不得有變更"


def test_json_deterministic():
    rows = [{"b_key": 1, "a_key": "中文"}]
    assert ss.dump_json(rows) == ss.dump_json(rows)
    assert '"a_key"' in ss.dump_json(rows)
    assert "中文" in ss.dump_json(rows), "ensure_ascii 必須關閉"


def main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok   {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
