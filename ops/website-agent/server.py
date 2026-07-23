#!/usr/bin/env python3
"""Narrow public facade for the Bamboo website Hermes profile.

The browser never receives the Hermes API key. This service accepts only a
bounded /ask request, builds context from explicitly public site sources, and
forwards one stateless turn to the localhost-only Hermes API server.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import re
import threading
import time
from typing import Any
from urllib import error, parse, request
from zoneinfo import ZoneInfo


LOG = logging.getLogger("bamboo-website-agent")
MAX_REQUEST_BYTES = 4096
MAX_QUESTION_CHARS = 500
MAX_HISTORY_MESSAGES = 3
MAX_HISTORY_CHARS = 1300
MAX_ANSWER_CHARS = 1400
MAX_CONTEXT_CHARS = 10_000
DEFAULT_SITE_URL = "https://harmonica.nycu.club/"
CALENDAR_ICS_URL = "https://calendar.google.com/calendar/ical/bmhc1968%40gmail.com/public/basic.ics"
TAIPEI = ZoneInfo("Asia/Taipei")
VISITOR_EVENT_EXCLUDES = ("幹部", "截止", "確認", "預備期", "彩排")


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    hermes_url: str
    hermes_key_file: Path
    site_root: Path
    system_prompt_file: Path
    allowed_origins: tuple[str, ...]
    per_ip_limit: int
    per_ip_window_seconds: int
    daily_limit: int
    request_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        here = Path(__file__).resolve().parent
        default_root = here.parents[1]
        origins = tuple(
            origin.strip().rstrip("/")
            for origin in os.getenv(
                "ALLOWED_ORIGINS",
                "https://harmonica.nycu.club,http://127.0.0.1:1313,http://localhost:1313",
            ).split(",")
            if origin.strip()
        )
        return cls(
            host=os.getenv("WEBSITE_AGENT_HOST", "127.0.0.1"),
            port=int(os.getenv("WEBSITE_AGENT_PORT", "8788")),
            hermes_url=os.getenv(
                "HERMES_API_URL", "http://127.0.0.1:8643/v1/chat/completions"
            ),
            hermes_key_file=Path(
                os.getenv(
                    "HERMES_API_KEY_FILE",
                    str(Path.home() / ".hermes/profiles/website/.website-api-key"),
                )
            ).expanduser(),
            site_root=Path(os.getenv("SITE_ROOT", str(default_root))).expanduser(),
            system_prompt_file=Path(
                os.getenv("SYSTEM_PROMPT_FILE", str(here / "system-prompt.txt"))
            ).expanduser(),
            allowed_origins=origins,
            per_ip_limit=int(os.getenv("PER_IP_LIMIT", "8")),
            per_ip_window_seconds=int(os.getenv("PER_IP_WINDOW_SECONDS", "600")),
            daily_limit=int(os.getenv("DAILY_LIMIT", "300")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "75")),
        )


class RequestLimiter:
    def __init__(self, per_ip_limit: int, window_seconds: int, daily_limit: int):
        self.per_ip_limit = per_ip_limit
        self.window_seconds = window_seconds
        self.daily_limit = daily_limit
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._day = date.today()
        self._daily_count = 0
        self._lock = threading.Lock()

    def allow(self, client_id: str, now: float | None = None) -> tuple[bool, str]:
        current = time.time() if now is None else now
        with self._lock:
            today = date.today()
            if today != self._day:
                self._day = today
                self._daily_count = 0
                self._requests.clear()
            if self._daily_count >= self.daily_limit:
                return False, "daily"
            recent = self._requests[client_id]
            cutoff = current - self.window_seconds
            while recent and recent[0] <= cutoff:
                recent.popleft()
            if len(recent) >= self.per_ip_limit:
                return False, "client"
            recent.append(current)
            self._daily_count += 1
            return True, "ok"


def normalise_history(value: Any) -> list[dict[str, str]]:
    """Accept only a short alternating text history from the public client."""
    if not isinstance(value, list):
        return []
    messages: list[dict[str, str]] = []
    total_chars = 0
    for item in value[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = re.sub(r"[\x00-\x1f\x7f]", " ", str(item.get("text", "")))
        text = re.sub(r"\s+", " ", text).strip()[:MAX_QUESTION_CHARS]
        if not text:
            continue
        remaining = MAX_HISTORY_CHARS - total_chars
        if remaining <= 0:
            break
        text = text[:remaining]
        messages.append({"role": role, "content": text})
        total_chars += len(text)
    return messages


def _unescape_ics_text(value: str) -> str:
    return (
        value.replace("\\n", " ")
        .replace("\\N", " ")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
        .strip()
    )


def _parse_ics_datetime(property_name: str, value: str) -> tuple[datetime, bool]:
    params = property_name.split(";")[1:]
    if "VALUE=DATE" in params:
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=TAIPEI), True
    if value.endswith("Z"):
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        return parsed.astimezone(TAIPEI), False
    parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
    return parsed.replace(tzinfo=TAIPEI), False


def parse_calendar_events(ics_text: str, now: datetime | None = None) -> list[dict[str, Any]]:
    """Parse only the public Calendar fields needed for visitor-facing answers."""
    unfolded: list[str] = []
    for raw_line in ics_text.replace("\r\n", "\n").split("\n"):
        if raw_line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += raw_line[1:]
        else:
            unfolded.append(raw_line)

    current = (now or datetime.now(TAIPEI)).astimezone(TAIPEI)
    cutoff = current - timedelta(days=1)
    events: list[dict[str, Any]] = []
    block: dict[str, tuple[str, str]] | None = None
    for line in unfolded:
        if line == "BEGIN:VEVENT":
            block = {}
            continue
        if line == "END:VEVENT":
            if block is not None:
                try:
                    start_name, start_value = block["DTSTART"]
                    end_name, end_value = block.get("DTEND", block["DTSTART"])
                    start, all_day = _parse_ics_datetime(start_name, start_value)
                    end, _ = _parse_ics_datetime(end_name, end_value)
                    all_day = all_day or (
                        start.time().isoformat() == "00:00:00"
                        and end.time().isoformat() == "00:00:00"
                        and end - start >= timedelta(days=1)
                    )
                    summary = _unescape_ics_text(block.get("SUMMARY", ("", ""))[1])
                    location = _unescape_ics_text(block.get("LOCATION", ("", ""))[1])
                    status = block.get("STATUS", ("", "CONFIRMED"))[1]
                except (KeyError, ValueError):
                    block = None
                    continue
                if (
                    status == "CONFIRMED"
                    and summary
                    and end >= cutoff
                    and not any(word in summary for word in VISITOR_EVENT_EXCLUDES)
                ):
                    events.append(
                        {
                            "summary": summary[:160],
                            "location": location[:220],
                            "start": start,
                            "end": end,
                            "all_day": all_day,
                        }
                    )
            block = None
            continue
        if block is None or ":" not in line:
            continue
        name, value = line.split(":", 1)
        key = name.split(";", 1)[0]
        if key in {"DTSTART", "DTEND", "SUMMARY", "LOCATION", "STATUS"}:
            block[key] = (name, value)
    return sorted(events, key=lambda event: event["start"])[:8]


def format_public_event(event: dict[str, Any]) -> str:
    start: datetime = event["start"]
    end: datetime = event["end"]
    if event["all_day"]:
        final_day = (end - timedelta(days=1)).date()
        when = f"{start.month}/{start.day}（全天）"
        if final_day > start.date():
            when = f"{start.month}/{start.day} 至 {final_day.month}/{final_day.day}（全天）"
    else:
        when = f"{start.month}/{start.day} {start:%H:%M}–{end:%H:%M}"
    summary = str(event["summary"]).replace("｜", "：")
    location = str(event.get("location") or "待公告").replace("｜", "、")
    return f"{when}｜{summary}｜地點：{location}"


def format_public_event_list(events: list[dict[str, Any]]) -> str:
    blocks = []
    for event in events:
        when, summary, location = format_public_event(event).split("｜", 2)
        blocks.append(f"• {when}\n  {summary}\n  {location}")
    return "\n\n".join(blocks)


class KnowledgeBase:
    """Build a small context using public site files and public Sheet tabs."""

    HEADER_ALIASES = {
        "排序": "order",
        "職稱": "role",
        "姓名": "name",
        "狀態": "status",
        "名稱": "label",
        "網址": "url",
        "顯示位置": "show_in",
        "圖示": "icon",
    }

    def __init__(self, site_root: Path, cache_seconds: int = 60):
        self.site_root = site_root
        self.cache_seconds = cache_seconds
        self._value = ""
        self._expires_at = 0.0
        self._lock = threading.Lock()
        self._events: list[dict[str, Any]] = []
        self._links: dict[str, dict[str, Any]] = {}

    def get(self) -> str:
        now = time.monotonic()
        with self._lock:
            if self._value and now < self._expires_at:
                return self._value
            self._value = self._build()[:MAX_CONTEXT_CHARS]
            self._expires_at = now + self.cache_seconds
            return self._value

    @staticmethod
    def _strip_front_matter(text: str) -> str:
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end >= 0:
                return text[end + 5 :].strip()
        return text.strip()

    def _read_public_text(self, relative_path: str) -> str:
        path = (self.site_root / relative_path).resolve()
        root = self.site_root.resolve()
        if root not in path.parents:
            raise ValueError("public context path escaped the site root")
        return self._strip_front_matter(path.read_text(encoding="utf-8"))

    @staticmethod
    def _normalize_header(value: str) -> str:
        raw = value.strip().lstrip("\ufeff")
        key = raw.lower().replace(" ", "_").replace("-", "_")
        return KnowledgeBase.HEADER_ALIASES.get(raw, key)

    @staticmethod
    def _cell_text(cell: Any) -> str:
        if not isinstance(cell, dict) or cell.get("v") is None:
            return ""
        value = cell.get("f") if isinstance(cell.get("f"), str) else cell.get("v")
        return re.sub(r"\s+", " ", str(value)).strip()

    def _fetch_sheet_rows(self, tab: str) -> list[dict[str, str]]:
        source_path = self.site_root / "scripts/sources.json"
        sources = json.loads(source_path.read_text(encoding="utf-8"))
        sheet_id = str(sources["sheet_id"])
        gid = str(sources["tabs"][tab]["gid"])
        query = parse.urlencode({"gid": gid, "tqx": "out:json", "headers": "0"})
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?{query}"
        req = request.Request(url, headers={"User-Agent": "BambooWebsiteAgent/1.0"})
        with request.urlopen(req, timeout=6) as response:
            body = response.read(1_000_000).decode("utf-8")
        match = re.search(r"setResponse\((.*)\);?\s*$", body, re.DOTALL)
        if not match:
            raise ValueError("unexpected Google Sheet response")
        payload = json.loads(match.group(1))
        raw_rows = payload.get("table", {}).get("rows", [])
        if not raw_rows or len(raw_rows) > 501:
            raise ValueError("invalid Google Sheet row count")
        header_cells = raw_rows[0].get("c") or []
        headers = [self._normalize_header(self._cell_text(cell)) for cell in header_cells]
        rows: list[dict[str, str]] = []
        for raw_row in raw_rows[1:]:
            cells = raw_row.get("c") or []
            row = {
                header: self._cell_text(cells[index] if index < len(cells) else None)
                for index, header in enumerate(headers)
                if header
            }
            if any(row.values()):
                rows.append(row)
        return rows

    def _fallback_json(self, filename: str) -> list[dict[str, Any]]:
        path = self.site_root / "data/generated" / filename
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []

    def _public_rows(self, tab: str, fallback_file: str) -> list[dict[str, Any]]:
        try:
            rows = self._fetch_sheet_rows(tab)
            return [
                row
                for row in rows
                if row.get("status", "").strip().lower()
                not in {"draft", "草稿", "hidden", "隱藏"}
            ]
        except Exception as exc:
            LOG.warning("public Sheet %s unavailable; using repo fallback: %s", tab, exc)
            return self._fallback_json(fallback_file)

    def _fetch_calendar_events(self) -> list[dict[str, Any]]:
        req = request.Request(CALENDAR_ICS_URL, headers={"User-Agent": "BambooWebsiteAgent/1.0"})
        with request.urlopen(req, timeout=8) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("public Calendar response too large")
        return parse_calendar_events(raw.decode("utf-8"))

    def _source(self, key: str, fallback_label: str, fallback_url: str) -> dict[str, str]:
        link = self._links.get(key, {})
        url = str(link.get("url", ""))
        return {
            "label": str(link.get("label") or fallback_label),
            "url": url if url.startswith("https://") else fallback_url,
        }

    def quick_answer(self, question: str) -> tuple[str, list[dict[str, str]]] | None:
        self.get()
        compact = re.sub(r"\s+", "", question)
        instagram = self._source(
            "instagram", "Instagram @nycu_harmonica", "https://www.instagram.com/nycu_harmonica/"
        )
        discord = self._source("discord", "Discord 社群", "https://discord.gg/uEQDCbnY8P")
        calendar = {"label": "社團公開行事曆", "url": DEFAULT_SITE_URL + "#calendar"}

        if any(word in compact for word in ("加入", "入社", "新生", "社員")):
            return (
                "可以直接點下方「Discord 社群」加入竹韻；零基礎也歡迎。"
                "加入後可收到招生、社課與活動的第一手消息，公開公告也會同步在 Instagram。",
                [discord, instagram],
            )
        if "社課" in compact and any(word in compact for word in ("時間", "地點", "哪裡", "何時")):
            return (
                "目前尚未公布固定社課時間與地點，這是目前公開資料的真實狀態。"
                "建議先加入下方 Discord 社群；正式社課公告會同步在 Instagram 與官網行事曆。",
                [discord, instagram, calendar],
            )
        if "活動" in compact and any(word in compact for word in ("最近", "近期", "什麼", "哪些", "有沒有")):
            if self._events:
                return (
                    "接下來有這些公開活動：\n\n"
                    + format_public_event_list(self._events[:4])
                    + "\n\n時間與地點若有異動，以公開行事曆為準。",
                    [calendar],
                )
            return ("目前無法讀取近期活動清單，請直接查看下方社團公開行事曆。", [calendar])
        return None

    def _build(self) -> str:
        sections = [
            "【社團與網站介紹】\n" + self._read_public_text("content/_index.md"),
            "【關於竹韻】\n" + self._read_public_text("content/about.md"),
        ]

        officers = self._public_rows("officers", "officers.json")
        officer_lines = [
            f"- {str(row.get('role', '')).strip()}：{str(row.get('name', '')).strip()}"
            for row in officers[:30]
            if row.get("role") and row.get("name")
        ]
        if officer_lines:
            sections.append("【公開幹部名單】\n" + "\n".join(officer_lines))

        links = self._public_rows("links", "links.json")
        self._links = {str(row.get("key", "")): row for row in links if row.get("key")}
        link_lines = [
            f"- {str(row.get('label', '')).strip()}：{str(row.get('url', '')).strip()}"
            for row in links[:30]
            if row.get("label") and str(row.get("url", "")).startswith(("https://", "mailto:"))
        ]
        if link_lines:
            sections.append("【官方公開連結】\n" + "\n".join(link_lines))

        try:
            self._events = self._fetch_calendar_events()
        except Exception as exc:
            LOG.warning("public Calendar unavailable; keeping cached events: %s", exc)
        if self._events:
            sections.append(
                "【近期公開活動】\n"
                + "\n".join(f"- {format_public_event(event)}" for event in self._events)
            )

        sections.append(
            "【固定入口】\n"
            f"- 官網：{DEFAULT_SITE_URL}\n"
            f"- 公開活動行事曆：{DEFAULT_SITE_URL}#calendar\n"
            f"- 加入與聯絡：{DEFAULT_SITE_URL}about/\n"
            "- 活動與社課的日期、時間、地點以公開行事曆及 Instagram 最新公告為準。"
        )
        return "\n\n".join(sections)


class HermesClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _api_key(self) -> str:
        value = self.settings.hermes_key_file.read_text(encoding="utf-8").strip()
        if len(value) < 16:
            raise RuntimeError("Hermes API key is missing or invalid")
        return value

    def ask(
        self,
        question: str,
        history: list[dict[str, str]],
        system_prompt: str,
        context: str,
    ) -> str:
        payload = {
            "model": "website",
            "stream": False,
            "temperature": 0.2,
            "max_tokens": 250,
            "messages": [
                {"role": "system", "content": system_prompt + "\n\n" + context},
                *history,
                {"role": "user", "content": question},
            ],
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            self.settings.hermes_url,
            data=body,
            method="POST",
            headers={
                "Authorization": "Bearer " + self._api_key(),
                "Content-Type": "application/json",
                "User-Agent": "BambooWebsiteFacade/1.0",
            },
        )
        with request.urlopen(req, timeout=self.settings.request_timeout_seconds) as response:
            result = json.loads(response.read(2_000_000).decode("utf-8"))
        choices = result.get("choices") or []
        answer = choices[0].get("message", {}).get("content", "") if choices else ""
        answer = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(answer)).strip()
        if not answer:
            raise RuntimeError("Hermes returned an empty answer")
        return answer[:MAX_ANSWER_CHARS]

    def healthy(self) -> bool:
        health_url = self.settings.hermes_url.split("/v1/", 1)[0] + "/health"
        try:
            with request.urlopen(health_url, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False


class WebsiteAgentServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, settings: Settings):
        self.settings = settings
        self.limiter = RequestLimiter(
            settings.per_ip_limit,
            settings.per_ip_window_seconds,
            settings.daily_limit,
        )
        self.knowledge = KnowledgeBase(settings.site_root, cache_seconds=300)
        self.hermes = HermesClient(settings)
        self.system_prompt = settings.system_prompt_file.read_text(encoding="utf-8").strip()
        self.inference_lock = threading.Lock()
        super().__init__((settings.host, settings.port), WebsiteAgentHandler)
        # Pay the public Sheet fetch cost at service startup instead of on the
        # first visitor request. Failures already fall back to committed JSON.
        self.knowledge.get()


class WebsiteAgentHandler(BaseHTTPRequestHandler):
    server: WebsiteAgentServer
    protocol_version = "HTTP/1.1"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(90)
        self.close_connection = True

    def log_message(self, format_string: str, *args: Any) -> None:
        LOG.info("%s %s", self.address_string(), format_string % args)

    def _origin(self) -> str:
        return self.headers.get("Origin", "").strip().rstrip("/")

    def _origin_allowed(self) -> bool:
        return self._origin() in self.server.settings.allowed_origins

    def _client_id(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[-1].strip()[:128]
        return self.client_address[0]

    def _send_json(self, status: int, payload: dict[str, Any], allow_cors: bool = True) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Connection", "close")
        if allow_cors and self._origin_allowed():
            self.send_header("Access-Control-Allow-Origin", self._origin())
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path != "/ask" or not self._origin_allowed():
            self._send_json(403, {"error": "origin_not_allowed"}, allow_cors=False)
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self._origin())
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Content-Length", "0")
        self.send_header("Vary", "Origin")
        self.send_header("Connection", "close")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._send_json(404, {"error": "not_found"}, allow_cors=False)
            return
        healthy = self.server.hermes.healthy()
        self._send_json(
            200 if healthy else 503,
            {"status": "ok" if healthy else "degraded", "agent": healthy},
            allow_cors=False,
        )

    def do_POST(self) -> None:  # noqa: N802
        started = time.monotonic()
        if self.path != "/ask":
            self._send_json(404, {"error": "not_found"}, allow_cors=False)
            return
        if not self._origin_allowed():
            self._send_json(403, {"error": "origin_not_allowed"}, allow_cors=False)
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "json_required"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length < 1 or length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "request_too_large"})
            return
        allowed, reason = self.server.limiter.allow(self._client_id())
        if not allowed:
            self._send_json(
                429,
                {
                    "error": "rate_limited",
                    "message": "今天的詢問量已達上限，請稍後再試。"
                    if reason == "daily"
                    else "詢問得太快了，請稍後再試。",
                },
            )
            return
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            question = re.sub(r"[\x00-\x1f\x7f]", " ", str(data.get("question", "")))
            question = re.sub(r"\s+", " ", question).strip()
            history = normalise_history(data.get("history"))
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not question or len(question) > MAX_QUESTION_CHARS:
            self._send_json(
                400,
                {"error": "invalid_question", "message": "問題需介於 1 到 500 個字之間。"},
            )
            return
        quick_answer = self.server.knowledge.quick_answer(question)
        if quick_answer is not None:
            answer, sources = quick_answer
            LOG.info("public-data shortcut completed in %.2fs", time.monotonic() - started)
            self._send_json(200, {"answer": answer, "sources": sources})
            return
        if not self.server.inference_lock.acquire(blocking=False):
            self._send_json(
                429,
                {"error": "busy", "message": "目前有人正在詢問，請稍後再試。"},
            )
            return
        try:
            answer = self.server.hermes.ask(
                question,
                history,
                self.server.system_prompt,
                self.server.knowledge.get(),
            )
        except (error.URLError, TimeoutError, RuntimeError, OSError, ValueError) as exc:
            LOG.warning("agent request failed after %.2fs: %s", time.monotonic() - started, exc)
            self._send_json(
                503,
                {
                    "error": "agent_unavailable",
                    "message": "竹韻問答目前暫時無法使用，請查看官網行事曆或 Instagram。",
                },
            )
            return
        finally:
            self.server.inference_lock.release()
        LOG.info("agent request completed in %.2fs", time.monotonic() - started)
        self._send_json(
            200,
            {
                "answer": answer,
                "sources": [
                    {"label": "社團行事曆", "url": DEFAULT_SITE_URL + "#calendar"},
                    {"label": "關於我們", "url": DEFAULT_SITE_URL + "about/"},
                ],
            },
        )


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings.from_env()
    server = WebsiteAgentServer(settings)
    LOG.info("website agent facade listening on http://%s:%d", settings.host, settings.port)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
