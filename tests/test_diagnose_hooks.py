"""The installed diagnostic must catch launch failures that hook mocks miss."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/high-agency"
SPEC = importlib.util.spec_from_file_location("diagnose_hooks", PLUGIN / "scripts/diagnose_hooks.py")
DIAGNOSTIC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTIC)


class HookDiagnosticTests(unittest.TestCase):
    def test_missing_configured_python_does_not_pass_via_running_interpreter(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = DIAGNOSTIC.diagnose(PLUGIN, claude_version="2.1.290", source_env={"PATH": temporary})
        self.assertEqual(report["status"], "failed")
        interpreter = next(item for item in report["checks"] if item["name"] == "configured_interpreter")
        self.assertEqual(interpreter["command"], "python")
        self.assertIsNone(interpreter["executable"])
        self.assertIn("python3-only", interpreter["next_step"])

    def test_old_client_reports_both_version_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = DIAGNOSTIC.diagnose(PLUGIN, claude_version="2.1.138 (Claude Code)", source_env={"PATH": temporary})
        claude = report["checks"][0]
        self.assertEqual(claude["status"], "failed")
        self.assertFalse(claude["exec_args_supported"])
        self.assertFalse(claude["stop_context_supported"])
        self.assertIn("2.1.163", claude["next_step"])
        check = DIAGNOSTIC._claude_check("unused", "2.1.162", {}, Path("."))
        self.assertTrue(check["exec_args_supported"])
        self.assertFalse(check["stop_context_supported"])

    def test_unavailable_cli_version_is_not_inferred_from_hook_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = DIAGNOSTIC._claude_check("not-installed-claude", None, {"PATH": temporary}, Path(temporary))
        self.assertEqual(result["status"], "unverified")
        self.assertNotIn("version", result)
        result = DIAGNOSTIC._claude_check("unused", "unknown build", {}, Path("."))
        self.assertEqual(result["status"], "unverified")
        self.assertNotIn("version", result)

    def test_old_configured_python_is_rejected_before_hooks_start(self):
        real_run = DIAGNOSTIC._run
        def fake_probe(argv, *args, **kwargs):
            if argv[:2] == ["python", "-c"]:
                return {"exit_code": 0, "stdout": json.dumps({"version": [3, 9, 22], "executable": "/old/python"}), "stderr": ""}
            return real_run(argv, *args, **kwargs)
        with patch.object(DIAGNOSTIC, "_run", side_effect=fake_probe):
            report = DIAGNOSTIC.diagnose(PLUGIN, claude_version="2.1.290")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["checks"][-1]["status"], "skipped")
        self.assertEqual(report["checks"][1]["runtime"]["version"], [3, 9, 22])

    def test_safe_environment_preserves_path_without_auth_or_user_state(self):
        source = {"PATH": "original-path", "ANTHROPIC_API_KEY": "private-key",
                  "CLAUDE_CODE_OAUTH_TOKEN": "private-token", "GIT_DIR": "user-repo",
                  "TMPDIR": "user-temp", "CLAUDE_PLUGIN_ROOT": "user-plugin", "PYTHONPATH": "python-import-path"}
        env = DIAGNOSTIC._environment(Path("isolated-home"), source)
        self.assertEqual(env["PATH"], source["PATH"])
        self.assertEqual(env["PYTHONPATH"], source["PYTHONPATH"])
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertNotIn("CLAUDE_CODE_OAUTH_TOKEN", env)
        self.assertNotIn("GIT_DIR", env)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", env)
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertNotEqual(env["TMPDIR"], source["TMPDIR"])

    @unittest.skipUnless(shutil.which("python") and shutil.which("git"), "Configured Python and Git are needed for a real fixture")
    def test_real_configured_entrypoints_execute_without_touching_user_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary)
            original = outside / "user-state.json"
            original.write_text('{"untouched":true}', encoding="utf-8")
            env = {**os.environ, "TMPDIR": str(outside), "TEMP": str(outside), "TMP": str(outside),
                   "PLUGIN_DATA": str(outside), "CLAUDE_PLUGIN_DATA": str(outside)}
            report = DIAGNOSTIC.diagnose(PLUGIN, claude_version="2.1.290", source_env=env)
            self.assertEqual(list(outside.iterdir()), [original])
            self.assertEqual(original.read_text(), '{"untouched":true}')
        self.assertEqual(report["status"], "passed", report)
        fixture = next(item for item in report["checks"] if item["name"] == "configured_hook_fixture")
        self.assertEqual(fixture["entrypoints"], ["verification_state.py", "routing_observer.py", "stop_loop.py"])
        self.assertIn("synthetic events", report["scope"])
        self.assertIn("No real Claude event delivery", report["scope"])
        self.assertEqual(report["environment"]["path"], "inherited; value not printed")


if __name__ == "__main__":
    unittest.main()
