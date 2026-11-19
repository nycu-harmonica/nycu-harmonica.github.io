#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from server import HermesClient, KnowledgeBase, RequestLimiter, TAIPEI, normalise_history, parse_calendar_events


class HermesClientTests(unittest.TestCase):
    def ask_with_response(self, payload):
        settings = mock.Mock(hermes_url="http://127.0.0.1:8643/v1/chat/completions", request_timeout_seconds=10)
        client = HermesClient(settings)
        with mock.patch.object(client, "_api_key", return_value="synthetic-test-key"), mock.patch(
            "server.request.urlopen"
        ) as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            return client.ask("公開問題", [], "公開指示", "公開資料")

    def test_http_200_agent_failure_is_not_a_public_answer(self):
        with self.assertRaisesRegex(RuntimeError, "Hermes model request failed"):
            self.ask_with_response({
                "choices": [{"message": {"content": "Provider rejected your API key"}, "finish_reason": "error"}],
                "hermes": {"completed": False, "failed": True, "error": "HTTP 401"},
            })

    def test_success_and_token_limited_text_remain_answers(self):
        for reason in ["stop", "length"]:
            with self.subTest(finish_reason=reason):
                payload = {"choices": [{"message": {"content": "竹韻以口琴合奏演出。"}, "finish_reason": reason}]}
                if reason == "length":
                    payload["hermes"] = {"completed": False, "partial": True, "failed": False}
                self.assertEqual(self.ask_with_response(payload), "竹韻以口琴合奏演出。")


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
                json.dumps({"sheet_id": "public", "tabs": {"links": {"gid": "2"}}}),
                encoding="utf-8",
            )
            (root / "hugo.toml").write_text(
                '[params]\ncontactEmail = "club@example.com"\n', encoding="utf-8"
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
            self.assertIn("Instagram：https://example.com/instagram", context)
            self.assertIn("9/9 17:30–22:00｜社團博覽會｜地點：光復校區", context)
            self.assertIn("club@example.com", context)
            # 幹部姓名已從官網下架,公開問答的 context 也不得再帶入名單。
            self.assertNotIn("【公開幹部名單】", context)
            self.assertNotIn("private", context)

            contact_answer = knowledge.quick_answer("請問你們的聯絡信箱是什麼？")
            self.assertIsNotNone(contact_answer)
            self.assertIn("club@example.com", contact_answer[0])
            self.assertEqual(contact_answer[1][0]["url"], "https://harmonica.nycu.club/about/#join")

            join_answer = knowledge.quick_answer("我要怎麼加入竹韻口琴社？")
            self.assertIsNotNone(join_answer)
            self.assertIn("Discord", join_answer[0])
            self.assertEqual(join_answer[1][0]["url"], "https://example.com/discord")
            class_answer = knowledge.quick_answer("社課的時間和地點在哪裡？")
            self.assertIn("未找到近期社課", class_answer[0])
            self.assertNotIn("尚未公布", class_answer[0])
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

    def test_class_answer_uses_expanded_public_occurrences_beyond_activity_preview(self) -> None:
        knowledge = KnowledgeBase(Path("unused"))
        classes = parse_calendar_events(CalendarRecurrenceTests.SERIES, now=CalendarRecurrenceTests.NOW)
        # Busy calendars must not hide a class behind the eight-entry model preview.
        knowledge._events = [{**classes[0], "summary": "公開音樂會"} for _ in range(8)] + classes
        knowledge._calendar_available = True
        with mock.patch.object(knowledge, "get"), mock.patch.object(knowledge, "_contact_email", return_value=""):
            answer, sources = knowledge.quick_answer("新生想加入，社課什麼時候、在哪裡？")
        self.assertIn("10/27 19:00–21:00", answer)
        self.assertIn("測試教室", answer)
        self.assertNotIn("尚未公布", answer)
        self.assertNotIn("公開音樂會", answer)
        self.assertEqual(sources[0]["url"], "https://harmonica.nycu.club/#calendar")

    def test_class_answer_preserves_missing_location_and_all_day_uncertainty(self) -> None:
        knowledge = KnowledgeBase(Path("unused"))
        knowledge._events = [{
            "summary": "公開社課", "location": "", "all_day": True,
            "start": datetime(2026, 10, 27, tzinfo=TAIPEI),
            "end": datetime(2026, 10, 28, tzinfo=TAIPEI),
        }]
        with mock.patch.object(knowledge, "get"), mock.patch.object(knowledge, "_contact_email", return_value=""):
            answer, _ = knowledge.quick_answer("社課星期幾？")
        self.assertIn("10/27（全天）", answer)
        self.assertIn("公開行事曆未列出", answer)
        self.assertIn("未提供確切上課時段", answer)

    def test_calendar_failure_does_not_present_stale_classes_as_current(self) -> None:
        knowledge = KnowledgeBase(Path("unused"))
        knowledge._events = parse_calendar_events(CalendarRecurrenceTests.SERIES, now=CalendarRecurrenceTests.NOW)
        with mock.patch.object(knowledge, "_read_public_text", return_value="公開資料"), mock.patch.object(
            knowledge, "_contact_email", return_value=""
        ), mock.patch.object(knowledge, "_public_rows", return_value=[]), mock.patch.object(
            knowledge, "_fetch_calendar_events", side_effect=OSError("offline")
        ):
            with self.assertLogs("bamboo-website-agent", level="WARNING"):
                answer, _ = knowledge.quick_answer("社課何時？")
        self.assertIn("無法讀取公開行事曆", answer)
        self.assertNotIn("10/27", answer)
        self.assertNotIn("尚未公布", answer)
        self.assertEqual(knowledge._events, [])


class CalendarRecurrenceTests(unittest.TestCase):
    NOW = datetime(2026, 10, 22, 12, tzinfo=TAIPEI)
    SERIES = """BEGIN:VCALENDAR
BEGIN:VEVENT
UID:synthetic-class
DTSTART;TZID=Asia/Taipei:20260915T190000
DTEND;TZID=Asia/Taipei:20260915T210000
RRULE:FREQ=WEEKLY;COUNT=15;BYDAY=TU
SUMMARY:竹韻社課（合成測試）
LOCATION:測試教室
END:VEVENT
END:VCALENDAR
"""

    def parse(self, text: str) -> list[dict]:
        return parse_calendar_events(text, now=self.NOW)

    def test_fifteen_week_september_series_still_has_october_classes(self) -> None:
        events = self.parse(self.SERIES)
        self.assertEqual(len(events), 9)
        self.assertEqual(events[0]["start"], datetime(2026, 10, 27, 19, tzinfo=TAIPEI))
        self.assertEqual(events[0]["end"], datetime(2026, 10, 27, 21, tzinfo=TAIPEI))
        self.assertEqual(events[-1]["start"], datetime(2026, 12, 22, 19, tzinfo=TAIPEI))
        self.assertEqual(self.parse(self.SERIES.replace("COUNT=15", "COUNT=5")), [])

    def test_repeated_exdates_rdates_and_folded_lines(self) -> None:
        text = self.SERIES.replace("SUMMARY:", """EXDATE;TZID=Asia/Taipei:20261027T190000
EXDATE;TZID=Asia/Taipei:20261110T190000,20261117T190000
RDATE;TZID=Asia/Taipei:20261029T190000,
 20261105T190000
RDATE;TZID=Asia/Taipei:20261029T190000
SUMMARY:""")
        starts = [event["start"].strftime("%m/%d") for event in self.parse(text)]
        self.assertEqual(starts[:3], ["10/29", "11/03", "11/05"])
        for excluded in ("10/27", "11/10", "11/17"):
            self.assertNotIn(excluded, starts)
        self.assertEqual(starts.count("10/29"), 1)

    def test_moved_and_cancelled_exceptions_override_series_in_any_order(self) -> None:
        exceptions = """BEGIN:VEVENT
UID:synthetic-class
RECURRENCE-ID;TZID=Asia/Taipei:20261027T190000
DTSTART;TZID=Asia/Taipei:20261028T180000
LOCATION:新測試教室
END:VEVENT
BEGIN:VEVENT
UID:synthetic-class
RECURRENCE-ID:20261103T110000Z
STATUS:CANCELLED
END:VEVENT
"""
        events = self.parse(self.SERIES.replace("BEGIN:VCALENDAR\n", "BEGIN:VCALENDAR\n" + exceptions))
        self.assertEqual(events[0]["start"], datetime(2026, 10, 28, 18, tzinfo=TAIPEI))
        self.assertEqual(events[0]["end"], datetime(2026, 10, 28, 20, tzinfo=TAIPEI))
        self.assertEqual(events[0]["location"], "新測試教室")
        self.assertEqual(events[0]["summary"], "竹韻社課（合成測試）")
        self.assertEqual(events[1]["start"], datetime(2026, 11, 10, 19, tzinfo=TAIPEI))
        self.assertEqual(len(events), 8)

    def test_moved_exception_can_enter_window_from_an_expired_original(self) -> None:
        text = self.SERIES.replace("COUNT=15", "COUNT=1").replace("END:VCALENDAR", """BEGIN:VEVENT
UID:synthetic-class
RECURRENCE-ID;TZID=Asia/Taipei:20260915T190000
DTSTART;TZID=Asia/Taipei:20261029T190000
END:VEVENT
END:VCALENDAR""")
        events = self.parse(text)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["start"], datetime(2026, 10, 29, 19, tzinfo=TAIPEI))

    def test_cancelled_series_and_admin_replacement_do_not_reappear(self) -> None:
        self.assertEqual(self.parse(self.SERIES.replace("SUMMARY:", "STATUS:CANCELLED\nSUMMARY:")), [])
        self.assertEqual(self.parse(self.SERIES.replace("竹韻社課（合成測試）", "很長的活動標題" * 30 + "幹部")), [])
        text = self.SERIES.replace("END:VCALENDAR", """BEGIN:VEVENT
UID:synthetic-class
RECURRENCE-ID;TZID=Asia/Taipei:20261027T190000
SUMMARY:社課幹部會議
END:VEVENT
END:VCALENDAR""")
        events = self.parse(text)
        self.assertEqual(events[0]["start"], datetime(2026, 11, 3, 19, tzinfo=TAIPEI))

    def test_utc_until_is_inclusive(self) -> None:
        text = self.SERIES.replace("COUNT=15", "UNTIL=20261103T110000Z")
        self.assertEqual([event["start"].day for event in self.parse(text)], [27, 3])

    def test_all_day_recurrence_until_and_default_one_day_duration(self) -> None:
        text = """BEGIN:VCALENDAR
BEGIN:VEVENT
UID:all-day
DTSTART;VALUE=DATE:20261020
RRULE:FREQ=DAILY;UNTIL=20261025
EXDATE;VALUE=DATE:20261023
SUMMARY:公開社課
END:VEVENT
END:VCALENDAR
"""
        events = self.parse(text)
        self.assertEqual([event["start"].day for event in events], [22, 24, 25])
        self.assertTrue(all(event["all_day"] for event in events))
        self.assertEqual(events[-1]["end"], datetime(2026, 10, 26, tzinfo=TAIPEI))

    def test_timezone_recurrence_preserves_wall_time_across_dst(self) -> None:
        text = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART;TZID=America/New_York:20261025T190000
DTEND;TZID=America/New_York:20261025T210000
RRULE:FREQ=WEEKLY;COUNT=3
SUMMARY:公開線上交流
END:VEVENT
END:VCALENDAR
"""
        events = self.parse(text)
        self.assertEqual([event["start"].strftime("%m/%d %H:%M") for event in events],
                         ["10/26 07:00", "11/02 08:00", "11/09 08:00"])

    def test_ended_events_are_excluded_but_in_progress_events_remain(self) -> None:
        text = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART;TZID=Asia/Taipei:20261021T190000
DTEND;TZID=Asia/Taipei:20261021T210000
SUMMARY:昨日活動
END:VEVENT
BEGIN:VEVENT
DTSTART;TZID=Asia/Taipei:20261022T110000
DTEND;TZID=Asia/Taipei:20261022T130000
SUMMARY:進行中的活動
END:VEVENT
END:VCALENDAR
"""
        self.assertEqual([event["summary"] for event in self.parse(text)], ["進行中的活動"])

    def test_bad_or_unsupported_series_does_not_hide_valid_events(self) -> None:
        for rule in ("FREQ=WEEKLY;INTERVAL=0", "FREQ=SECONDLY", "FREQ=INVALID"):
            with self.subTest(rule=rule):
                bad = self.SERIES.replace("UID:synthetic-class", "UID:bad").replace(
                    "FREQ=WEEKLY;COUNT=15;BYDAY=TU", rule
                )
                with self.assertLogs("bamboo-website-agent", level="WARNING"):
                    events = self.parse(bad + self.SERIES)
                self.assertEqual(len(events), 9)

    def test_unsupported_range_exception_does_not_show_obsolete_schedule(self) -> None:
        text = self.SERIES.replace("END:VCALENDAR", """BEGIN:VEVENT
UID:synthetic-class
RECURRENCE-ID;TZID=Asia/Taipei;RANGE=THISANDFUTURE:20261027T190000
DTSTART;TZID=Asia/Taipei:20261028T190000
END:VEVENT
END:VCALENDAR""")
        with self.assertLogs("bamboo-website-agent", level="WARNING"):
            self.assertEqual(self.parse(text), [])

    def test_infinite_recurrence_is_bounded_and_alarm_fields_are_not_exposed(self) -> None:
        text = self.SERIES.replace("FREQ=WEEKLY;COUNT=15;BYDAY=TU", "FREQ=DAILY").replace(
            "END:VEVENT", """DESCRIPTION:This synthetic description must never enter answers.
BEGIN:VALARM
SUMMARY:Alarm title must not replace the public event
END:VALARM
END:VEVENT"""
        )
        events = self.parse(text)
        self.assertEqual(len(events), 128)
        self.assertTrue(all(event["summary"] == "竹韻社課（合成測試）" for event in events))
        self.assertEqual(set(events[0]), {"summary", "location", "start", "end", "all_day"})

    def test_invalid_response_is_not_mistaken_for_an_empty_calendar(self) -> None:
        for text in ("<html>Unavailable</html>", self.SERIES.replace("END:VCALENDAR", "")):
            with self.subTest(text=text[:20]), self.assertRaisesRegex(ValueError, "Calendar response"):
                self.parse(text)
        self.assertEqual(self.parse("BEGIN:VCALENDAR\nEND:VCALENDAR\n"), [])


class ProfileConfigTests(unittest.TestCase):
    def test_profile_routes_to_gateway_and_stays_isolated(self) -> None:
        import hermes_yaml as yaml

        config = yaml.safe_load((Path(__file__).parent / "hermes-config.yaml").read_text())
        # Primary route: the local AI gateway's sky-fast alias.
        gateway = config["providers"]["ai-gateway-sky-fast"]
        self.assertEqual(config["model"]["default"], "sky-fast")
        self.assertEqual(config["model"]["provider"], "custom:ai-gateway-sky-fast")
        self.assertEqual(gateway["api"], "http://127.0.0.1:8317/v1")
        self.assertEqual(gateway["key_env"], "AI_GATEWAY_API_KEY")
        self.assertEqual(gateway["extra_body"]["max_tokens"], 250)
        self.assertGreaterEqual(config["model"]["context_length"], 64000)
        self.assertEqual(config["agent"]["reasoning_effort"], "none")
        self.assertEqual(config["agent"]["auto_recovery_cycles"], 0)
        self.assertNotIn("ollama-qwen35-local", config["providers"])
        self.assertEqual(config["fallback_providers"], [])
        self.assertFalse(config["providers"]["ai-kot-gg-luna"]["enabled"])
        self.assertTrue(config["gateway"]["standalone"])
        self.assertEqual(config["gateway"]["api_server"]["max_concurrent_runs"], 1)
        self.assertEqual(config["platform_toolsets"]["api_server"], ["no_mcp"])
        self.assertFalse(config["memory"]["memory_enabled"])
        self.assertFalse(config["memory"]["user_profile_enabled"])


if __name__ == "__main__":
    unittest.main()
