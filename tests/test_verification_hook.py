import json
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "plugins/high-agency/hooks/verification_state.py"


def run_hook(payload, *, cwd=None):
    return subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=cwd or ROOT,
        timeout=5,
        check=False,
    )


class VerificationHookTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "High Agency Test"], cwd=root, check=True)
        (root / "app.py").write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "app.py"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
        return temp, root

    def test_inactive_bash_post_tool_use_is_silent(self):
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": "inactive-" + uuid.uuid4().hex,
            "cwd": str(ROOT),
            "tool_name": "Bash",
            "tool_input": {"command": "echo ok"},
        }
        result = run_hook(payload)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_active_prompt_then_bash_verification_is_silent(self):
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        session_id = "active-" + uuid.uuid4().hex

        submit = run_hook(
            {
                "hook_event_name": "UserPromptSubmit",
                "session_id": session_id,
                "cwd": str(root),
                "prompt": "Use high-agency-coding for this task",
            },
            cwd=root,
        )
        self.assertEqual(submit.returncode, 0)
        self.assertEqual(submit.stderr, "")

        post = run_hook(
            {
                "hook_event_name": "PostToolUse",
                "session_id": session_id,
                "cwd": str(root),
                "tool_name": "Bash",
                "tool_input": {"command": "python -m pytest tests/test_auth.py"},
            },
            cwd=root,
        )
        self.assertEqual(post.returncode, 0)
        self.assertEqual(post.stderr, "")

    def test_malformed_input_fails_open(self):
        result = subprocess.run(
            ["python3", str(HOOK)],
            input="{not-json",
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
