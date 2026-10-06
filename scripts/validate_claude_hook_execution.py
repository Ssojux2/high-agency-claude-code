#!/usr/bin/env python3
"""Execute the configured hooks through the real Claude CLI without inference.

The CLI's Messages API endpoint is a deterministic fixture on loopback, using
an isolated home and a dummy API key. Nonessential traffic is disabled; this
does not impose an operating-system network boundary. Read, Write, and a native
shell really run against a disposable Git repository. This verifies host event
delivery and feedback, not authenticated model behavior or its choice of tools.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from validate_claude_plugin import native_cli


TEST_COMMAND = "python -m unittest discover -v"
CONTINUE_MARKER = "<!-- high-agency:continue max=1 -->"
TEST_SOURCE = (
    "import unittest\n\n"
    "class FixtureTest(unittest.TestCase):\n"
    "    def test_arithmetic(self):\n"
    "        self.assertEqual(2 + 2, 4)\n"
)
MAX_REQUEST_BYTES = 16 * 1024 * 1024


def isolated_environment(home: Path, temporary: Path) -> dict[str, str]:
    # Deliberately build an allowlist instead of inheriting credentials, proxy
    # configuration, shell initialization variables, or project Python paths.
    env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "HOME": str(home),
        "CLAUDE_CONFIG_DIR": str(home / "config"),
        "XDG_CONFIG_HOME": str(home / "xdg"),
        "TMPDIR": str(temporary), "TEMP": str(temporary), "TMP": str(temporary),
        "LANG": "C.UTF-8", "TERM": "dumb", "CI": "true", "NO_COLOR": "1",
        "ANTHROPIC_API_KEY": "sk-ant-local-fixture-dummy-not-a-real-key",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "DISABLE_AUTOUPDATER": "1",
        "HIGH_AGENCY_HOOK_DEBUG": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": str(home / "empty.gitconfig"),
    }
    if os.name == "nt":
        for name in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "ProgramFiles", "ProgramFiles(x86)"):
            if name in os.environ:
                env[name] = os.environ[name]
        env.update({
            "USERPROFILE": str(home),
            "APPDATA": str(home / "appdata"),
            "LOCALAPPDATA": str(home / "localappdata"),
            # With nonessential traffic disabled, the Windows feature flag is
            # not fetched. Explicit opt-in enables the native tool even when
            # Git Bash is also installed (as on GitHub's Windows runners).
            # https://code.claude.com/docs/en/env-vars
            "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1",
        })
    return env


def fixture_server(plan: list[list[dict]]) -> tuple[http.server.ThreadingHTTPServer, list[dict]]:
    requests: list[dict] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def send_body(self, data: bytes, content_type: str, status: int = 200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            try:
                self.wfile.write(data)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                # A cancelled CLI may close a connection during cleanup.
                pass

        def send_json(self, data: dict, status: int = 200):
            self.send_body(json.dumps(data).encode("utf-8"), "application/json", status)

        def do_GET(self):
            self.send_json({"error": {"type": "not_found_error", "message": "No fixture GET endpoint"}}, 404)

        def do_POST(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > MAX_REQUEST_BYTES:
                    self.send_json({"error": {"message": "Request exceeds fixture limit"}}, 413)
                    return
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Messages request must be an object")
            except (ValueError, TypeError):
                self.send_json({"error": {"message": "Invalid fixture JSON request"}}, 400)
                return
            path = self.path.partition("?")[0]
            if path == "/v1/messages/count_tokens":
                self.send_json({"input_tokens": 100})
                return
            if path != "/v1/messages":
                self.send_json({"error": {"message": "No fixture endpoint"}}, 404)
                return
            requests.append(body)
            step = len(requests) - 1
            # Extra model turns are a failed assertion, but still receive a
            # terminal response so a diagnostic run can shut down normally.
            content = plan[step] if step < len(plan) else [{"type": "text", "text": "Fixture finished."}]
            reason = "tool_use" if any(block["type"] == "tool_use" for block in content) else "end_turn"
            message = {
                "id": f"msg_fixture_{step}", "type": "message", "role": "assistant",
                "model": body.get("model"), "content": content,
                "stop_reason": reason, "stop_sequence": None,
                "usage": {"input_tokens": 100, "output_tokens": 30},
            }
            if not body.get("stream"):
                self.send_json(message)
                return
            events = [("message_start", {
                "type": "message_start",
                "message": {**message, "content": [], "stop_reason": None,
                            "usage": {"input_tokens": 100, "output_tokens": 0}},
            })]
            for index, block in enumerate(content):
                if block["type"] == "text":
                    start = {"type": "text", "text": ""}
                    delta = {"type": "text_delta", "text": block["text"]}
                else:
                    start = {**block, "input": {}}
                    delta = {"type": "input_json_delta", "partial_json": json.dumps(block["input"])}
                events.extend([
                    ("content_block_start", {"type": "content_block_start", "index": index, "content_block": start}),
                    ("content_block_delta", {"type": "content_block_delta", "index": index, "delta": delta}),
                    ("content_block_stop", {"type": "content_block_stop", "index": index}),
                ])
            events.extend([
                ("message_delta", {"type": "message_delta", "delta": {"stop_reason": reason, "stop_sequence": None},
                                   "usage": {"output_tokens": 30}}),
                ("message_stop", {"type": "message_stop"}),
            ])
            data = "".join(f"event: {event}\ndata: {json.dumps(body)}\n\n" for event, body in events)
            self.send_body(data.encode("utf-8"), "text/event-stream")

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    return server, requests


def run_fixture(cli: Path, root: Path, base: Path, report: dict) -> None:
    home = base / "isolated home"
    work = base / "작업 tree with spaces"
    plugin = base / "플러그인 cache with spaces"
    temporary = base / "temporary state"
    empty_template = base / "empty git template"
    for path in (home, work, temporary, empty_template, home / "config", home / "xdg"):
        path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "plugins/high-agency", plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # hooks.json and its entrypoints are copied exactly; this script never
    # replaces the configured interpreter, injects payloads, or calls hooks.
    env = isolated_environment(home, temporary)
    (home / "empty.gitconfig").write_text("", encoding="utf-8")
    test_file = work / "test_smoke.py"
    test_file.write_text(TEST_SOURCE.replace("2 + 2, 4", "1 + 1, 2"), encoding="utf-8")
    for arguments in (
        ["init", "-q", "--template=" + str(empty_template)],
        ["config", "user.name", "Local Hook Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
        ["config", "core.autocrlf", "false"],
        ["add", "test_smoke.py"], ["commit", "-qm", "Initialize local fixture"],
    ):
        subprocess.run(["git", *arguments], cwd=work, env=env, check=True, capture_output=True, timeout=15)
    shell_tool = "PowerShell" if os.name == "nt" else "Bash"
    report["shell_tool"] = shell_tool
    plan = [
        [{"type": "tool_use", "id": "toolu_fixture_read", "name": "Read",
          "input": {"file_path": str(test_file)}}],
        [{"type": "text", "text": "Impact: local | files <= 1 | modules <= 1 | boundary=private"},
         {"type": "tool_use", "id": "toolu_fixture_write", "name": "Write",
          "input": {"file_path": str(test_file), "content": TEST_SOURCE}}],
        [{"type": "tool_use", "id": "toolu_fixture_test", "name": shell_tool,
          "input": {"command": TEST_COMMAND, "description": "Run deterministic local fixture test"}}],
        [{"type": "tool_use", "id": "toolu_fixture_diff", "name": shell_tool,
          "input": {"command": "git diff HEAD", "description": "Inspect complete local fixture diff"}}],
        [{"type": "text", "text": "Fixture checks completed.\n" + CONTINUE_MARKER}],
        # Repeat the marker deliberately to prove the actual host stops when
        # the task's budget is exhausted, rather than merely obeying prose.
        [{"type": "text", "text": "Fixture finished at its continuation limit.\n" + CONTINUE_MARKER}],
    ]
    server, requests = fixture_server(plan)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{server.server_port}"
    debug_log = base / "claude-debug.log"
    try:
        version = subprocess.run([str(cli), "--version"], cwd=home, env=env, stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, check=True)
        report["cli_version"] = version.stdout.strip()
        command = [
            str(cli), "--print", "--output-format", "stream-json", "--verbose", "--include-hook-events",
            "--plugin-dir", str(plugin), "--debug-file", str(debug_log), "--model", "claude-sonnet-4-6",
            "--setting-sources", "", "--strict-mcp-config", "--permission-mode", "dontAsk",
            "--allowedTools", "Read", "Write", f"{shell_tool}({TEST_COMMAND})", f"{shell_tool}(git diff HEAD)",
            "--tools", f"Read,Write,{shell_tool}", "--",
            "Use high-agency-coding for this local fixture. Update the arithmetic test, run unittest, "
            "inspect git diff, and make one bounded continuation.",
        ]
        process = subprocess.run(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    messages = []
    for line in process.stdout.splitlines():
        try:
            message = json.loads(line)
            if isinstance(message, dict):
                messages.append(message)
        except ValueError:
            pass
    started = [message for message in messages if message.get("subtype") == "hook_started"]
    responses = [message for message in messages if message.get("subtype") == "hook_response"]
    results = [message for message in messages if message.get("type") == "result"]
    report["exit_code"] = process.returncode
    report["model_fixture_requests"] = len(requests)
    report["hook_responses"] = [{
        "name": message.get("hook_name"), "event": message.get("hook_event"),
        "exit_code": message.get("exit_code"), "outcome": message.get("outcome"),
        **({"stderr": message["stderr"][-2000:]} if message.get("stderr") else {}),
    } for message in responses]
    last_content = requests[-1].get("messages", [])[-1].get("content", []) if requests else []
    stop_feedback = "\n".join(block.get("text", "") for block in last_content if isinstance(block, dict))
    states = [json.loads(path.read_text(encoding="utf-8"))
              for path in (temporary / "high-agency-claude-code-verification").glob("*.json")]
    state = states[0] if len(states) == 1 else {}
    evidence = state.get("verification_evidence", [])
    passed = [item for item in evidence if item.get("status") == "passed"]
    continuation = state.get("continuation", {})
    # A real failed/undelivered diff command leaves the normal initial value
    # None. Report failed checks instead of crashing the diagnostic itself.
    raw_diff = state.get("diff_snapshot")
    diff = raw_diff if isinstance(raw_diff, dict) else {}
    current_digest = "sha256:" + hashlib.sha256(test_file.read_bytes()).hexdigest()
    expected_names = {
        "UserPromptSubmit", "PreToolUse:Write", "PostToolUse:Write",
        f"PreToolUse:{shell_tool}", f"PostToolUse:{shell_tool}", "Stop",
    }
    report["checks"] = {
        "cli_completed": process.returncode == 0 and len(results) == 1
                         and results[0].get("is_error") is False,
        "normal_permissions_sufficed": len(results) == 1 and not results[0].get("permission_denials"),
        "actual_hook_events_delivered": {item.get("hook_name") for item in responses} == expected_names
                                        and len(responses) == 9,
        "every_started_hook_completed": len(started) == len(responses)
                                       and {item.get("hook_id") for item in started}
                                       == {item.get("hook_id") for item in responses},
        "hooks_exited_successfully": bool(responses) and all(
            item.get("exit_code") == 0 and item.get("outcome") == "success"
            and not item.get("stderr") for item in responses),
        "unicode_and_space_paths_worked": test_file.read_text(encoding="utf-8") == TEST_SOURCE,
        "verification_passed_in_fixture_cwd": len(passed) == 1 and passed[0].get("tool_use_id") == "toolu_fixture_test"
                                             and passed[0].get("shell") == shell_tool
                                             and Path(passed[0].get("cwd", "")).resolve() == work.resolve()
                                             and state.get("verification_commands") == [TEST_COMMAND],
        "current_diff_was_reviewed": diff.get("complete") is True
                                    and diff == state.get("verification_snapshot")
                                    and str(diff.get("files", {}).get("test_smoke.py", "")).endswith(current_digest),
        "stop_feedback_is_non_error": "Stop hook additional context:" in stop_feedback
                                     and "Stop hook blocking error" not in stop_feedback
                                     and "Final bounded-autonomy continuation 1/1" in stop_feedback,
        "continuation_budget_enforced": len(requests) == len(plan) and continuation.get("continuations") == 1
                                       and continuation.get("limit") == 1,
        "task_completed_at_budget": state.get("task_completed") is True
                                   and state.get("completion_reason") == "budget_exhausted",
    }
    report["passed"] = all(report["checks"].values())
    report["task"] = {
        "verification_status": passed[0].get("status") if len(passed) == 1 else "not_confirmed",
        "reviewed_files": sorted(diff.get("files", {})),
        "continuations": continuation.get("continuations"), "limit": continuation.get("limit"),
        "completed": state.get("task_completed"), "completion_reason": state.get("completion_reason"),
    }
    if not report["passed"]:
        # Only diagnostics from this disposable fixture are exposed; raw model
        # requests, system prompts, token-price estimates, and transcripts stay
        # in memory or the temporary directory, which is always cleaned up.
        report["diagnostics"] = {
            "stderr": process.stderr[-3000:],
            "stop_feedback": stop_feedback[-2000:],
            "failed_checks": [name for name, success in report["checks"].items() if not success],
        }
        if debug_log.is_file():
            lines = debug_log.read_text(encoding="utf-8", errors="replace").splitlines()
            report["diagnostics"]["hook_debug_tail"] = [
                line for line in lines if "hook" in line.lower() and ("error" in line.lower() or "failed" in line.lower())
            ][-12:]


def validate(executable: str, root: Path) -> dict:
    report = {
        "passed": False,
        "scope": "actual Claude host event delivery and native tool execution with mocked model transport",
        "model_transport": "deterministic Messages API fixture bound to 127.0.0.1",
        "authenticated_model_e2e": False,
        "external_model_inference": False,
        "checks": {},
    }
    cli = native_cli(executable)
    if cli is None:
        report["error"] = "Claude CLI executable not found; pass --claude with a native binary path"
        return report
    try:
        with tempfile.TemporaryDirectory(prefix="high-agency-host-hooks-") as temporary:
            run_fixture(cli, root, Path(temporary).resolve(), report)
    except (OSError, ValueError, TypeError, KeyError, IndexError, subprocess.SubprocessError) as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}
        report["passed"] = False
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default="claude", help="Claude executable or native binary path")
    parser.add_argument("--output", type=Path, help="Optional compact JSON report; raw request bodies are never saved")
    arguments = parser.parse_args()
    report = validate(arguments.claude, Path(__file__).resolve().parents[1])
    output = json.dumps(report, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
