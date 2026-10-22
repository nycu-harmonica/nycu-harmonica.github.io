#!/usr/bin/env python3
"""Installer preflight tests; never install files or access a real profile."""

import builtins
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import install


class ProviderKeyTests(unittest.TestCase):
    def test_local_reinstall_preserves_disabled_remote_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile_env = Path(directory) / "website.env"
            profile_env.write_text('AI_KOT_GG_API_KEY="website-test-key"\nAPI_SERVER_PORT=1234\n')
            install.update_env(profile_env, {"API_SERVER_PORT": "8643", "OLLAMA_API_KEY": "ollama"})
            self.assertIn('AI_KOT_GG_API_KEY="website-test-key"\n', profile_env.read_text())
            self.assertIn("API_SERVER_PORT=8643\n", profile_env.read_text())
            self.assertEqual(profile_env.stat().st_mode & 0o777, 0o600)


class LocalModelPreflightTests(unittest.TestCase):
    def test_missing_binary_does_not_contact_or_pull_models(self) -> None:
        with mock.patch.object(install.shutil, "which", return_value=None), mock.patch.object(
            install.request, "urlopen"
        ) as urlopen:
            with self.assertRaisesRegex(SystemExit, "existing Ollama"):
                install.local_model_preflight()
        urlopen.assert_not_called()

    def test_checks_actual_architecture_and_context_metadata(self) -> None:
        for architecture, context, override, quant, valid in (
            ("qwen35", 262144, "", "Q4_K_M", True),
            ("qwen35", 32768, "", "Q4_K_M", False),
            ("qwen3", 262144, "", "Q4_K_M", False),
            ("qwen35", 262144, "num_ctx 8192", "Q4_K_M", False),
            ("qwen35", 262144, "num_ctx 262144", "Q4_K_M", False),
            ("qwen35", 262144, "", "F16", False),
        ):
            with self.subTest(architecture=architecture, context=context, override=override, quant=quant):
                payload = {"model_info": {"general.architecture": architecture,
                           "qwen35.context_length": context, "general.parameter_count": 9653104368},
                           "details": {"quantization_level": quant},
                           "parameters": override, "capabilities": ["completion"]}
                with mock.patch.object(install.shutil, "which", return_value="/test/ollama"), mock.patch.object(
                    install.request, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())
                ):
                    if valid:
                        self.assertEqual(install.local_model_preflight(), "/test/ollama")
                    else:
                        with self.assertRaisesRegex(SystemExit, "genuinely support"):
                            install.local_model_preflight()


class InstallerPreflightTests(unittest.TestCase):
    def test_missing_local_model_exits_before_profile_changes(self) -> None:
        with mock.patch.object(install.sys, "argv", ["install.py"]), mock.patch.object(
            install, "local_model_preflight", side_effect=SystemExit("missing local model")
        ), mock.patch.object(install.Path, "mkdir") as mkdir, mock.patch.object(install, "run") as run:
            with self.assertRaisesRegex(SystemExit, "missing local model"):
                install.main()
        mkdir.assert_not_called()
        run.assert_not_called()

    def test_missing_hermes_exits_before_profile_changes(self) -> None:
        with mock.patch.object(install.importlib.util, "find_spec", return_value=None), mock.patch.object(
            install.Path, "mkdir"
        ) as mkdir:
            with self.assertRaisesRegex(SystemExit, "must have Hermes installed"):
                install.main()
        mkdir.assert_not_called()

    def test_unsupported_python_exits_before_any_profile_or_service_work(self) -> None:
        with mock.patch.object(install.sys, "version_info", (3, 9, 6)), mock.patch.object(
            install.Path, "mkdir"
        ) as mkdir, mock.patch.object(install, "local_model_preflight") as preflight, mock.patch.object(
            install, "run"
        ) as run:
            with self.assertRaisesRegex(SystemExit, "Python >= 3.11"):
                install.main()
        mkdir.assert_not_called()
        preflight.assert_not_called()
        run.assert_not_called()

    def test_missing_dateutil_exits_before_any_profile_or_service_work(self) -> None:
        original_import = builtins.__import__

        def import_without_dateutil(name, *args, **kwargs):
            if name == "dateutil.rrule":
                raise ImportError("synthetic missing dependency")
            return original_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=import_without_dateutil), mock.patch.object(
            install.Path, "mkdir"
        ) as mkdir, mock.patch.object(install, "local_model_preflight") as preflight, mock.patch.object(
            install, "run"
        ) as run:
            with self.assertRaisesRegex(SystemExit, "python-dateutil is required"):
                install.main()
        mkdir.assert_not_called()
        preflight.assert_not_called()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
