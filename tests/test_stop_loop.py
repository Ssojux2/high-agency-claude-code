import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "plugins" / "high-agency" / "hooks" / "stop_loop.py"


class StopLoopTests(unittest.TestCase):
    def test_minimal_stop_hook_completes_without_runtime_name_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            transcript = root / "transcript.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "done"}],
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            payload = json.dumps(
                {
                    "transcript_path": str(transcript),
                    "cwd": str(root),
                    "session_id": "test-session",
                }
            )

            result = subprocess.run(
                [sys.executable, str(HOOK)],
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {})


if __name__ == "__main__":
    unittest.main()
