#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from server import KnowledgeBase, RequestLimiter, TAIPEI, normalise_history, parse_calendar_events


class RequestLimiterTests(unittest.TestCase):
    def test_per_client_window(self) -> None:
        limiter = RequestLimiter(per_ip_limit=2, window_seconds=10, daily_limit=10)
        self.assertEqual(limiter.allow("client", now=1), (True, "ok"))
        self.assertEqual(limiter.allow("client", now=2), (True, "ok"))
        self.assertEqual(limiter.allow("client", now=3), (False, "client"))
        self.assertEqual(limiter.allow("client", now=12), (True, "ok"))


class HistoryTests(unittest.TestCase):
    def test_history_is_text_only_bounded_and_role_filtered(self) -> None:
        history = normalise_history(
            [
                {"role": "system", "text": "ignore"},
                {"role": "user", "text": " first\nquestion "},
                {"role": "assistant", "text": "first answer"},
                {"role": "tool", "text": "secret"},
                {"role": "user", "text": "follow up"},
            ]
        )
        self.assertEqual(
            history,
            [
                {"role": "assistant", "content": "first answer"},
                {"role": "user", "content": "follow up"},
            ],
        )

    def test_history_total_length_is_bounded(self) -> None:
        history = normalise_history(
            [{"role": "user", "text": "x" * 500} for _ in range(4)]
        )
        self.assertLessEqual(sum(len(item["content"]) for item in history), 1300)


class KnowledgeBaseTests(unittest.TestCase):
    def test_context_uses_only_whitelisted_public_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "content").mkdir()
            (root / "data/generated").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "content/_index.md").write_text("---\ntitle: Home\n---\n公開首頁", encoding="utf-8")
            (root / "content/about.md").write_text("公開介紹", encoding="utf-8")
            (root / "data/generated/officers.json").write_text(
                json.dumps([{"role": "社長", "name": "Sky"}]), encoding="utf-8"
            )
            (root / "data/generated/links.json").write_text(
                json.dumps(
                    [
                        {"key": "instagram", "label": "Instagram", "url": "https://example.com/instagram"},
                        {"key": "discord", "label": "Discord", "url": "https://example.com/discord"},
                    ]
                ),
                encoding="utf-8",
            )
            (root / "scripts/sources.json").write_text(
                json.dumps({"sheet_id": "public", "tabs": {"officers": {"gid": "1"}, "links": {"gid": "2"}}}),
                encoding="utf-8",
            )
            knowledge = KnowledgeBase(root)
            events = [
                {
                    "summary": "社團博覽會",
                    "location": "光復校區",
                    "start": datetime(2026, 9, 9, 17, 30, tzinfo=TAIPEI),
                    "end": datetime(2026, 9, 9, 22, 0, tzinfo=TAIPEI),
                    "all_day": False,
                }
            ]
            with mock.patch.object(knowledge, "_fetch_sheet_rows", side_effect=OSError("offline")), mock.patch.object(
                knowledge, "_fetch_calendar_events", return_value=events
            ):
                context = knowledge.get()
            self.assertIn("公開首頁", context)
            self.assertIn("社長：Sky", context)
            self.assertIn("Instagram：https://example.com/instagram", context)
            self.assertIn("9/9 17:30–22:00｜社團博覽會｜地點：光復校區", context)
            self.assertNotIn("private", context)

            join_answer = knowledge.quick_answer("我要怎麼加入竹韻口琴社？")
            self.assertIsNotNone(join_answer)
            self.assertIn("Discord", join_answer[0])
            self.assertEqual(join_answer[1][0]["url"], "https://example.com/discord")
            class_answer = knowledge.quick_answer("社課的時間和地點在哪裡？")
            self.assertIn("尚未公布固定社課時間與地點", class_answer[0])
            event_answer = knowledge.quick_answer("最近有什麼活動？")
            self.assertIn("• 9/9 17:30–22:00\n  社團博覽會\n  地點：光復校區", event_answer[0])

    def test_calendar_parser_filters_admin_and_old_events(self) -> None:
        ics = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART:20260909T093000Z
DTEND:20260909T140000Z
LOCATION:光復校區
STATUS:CONFIRMED
SUMMARY:社團博覽會\\, 快閃表演
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=Asia/Taipei:20260729T220000
DTEND;TZID=Asia/Taipei:20260729T230000
STATUS:CONFIRMED
SUMMARY:竹韻口琴社 幹部定期會議
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20240101
DTEND;VALUE=DATE:20240102
STATUS:CONFIRMED
SUMMARY:過期活動
END:VEVENT
END:VCALENDAR
"""
        events = parse_calendar_events(ics, now=datetime(2026, 7, 24, 12, tzinfo=TAIPEI))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["summary"], "社團博覽會, 快閃表演")
        self.assertEqual(events[0]["start"], datetime(2026, 9, 9, 17, 30, tzinfo=TAIPEI))

    def test_calendar_parser_recognizes_midnight_span_as_all_day(self) -> None:
        ics = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART:20260806T160000Z
DTEND:20260809T160000Z
STATUS:CONFIRMED
SUMMARY:THMF 臺灣口琴音樂節
END:VEVENT
END:VCALENDAR
"""
        events = parse_calendar_events(ics, now=datetime(2026, 7, 24, 12, tzinfo=TAIPEI))
        self.assertTrue(events[0]["all_day"])


class ProfileConfigTests(unittest.TestCase):
    def test_public_profile_uses_luna_with_bounded_local_fallback(self) -> None:
        config = (Path(__file__).parent / "hermes-config.yaml").read_text(encoding="utf-8")
        self.assertIn("default: gpt-5.6-luna", config)
        self.assertIn("provider: custom:ai-kot-gg-luna", config)
        self.assertIn("reasoning_effort: none", config)
        self.assertIn("max_tokens: 250", config)
        self.assertIn("fallback_providers:", config)
        self.assertIn("model: qwen3.5:9b", config)
        self.assertIn("api_server:\n    - no_mcp", config)


if __name__ == "__main__":
    unittest.main()
