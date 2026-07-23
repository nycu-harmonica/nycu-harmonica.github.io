#!/usr/bin/env python3
"""Install the isolated website Hermes profile and launchd facade."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import plistlib
import secrets
import shutil
import subprocess
import sys
import time


PROFILE = Path.home() / ".hermes/profiles/website"
RUNTIME = PROFILE / "website-agent-runtime"
PUBLIC_SNAPSHOT = PROFILE / "public-site"
LAUNCH_AGENT = Path.home() / "Library/LaunchAgents/club.nycu.harmonica.website-agent.plist"
LABEL = "club.nycu.harmonica.website-agent"
HERMES_LAUNCH_AGENT = Path.home() / "Library/LaunchAgents/club.nycu.harmonica.website-hermes.plist"
HERMES_LABEL = "club.nycu.harmonica.website-hermes"
LEGACY_HERMES_LABEL = "ai.hermes.gateway-website"
LEGACY_HERMES_PLIST = Path.home() / "Library/LaunchAgents/ai.hermes.gateway-website.plist"


def update_env(path: Path, values: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    remaining = dict(values)
    output: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else ""
        if key in remaining:
            output.append(f"{key}={remaining.pop(key)}")
        else:
            output.append(line)
    if output and output[-1] != "":
        output.append("")
    output.extend(f"{key}={value}" for key, value in remaining.items())
    path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    path.chmod(0o600)


def read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith(key + "="):
            continue
        value = line.split("=", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value
    return ""


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True)


def reload_launch_agent(uid: str, label: str, plist: Path) -> None:
    run("launchctl", "bootout", f"gui/{uid}/{label}", check=False)
    result: subprocess.CompletedProcess[str] | None = None
    for _attempt in range(3):
        result = run("launchctl", "bootstrap", f"gui/{uid}", str(plist), check=False)
        if result.returncode == 0:
            break
        time.sleep(1)
    if result is None or result.returncode != 0:
        raise SystemExit(f"Could not bootstrap {label}")
    run("launchctl", "kickstart", "-k", f"gui/{uid}/{label}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-start", action="store_true", help="Install files without starting services")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    site_root = here.parents[1]
    PROFILE.mkdir(parents=True, exist_ok=True)
    (PROFILE / "logs").mkdir(parents=True, exist_ok=True)

    # LaunchAgents cannot read ~/Documents without interactive TCC approval.
    # Install only the explicitly public files required by the facade.
    RUNTIME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(here / "server.py", RUNTIME / "server.py")
    shutil.copyfile(here / "system-prompt.txt", RUNTIME / "system-prompt.txt")
    if PUBLIC_SNAPSHOT.exists():
        shutil.rmtree(PUBLIC_SNAPSHOT)
    for relative in ("content/_index.md", "content/about.md", "scripts/sources.json"):
        destination = PUBLIC_SNAPSHOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(site_root / relative, destination)
    generated = PUBLIC_SNAPSHOT / "data/generated"
    generated.mkdir(parents=True, exist_ok=True)
    for filename in ("officers.json", "links.json"):
        shutil.copyfile(site_root / "data/generated" / filename, generated / filename)

    key_file = PROFILE / ".website-api-key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32) + "\n", encoding="utf-8")
        key_file.chmod(0o600)

    ai_kot_key = os.getenv("AI_KOT_GG_API_KEY", "").strip()
    if not ai_kot_key:
        ai_kot_key = read_env_value(Path.home() / ".hermes/profiles/bamboo/.env", "AI_KOT_GG_API_KEY")
    if not ai_kot_key:
        raise SystemExit("AI_KOT_GG_API_KEY is required for the Luna 5.6 website profile")

    shutil.copyfile(here / "hermes-config.yaml", PROFILE / "config.yaml")
    shutil.copyfile(here / "SOUL.md", PROFILE / "SOUL.md")
    update_env(
        PROFILE / ".env",
        {
            "AI_KOT_GG_API_KEY": ai_kot_key,
            "OLLAMA_API_KEY": "ollama",
            "API_SERVER_ENABLED": "true",
            "API_SERVER_HOST": "127.0.0.1",
            "API_SERVER_PORT": "8643",
            "API_SERVER_KEY": key_file.read_text(encoding="utf-8").strip(),
            "API_SERVER_MODEL_NAME": "website",
        },
    )

    logs = Path.home() / "Library/Logs"
    logs.mkdir(parents=True, exist_ok=True)
    hermes_root = Path.home() / ".hermes/hermes-agent"
    hermes_venv = hermes_root / "venv"
    hermes_plist = {
        "Label": HERMES_LABEL,
        "ProgramArguments": [
            str(hermes_venv / "bin/python"),
            "-m",
            "hermes_cli.main",
            "gateway",
            "run",
            "--replace",
        ],
        "WorkingDirectory": str(PROFILE),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "ProcessType": "Background",
        "EnvironmentVariables": {
            "HERMES_HOME": str(PROFILE),
            "VIRTUAL_ENV": str(hermes_venv),
            "PATH": ":".join(
                [
                    str(hermes_venv / "bin"),
                    str(hermes_root / "node_modules/.bin"),
                    "/opt/homebrew/bin",
                    str(Path.home() / ".local/bin"),
                    "/usr/local/bin",
                    "/usr/bin",
                    "/bin",
                    "/usr/sbin",
                    "/sbin",
                ]
            ),
        },
        "StandardOutPath": str(PROFILE / "logs/gateway.log"),
        "StandardErrorPath": str(PROFILE / "logs/gateway.error.log"),
    }
    HERMES_LAUNCH_AGENT.parent.mkdir(parents=True, exist_ok=True)
    with HERMES_LAUNCH_AGENT.open("wb") as handle:
        plistlib.dump(hermes_plist, handle, sort_keys=False)

    plist = {
        "Label": LABEL,
        "ProgramArguments": [str(Path(sys.executable).resolve()), str(RUNTIME / "server.py")],
        "WorkingDirectory": str(RUNTIME),
        "RunAtLoad": True,
        "KeepAlive": {"SuccessfulExit": False},
        "ProcessType": "Background",
        "EnvironmentVariables": {
            "HERMES_API_URL": "http://127.0.0.1:8643/v1/chat/completions",
            "HERMES_API_KEY_FILE": str(key_file),
            "SITE_ROOT": str(PUBLIC_SNAPSHOT),
            "SYSTEM_PROMPT_FILE": str(RUNTIME / "system-prompt.txt"),
            "ALLOWED_ORIGINS": "https://harmonica.nycu.club,http://127.0.0.1:1313,http://localhost:1313",
            "WEBSITE_AGENT_HOST": "127.0.0.1",
            "WEBSITE_AGENT_PORT": "8788",
        },
        "StandardOutPath": str(logs / f"{LABEL}.log"),
        "StandardErrorPath": str(logs / f"{LABEL}.error.log"),
    }
    LAUNCH_AGENT.parent.mkdir(parents=True, exist_ok=True)
    with LAUNCH_AGENT.open("wb") as handle:
        plistlib.dump(plist, handle, sort_keys=False)

    if args.no_start:
        return

    uid = str(os.getuid())
    run("launchctl", "bootout", f"gui/{uid}/{LEGACY_HERMES_LABEL}", check=False)
    if LEGACY_HERMES_PLIST.exists():
        LEGACY_HERMES_PLIST.unlink()
    reload_launch_agent(uid, HERMES_LABEL, HERMES_LAUNCH_AGENT)
    reload_launch_agent(uid, LABEL, LAUNCH_AGENT)


if __name__ == "__main__":
    main()
