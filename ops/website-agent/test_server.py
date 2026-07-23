#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from server import KnowledgeBase, RequestLimiter, normalise_history


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
                json.dumps([{"label": "Instagram", "url": "https://example.com/"}]),
                encoding="utf-8",
            )
            (root / "scripts/sources.json").write_text(
                json.dumps({"sheet_id": "public", "tabs": {"officers": {"gid": "1"}, "links": {"gid": "2"}}}),
                encoding="utf-8",
            )
            knowledge = KnowledgeBase(root)
            with mock.patch.object(knowledge, "_fetch_sheet_rows", side_effect=OSError("offline")):
                context = knowledge.get()
            self.assertIn("公開首頁", context)
            self.assertIn("社長：Sky", context)
            self.assertIn("Instagram：https://example.com/", context)
            self.assertNotIn("private", context)


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
