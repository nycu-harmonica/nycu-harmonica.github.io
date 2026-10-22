#!/usr/bin/env python3
"""Install the isolated website Hermes profile and launchd facade."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import secrets
import shutil
import subprocess
import sys
import time
from urllib import error, request


PROFILE = Path.home() / ".hermes/profiles/website"
RUNTIME = PROFILE / "website-agent-runtime"
PUBLIC_SNAPSHOT = PROFILE / "public-site"
LAUNCH_AGENT = Path.home() / "Library/LaunchAgents/club.nycu.harmonica.website-agent.plist"
LABEL = "club.nycu.harmonica.website-agent"
HERMES_LAUNCH_AGENT = Path.home() / "Library/LaunchAgents/club.nycu.harmonica.website-hermes.plist"
HERMES_LABEL = "club.nycu.harmonica.website-hermes"
LEGACY_HERMES_LABEL = "ai.hermes.gateway-website"
LEGACY_HERMES_PLIST = Path.home() / "Library/LaunchAgents/ai.hermes.gateway-website.plist"
OLLAMA_LABEL = "club.nycu.harmonica.website-ollama"
OLLAMA_LAUNCH_AGENT = Path.home() / f"Library/LaunchAgents/{OLLAMA_LABEL}.plist"
LOCAL_MODEL = "qwen3.5:9b"
LOCAL_CONTEXT = 65536


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


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True)


def local_model_preflight() -> str:
    """Check an already installed model; never pull one or acquire credentials."""
    binary = shutil.which("ollama")
    if not binary:
        raise SystemExit("An existing Ollama installation with qwen3.5:9b is required.")
    for port in (11435, 11434):
        req = request.Request(
            f"http://127.0.0.1:{port}/api/show",
            data=json.dumps({"model": LOCAL_MODEL}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with request.urlopen(req, timeout=5) as response:
                metadata = json.load(response)
        except (error.URLError, TimeoutError, OSError, ValueError):
            continue
        info = metadata.get("model_info", {})
        # A model-level num_ctx wins over the service default. Reject a changed
        # alias that would silently shrink or greatly enlarge the allocation.
        overrides = [line.split()[1] for line in metadata.get("parameters", "").splitlines()
                     if len(line.split()) >= 2 and line.split()[0] == "num_ctx"]
        if (info.get("general.architecture") == "qwen35"
                and info.get("qwen35.context_length", 0) >= LOCAL_CONTEXT
                and 0 < info.get("general.parameter_count", 0) <= 10_000_000_000
                and metadata.get("details", {}).get("quantization_level") == "Q4_K_M"
                and all(value == str(LOCAL_CONTEXT) for value in overrides)
                and "completion" in metadata.get("capabilities", [])):
            return binary
        raise SystemExit(
            "The existing qwen3.5:9b must be Q4_K_M, genuinely support at least 65,536 tokens, "
            "and have no conflicting num_ctx override."
        )
    raise SystemExit("Start the existing local Ollama with qwen3.5:9b before installing; no model is downloaded.")


def ollama_service(binary: str) -> dict:
    return {
        "Label": OLLAMA_LABEL,
        "ProgramArguments": [binary, "serve"],
        "WorkingDirectory": str(RUNTIME),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "ProcessType": "Background",
        "EnvironmentVariables": {
            "OLLAMA_HOST": "127.0.0.1:11435",
            "OLLAMA_MODELS": str(Path.home() / ".ollama/models"),
            "OLLAMA_FLASH_ATTENTION": "1",
            "OLLAMA_KV_CACHE_TYPE": "q4_0",
            "OLLAMA_CONTEXT_LENGTH": str(LOCAL_CONTEXT),
            "OLLAMA_NUM_PARALLEL": "1",
            "OLLAMA_MAX_LOADED_MODELS": "1",
            "OLLAMA_MAX_QUEUE": "1",
            "OLLAMA_KEEP_ALIVE": "30s",
            "OLLAMA_LOAD_TIMEOUT": "45s",
            "OLLAMA_NO_CLOUD": "1",
            "OLLAMA_NOPRUNE": "1",
        },
        "StandardOutPath": str(PROFILE / "logs/ollama.log"),
        "StandardErrorPath": str(PROFILE / "logs/ollama.error.log"),
    }


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
    # RunAtLoad already starts it; do not kill a service that just bootstrapped.
    run("launchctl", "kickstart", f"gui/{uid}/{label}")


def main() -> None:
    # Fail before touching profiles, keys, snapshots or LaunchAgents.
    if sys.version_info < (3, 11):
        raise SystemExit("Python >= 3.11 is required. Run with ~/.hermes/bamboo-runtime/bin/python.")
    try:
        import dateutil.rrule  # noqa: F401
    except ImportError:
        raise SystemExit(
            "python-dateutil is required in the selected Python environment. "
            "Use ~/.hermes/bamboo-runtime/bin/python with its PM-managed dependencies."
        ) from None
    hermes_spec = importlib.util.find_spec("hermes_cli")
    if hermes_spec is None or not hermes_spec.origin:
        raise SystemExit("The selected Python must have Hermes installed; use ~/.hermes/bamboo-runtime/bin/python.")
    hermes_root = Path(hermes_spec.origin).parent.parent
    hermes_python = Path(sys.executable)
    hermes_venv = hermes_python.parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-start", action="store_true", help="Install files without starting services")
    args = parser.parse_args()
    ollama_binary = local_model_preflight()

    here = Path(__file__).resolve().parent
    site_root = here.parents[1]
    PROFILE.mkdir(parents=True, exist_ok=True)
    PROFILE.chmod(0o700)
    (PROFILE / "logs").mkdir(parents=True, exist_ok=True)

    # LaunchAgents cannot read ~/Documents without interactive TCC approval.
    # Install only the explicitly public files required by the facade.
    RUNTIME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(here / "server.py", RUNTIME / "server.py")
    shutil.copyfile(here / "system-prompt.txt", RUNTIME / "system-prompt.txt")
    if PUBLIC_SNAPSHOT.exists():
        shutil.rmtree(PUBLIC_SNAPSHOT)
    for relative in ("content/_index.md", "content/about.md", "hugo.toml", "scripts/sources.json"):
        destination = PUBLIC_SNAPSHOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(site_root / relative, destination)
    generated = PUBLIC_SNAPSHOT / "data/generated"
    generated.mkdir(parents=True, exist_ok=True)
    for filename in ("links.json",):
        shutil.copyfile(site_root / "data/generated" / filename, generated / filename)

    key_file = PROFILE / ".website-api-key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32) + "\n", encoding="utf-8")
        key_file.chmod(0o600)

    shutil.copyfile(here / "hermes-config.yaml", PROFILE / "config.yaml")
    (PROFILE / "config.yaml").chmod(0o600)
    shutil.copyfile(here / "SOUL.md", PROFILE / "SOUL.md")
    update_env(
        PROFILE / ".env",
        {
            # Leave the disabled remote provider's existing key untouched.
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
    hermes_plist = {
        "Label": HERMES_LABEL,
        "ProgramArguments": [
            str(hermes_python),
            "-m",
            "hermes_cli.main",
            "gateway",
            "run",
            "--replace",
            "--external-supervisor",
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
    with OLLAMA_LAUNCH_AGENT.open("wb") as handle:
        plistlib.dump(ollama_service(ollama_binary), handle, sort_keys=False)

    plist = {
        "Label": LABEL,
        # Keep the venv interpreter path: resolving its symlink loses installed dependencies.
        "ProgramArguments": [sys.executable, str(RUNTIME / "server.py")],
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
    reload_launch_agent(uid, OLLAMA_LABEL, OLLAMA_LAUNCH_AGENT)
    reload_launch_agent(uid, HERMES_LABEL, HERMES_LAUNCH_AGENT)
    reload_launch_agent(uid, LABEL, LAUNCH_AGENT)


if __name__ == "__main__":
    main()
