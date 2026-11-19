#!/usr/bin/env python3
"""Installer preflight tests; never install files or access a real profile."""

import builtins
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
            install.update_env(profile_env, {"API_SERVER_PORT": "8643", "AI_GATEWAY_API_KEY": "gateway-test-key"})
            self.assertIn('AI_KOT_GG_API_KEY="website-test-key"\n', profile_env.read_text())
            self.assertIn("API_SERVER_PORT=8643\n", profile_env.read_text())
            self.assertEqual(profile_env.stat().st_mode & 0o777, 0o600)


class GatewayKeyPreflightTests(unittest.TestCase):
    def test_reads_only_the_harmonica_client_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clients = Path(directory) / "clients.env"
            clients.write_text("other=" + "x" * 32 + "\nharmonica=" + "k" * 32 + "\n")
            self.assertEqual(install.gateway_key_preflight(clients), "k" * 32)

    def test_missing_key_exits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clients = Path(directory) / "clients.env"
            for content in (None, "other=" + "x" * 32 + "\n", "harmonica=short\n"):
                with self.subTest(content=content):
                    if content is not None:
                        clients.write_text(content)
                    with self.assertRaisesRegex(SystemExit, "client key named 'harmonica'"):
                        install.gateway_key_preflight(clients)


class InstallerPreflightTests(unittest.TestCase):
    def test_missing_gateway_key_exits_before_profile_changes(self) -> None:
        with mock.patch.object(install.sys, "argv", ["install.py"]), mock.patch.object(
            install, "gateway_key_preflight", side_effect=SystemExit("missing gateway key")
        ), mock.patch.object(install.Path, "mkdir") as mkdir, mock.patch.object(install, "run") as run:
            with self.assertRaisesRegex(SystemExit, "missing gateway key"):
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
        ) as mkdir, mock.patch.object(install, "gateway_key_preflight") as preflight, mock.patch.object(
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
        ) as mkdir, mock.patch.object(install, "gateway_key_preflight") as preflight, mock.patch.object(
            install, "run"
        ) as run:
            with self.assertRaisesRegex(SystemExit, "python-dateutil is required"):
                install.main()
        mkdir.assert_not_called()
        preflight.assert_not_called()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
