#!/usr/bin/env python3
"""sync_observe.py self-tests using only the Python standard library."""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sync_observe as so  # noqa: E402


NOW = datetime(2026, 7, 16, 12, 0, tzinfo=timezone.utc)


def valid_item(**overrides):
    item = {
        "id": "post-1234abcd",
        "title": "社團成果發表~",
        "excerpt": "此欄不得存入 snapshot",
        "url": "https://example.com/posts/1",
        "sourceName": so.SOURCE_NAME,
        "platform": "Instagram",
        "publishedAt": "2026-07-16T11:30:00Z",
    }
    item.update(overrides)
    return item


def payload(items, **overrides):
    value = {
        "schemaVersion": 1,
        "generatedAt": "2026-07-16T11:45:00Z",
        "source": {
            "id": so.SOURCE_ID,
            "slug": so.SOURCE_SLUG,
            "name": so.SOURCE_NAME,
            "pageUrl": so.SOURCE_URL,
        },
        "items": items,
    }
    value.update(overrides)
    return value


def test_normalizes_minimal_safe_fields_and_taipei_time():
    snapshot = so.snapshot_from_payload(payload([valid_item()]), updated_at=NOW)
    assert snapshot["items"] == [{
        "id": "post-1234abcd",
        "title": "社團成果發表～",
        "source": so.SOURCE_NAME,
        "platform": "Instagram",
        "posted_at_local": "2026-07-16 19:30",
        "link": "https://example.com/posts/1",
    }]
    assert "excerpt" not in json.dumps(snapshot, ensure_ascii=False)


def test_rejects_foreign_or_invalid_source_metadata():
    mutations = [
        {"schemaVersion": 2},
        {"source": {"id": 71, "slug": so.SOURCE_SLUG, "name": so.SOURCE_NAME, "pageUrl": so.SOURCE_URL}},
        {"source": {"id": so.SOURCE_ID, "slug": "foreign", "name": so.SOURCE_NAME, "pageUrl": so.SOURCE_URL}},
        {"source": {"id": so.SOURCE_ID, "slug": so.SOURCE_SLUG, "name": "其他口琴社", "pageUrl": so.SOURCE_URL}},
        {"source": {"id": so.SOURCE_ID, "slug": so.SOURCE_SLUG, "name": so.SOURCE_NAME, "pageUrl": "https://example.com/"}},
    ]
    for mutation in mutations:
        value = payload([valid_item()])
        value.update(mutation)
        try:
            so.snapshot_from_payload(value, updated_at=NOW)
            assert False, f"應拒絕：{mutation!r}"
        except so.ObserveSyncError:
            pass


def test_filters_unsafe_or_missing_item_fields():
    items = [
        valid_item(id="bad id"),
        valid_item(title="<b>不可信 HTML</b>"),
        valid_item(url="http://example.com/insecure"),
        valid_item(sourceName="其他口琴社"),
        valid_item(platform=""),
        valid_item(publishedAt="not-a-date"),
        valid_item(),
    ]
    snapshot = so.snapshot_from_payload(payload(items), updated_at=NOW)
    assert len(snapshot["items"]) == 1


def test_truncates_long_title_and_deduplicates_id_or_url():
    items = [
        valid_item(id="post-1", url="https://example.com/1", title="中文!" * 80),
        valid_item(id="post-1", url="https://example.com/2"),
        valid_item(id="post-2", url="https://example.com/1"),
        valid_item(id="post-3", url="https://example.com/3"),
        valid_item(id="post-4", url="https://example.com/4"),
        valid_item(id="post-5", url="https://example.com/5"),
    ]
    normalized = so.snapshot_from_payload(payload(items), updated_at=NOW)["items"]
    assert [item["id"] for item in normalized] == ["post-1", "post-3", "post-4"]
    assert len(normalized[0]["title"]) == so.MAX_TITLE_LENGTH
    assert normalized[0]["title"].endswith("…") and "中文！" in normalized[0]["title"]


def test_invalid_or_empty_payload_is_rejected():
    values = (None, [], {}, payload([]), payload([valid_item()], generatedAt="bad"))
    for value in values:
        try:
            so.snapshot_from_payload(value, updated_at=NOW)
            assert False, f"應拒絕：{value!r}"
        except so.ObserveSyncError:
            pass


def test_fetch_rejects_timeout_non_2xx_invalid_json_and_oversize():
    class FakeResponse:
        def __init__(self, body=b"{}", status=200, length=None):
            self.body = body
            self.status = status
            self.headers = {} if length is None else {"Content-Length": str(length)}

        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def read(self, _limit): return self.body

    def timeout_opener(*_args, **_kwargs):
        raise TimeoutError("timed out")

    openers = [
        lambda *_args, **_kwargs: FakeResponse(b"not-json"),
        lambda *_args, **_kwargs: FakeResponse(status=503),
        lambda *_args, **_kwargs: FakeResponse(length=so.MAX_RESPONSE_BYTES + 1),
        timeout_opener,
    ]
    for opener in openers:
        try:
            so.fetch_payload(opener=opener)
            assert False, "錯誤回應不得通過"
        except so.ObserveSyncError:
            pass


def test_failures_keep_last_good_bytes():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "observe.json"
        original = so.snapshot_from_payload(payload([valid_item()]), updated_at=NOW)
        so.write_snapshot(path, original)
        original_bytes = path.read_bytes()
        failures = [
            lambda: (_ for _ in ()).throw(so.ObserveSyncError("timeout")),
            lambda: {},
            lambda: payload([]),
        ]
        for fetcher in failures:
            changed, message = so.sync(path, fetcher=fetcher, now=NOW)
            assert changed is False and "沿用" in message
            assert path.read_bytes() == original_bytes


def test_generation_time_does_not_churn_unchanged_items():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "observe.json"
        original = so.snapshot_from_payload(payload([valid_item()]), updated_at=NOW)
        so.write_snapshot(path, original)
        original_bytes = path.read_bytes()
        later = payload([valid_item()], generatedAt="2026-07-17T01:45:00Z")
        changed, message = so.sync(path, fetcher=lambda: later, now=datetime(2026, 7, 17, tzinfo=timezone.utc))
        assert changed is False and message == "觀測站資料沒有變更。"
        assert path.read_bytes() == original_bytes


def test_real_change_updates_both_timestamps():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "observe.json"
        so.write_snapshot(path, so.snapshot_from_payload(payload([valid_item()]), updated_at=NOW))
        changed_payload = payload([valid_item(title="真正的新貼文")], generatedAt="2026-07-17T01:45:00Z")
        changed, message = so.sync(
            path,
            fetcher=lambda: changed_payload,
            now=datetime(2026, 7, 17, tzinfo=timezone.utc),
        )
        updated = json.loads(path.read_text(encoding="utf-8"))
        assert changed is True and "已更新" in message
        assert updated["source_generated_at"] == "2026-07-17T01:45:00Z"
        assert updated["updated_at"] == "2026-07-17T08:00:00+08:00"


def test_failure_without_last_good_is_an_error():
    with tempfile.TemporaryDirectory() as directory:
        try:
            so.sync(Path(directory) / "missing.json", fetcher=lambda: payload([]), now=NOW)
            assert False, "沒有 last-good 時應失敗"
        except so.ObserveSyncError:
            pass


def main() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok   {name}")
        except Exception as error:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {type(error).__name__}: {error}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
