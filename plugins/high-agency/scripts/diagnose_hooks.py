#!/usr/bin/env python3
"""Diagnose configured hook launchers in an isolated fixture, without inference.

Run with any available Python 3 interpreter. The configured hook interpreter is
resolved separately, so running this script with python3 does not accidentally
make a missing `python` launcher pass. The diagnostic writes its fixture and
hook state only to a temporary directory; it does not edit project or settings
files. Installed interpreter startup customization remains in effect.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


MINIMUM_CLAUDE = (2, 1, 163)
EXEC_FORM_CLAUDE = (2, 1, 139)
PYTHON_STARTUP_VARS = (
    "PYTHONHOME", "PYTHONPATH", "PYTHONUTF8", "PYTHONIOENCODING",
    "PYTHONSAFEPATH", "PYTHONNOUSERSITE",
)
SCOPE = (
    "Configured command/args executed with synthetic events in a temporary Git "
    "fixture. No real Claude event delivery, plugin trust, model call, or user "
    "session is exercised. Run from the environment that launches Claude; a "
    "terminal and an IDE can inherit different PATH values."
)


def _version(value):
    match = re.search(r"(?<![\d.])(\d+)\.(\d+)\.(\d+)(?![\d.])", value or "")
    return tuple(int(part) for part in match.groups()) if match else None


def _brief(value):
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return (value or "").strip()[-1200:]


def _run(argv, env, cwd, payload=None, timeout=15):
    try:
        process = subprocess.run(
            argv, cwd=cwd, env=env, input=payload, capture_output=True,
            shell=False, timeout=timeout, check=False,
        )
        return {"exit_code": process.returncode, "stdout": _brief(process.stdout),
                "stderr": _brief(process.stderr)}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"exit_code": None, "error": type(error).__name__ + ": " + _brief(str(error))}


def _environment(home, source):
    # Preserve interpreter resolution, but never inherit credentials, host
    # sessions, global Git configuration, or the user's state directories.
    names = (
        "PATH", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "ProgramFiles",
        "ProgramFiles(x86)", "LANG", "LC_ALL",
    ) + PYTHON_STARTUP_VARS
    env = {name: source[name] for name in names if name in source}
    env.setdefault("PATH", os.defpath)
    env.update({
        "HOME": str(home), "USERPROFILE": str(home),
        "APPDATA": str(home / "appdata"), "LOCALAPPDATA": str(home / "localappdata"),
        "CLAUDE_CONFIG_DIR": str(home / "config"), "XDG_CONFIG_HOME": str(home / "config"),
        "TMPDIR": str(home / "tmp"), "TEMP": str(home / "tmp"), "TMP": str(home / "tmp"),
        "GIT_CONFIG_GLOBAL": str(home / "empty.gitconfig"), "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0", "PYTHONDONTWRITEBYTECODE": "1",
        "HIGH_AGENCY_HOOK_DEBUG": "1", "CI": "true", "TERM": "dumb", "NO_COLOR": "1",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1",
    })
    return env


def _claude_executable(value, env):
    found = shutil.which(value, path=env["PATH"])
    if not found:
        return None
    path = Path(found).absolute()
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".bat"}:
        # npm shims are batch files; exec form must use the native binary.
        candidates = [
            path.parent / "node_modules/@anthropic-ai/claude-code/bin/claude.exe",
            path.parent.parent / "@anthropic-ai/claude-code/bin/claude.exe",
            path.parent / "node_modules/@anthropic-ai/claude-code-win32-x64/claude.exe",
            path.parent.parent / "@anthropic-ai/claude-code-win32-x64/claude.exe",
            path.parent / "node_modules/@anthropic-ai/claude-code-win32-arm64/claude.exe",
            path.parent.parent / "@anthropic-ai/claude-code-win32-arm64/claude.exe",
        ]
        return str(next((item for item in candidates if item.is_file()), "")) or None
    return str(path)


def _claude_check(executable, supplied_version, env, home):
    result = {"name": "claude_version", "minimum": ".".join(map(str, MINIMUM_CLAUDE))}
    if supplied_version:
        raw = supplied_version
        result["source"] = "user_supplied; current host identity not verified"
    else:
        cli = _claude_executable(executable, env)
        if not cli:
            return {**result, "status": "unverified", "detail": "Claude executable unavailable",
                    "next_step": "Pass --claude with the native executable, or --claude-version with the version reported by the affected client."}
        result["executable"] = cli
        outcome = _run([cli, "--version"], env, home)
        if outcome["exit_code"] != 0:
            return {**result, **outcome, "status": "unverified",
                    "next_step": "Check claude --version in the affected client environment; pass --claude-version if its CLI cannot be launched here."}
        raw = outcome["stdout"]
        result["source"] = "native Claude executable --version"
    version = _version(raw)
    if version is None:
        return {**result, "status": "unverified", "detail": "Could not parse a three-part Claude version",
                "next_step": "Pass --claude-version with the exact output of claude --version."}
    result.update({"version": ".".join(map(str, version)),
                   "exec_args_supported": version >= EXEC_FORM_CLAUDE,
                   "stop_context_supported": version >= MINIMUM_CLAUDE})
    if version < MINIMUM_CLAUDE:
        return {**result, "status": "failed",
                "next_step": "Update the affected Claude Code client to 2.1.163 or later and start a new session. Exec-form args require 2.1.139; non-error Stop feedback requires 2.1.163."}
    return {**result, "status": "passed"}


def _launch(hook, env, cwd, payload):
    def render(value):
        for name in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA", "CLAUDE_PROJECT_DIR"):
            value = value.replace("${" + name + "}", env[name])
        if "${" in value:
            raise ValueError("Unresolved hook configuration placeholder")
        return value
    command = render(hook["command"])
    args = hook.get("args")
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        raise ValueError("Configured hook must have a native exec args array")
    return _run(
        [command, *(render(arg) for arg in args)], env, cwd,
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        min(max(float(hook.get("timeout", 12)), 1), 30) + 2,
    )


def _fixture(config, plugin, env, home):
    git = shutil.which("git", path=env["PATH"])
    if not git:
        raise ValueError("Git is missing from PATH; the isolated repository fixture cannot run")
    repo, template = home / "작업 tree with spaces", home / "empty-template"
    repo.mkdir()
    template.mkdir()
    commands = [
        ["init", "-q", "--template=" + str(template)],
        ["add", "fixture.txt"],
        ["-c", "user.name=High Agency Hook Diagnostic", "-c", "user.email=diagnostic@example.invalid",
         "-c", "commit.gpgSign=false", "-c", "core.hooksPath=" + str(template),
         "commit", "-qm", "Isolated hook diagnostic fixture"],
    ]
    (repo / "fixture.txt").write_text("diagnostic fixture\n", encoding="utf-8")
    for arguments in commands:
        outcome = _run([git, *arguments], env, repo)
        if outcome["exit_code"] != 0:
            raise ValueError("Git fixture failed: " + (outcome.get("error") or outcome.get("stderr") or str(outcome["exit_code"])))
    env.update({"CLAUDE_PLUGIN_ROOT": str(plugin), "CLAUDE_PLUGIN_DATA": str(home / "plugin-data"),
                "CLAUDE_PROJECT_DIR": str(repo)})
    transcript = home / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    identity = "high-agency-isolated-diagnostic"
    base = {"session_id": identity, "prompt_id": "diagnostic-prompt", "cwd": str(repo),
            "transcript_path": str(transcript)}
    digest = hashlib.sha256(json.dumps([identity, ""], separators=(",", ":")).encode()).hexdigest()[:32]
    state_root = home / "tmp/high-agency-claude-code-verification"
    state_path = state_root / (digest + ".json")

    def run_event(event, payload, tool=None):
        matched = []
        for group in config["hooks"].get(event, []):
            matcher = group.get("matcher", "")
            if tool and matcher and not re.search(matcher, tool):
                continue
            matched.extend(group.get("hooks", []))
        if not matched:
            raise ValueError("No configured command hook for " + event)
        response = {}
        for hook in matched:
            outcome = _launch(hook, env, repo, {**base, "hook_event_name": event, **payload})
            if outcome["exit_code"] != 0 or outcome.get("stderr"):
                raise ValueError(event + " launcher failed: " + (outcome.get("error") or outcome.get("stderr") or str(outcome["exit_code"])))
            if outcome["stdout"]:
                response = json.loads(outcome["stdout"])
                if not isinstance(response, dict):
                    raise ValueError(event + " returned a non-object hook response")
        return response

    run_event("UserPromptSubmit", {"prompt": "Use bounded-autonomy for this diagnostic fixture"})
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("schema_version") != 2 or not state.get("active") or not state.get("baseline_snapshot", {}).get("available"):
        raise ValueError("UserPromptSubmit did not create active state with an available Git baseline")
    run_event("PostToolUse", {"tool_name": "Agent", "tool_use_id": "diagnostic-call",
                              "tool_input": {"model": "haiku"},
                              "tool_response": {"status": "completed", "agentId": "diagnostic-child"}}, tool="Agent")
    observed = json.loads((state_root / "routing" / (digest + ".json")).read_text(encoding="utf-8"))
    if len(observed.get("records", [])) != 1:
        raise ValueError("Routing observer did not record the isolated fixture event")
    stop = {"last_assistant_message": "<!-- high-agency:continue max=1 -->", "stop_hook_active": False}
    response = run_event("Stop", stop)
    output = response.get("hookSpecificOutput", {})
    if (response.get("decision") is not None or output.get("hookEventName") != "Stop"
            or "1/1" not in output.get("additionalContext", "")):
        raise ValueError("Stop did not return bounded, non-error additionalContext feedback")
    response = run_event("Stop", {**stop, "stop_hook_active": True})
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if response or state.get("completion_reason") != "budget_exhausted":
        raise ValueError("Stop did not finish after the configured continuation budget")
    return {"name": "configured_hook_fixture", "status": "passed",
            "entrypoints": ["verification_state.py", "routing_observer.py", "stop_loop.py"],
            "checks": ["UTF-8 stdin", "active state and Git baseline", "routing record",
                       "non-error Stop feedback", "continuation budget exhausted"]}


def diagnose(plugin=None, claude="claude", claude_version=None, source_env=None):
    plugin = Path(plugin or Path(__file__).resolve().parents[1]).resolve()
    source_env = os.environ if source_env is None else source_env
    report = {"schema_version": 1, "scope": SCOPE, "platform": sys.platform,
              "environment": {"path": "inherited; value not printed",
                              "home_config_temp_git": "isolated temporary directories",
                              "python_startup_vars_inherited": [name for name in PYTHON_STARTUP_VARS if name in source_env],
                              "note": "Selected Python startup settings are preserved to expose startup failures; interpreter customization is not isolated."},
              "checks": [], "next_steps": []}
    with tempfile.TemporaryDirectory(prefix="high-agency-hook-diagnostic-") as temporary:
        home = Path(temporary)
        (home / "config").mkdir()
        (home / "tmp").mkdir()
        (home / "empty.gitconfig").write_text("", encoding="utf-8")
        env = _environment(home, source_env)
        report["checks"].append(_claude_check(claude, claude_version, env, home))
        try:
            config = json.loads((plugin / "hooks/hooks.json").read_text(encoding="utf-8"))
            hooks = [hook for groups in config["hooks"].values() for group in groups for hook in group["hooks"]]
            commands = sorted({hook["command"] for hook in hooks if hook.get("type") == "command"})
            if not commands or any(hook.get("type") != "command" for hook in hooks):
                raise ValueError("Expected the plugin's configured native command hooks")
            for command in commands:
                found = shutil.which(command, path=env["PATH"])
                item = {"name": "configured_interpreter", "command": command, "executable": found}
                if not found:
                    item.update({"status": "failed", "detail": "Configured executable is absent from PATH",
                                 "next_step": "Expose Python 3.10+ as the real executable 'python' on the PATH inherited by Claude. A python3-only install or shell alias does not satisfy native exec hooks. Restart Claude after correcting its environment."})
                elif os.name == "nt" and Path(found).suffix.lower() in {".cmd", ".bat"}:
                    item.update({"status": "failed", "detail": "Configured interpreter is a batch shim, not a native executable",
                                 "next_step": "Use a Python installation that exposes python.exe on Claude's PATH."})
                else:
                    outcome = _run([command, "-c", "import json,sys; print(json.dumps({'version':list(sys.version_info[:3]),'executable':sys.executable}))"], env, home)
                    try:
                        details = json.loads(outcome["stdout"]) if outcome["exit_code"] == 0 else {}
                        if not isinstance(details, dict):
                            raise ValueError("Interpreter probe did not return an object")
                        version = tuple(details.get("version", []))
                        supported = len(version) == 3 and version >= (3, 10, 0)
                    except (ValueError, TypeError):
                        details, supported = {}, False
                    item.update({"status": "passed" if supported else "failed", "runtime": details})
                    if not supported:
                        item.update({"process": outcome, "next_step": "The configured python must start successfully and be Python 3.10+. Check for an older Python, Windows Store alias, or Python environment error on Claude's PATH."})
                report["checks"].append(item)
            if all(item["status"] == "passed" for item in report["checks"] if item["name"] == "configured_interpreter"):
                report["checks"].append(_fixture(config, plugin, env, home))
            else:
                report["checks"].append({"name": "configured_hook_fixture", "status": "skipped",
                                         "detail": "Configured interpreter could not run"})
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            report["checks"].append({"name": "configured_hook_fixture", "status": "failed",
                                     "detail": type(error).__name__ + ": " + _brief(str(error)),
                                     "next_step": "Check this failure against the affected client's hook error. Update the plugin and start a new Claude session; include this diagnostic if the failure persists."})
    report["next_steps"] = list(dict.fromkeys(item["next_step"] for item in report["checks"] if item.get("next_step")))
    statuses = {item["status"] for item in report["checks"]}
    report["status"] = "failed" if "failed" in statuses else "unverified" if "unverified" in statuses else "passed"
    report["passed"] = report["status"] == "passed"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default="claude", help="Claude executable or native executable path")
    parser.add_argument("--claude-version", help="Version reported by the affected client if its CLI is unavailable")
    args = parser.parse_args()
    report = diagnose(claude=args.claude, claude_version=args.claude_version)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return {"passed": 0, "failed": 1, "unverified": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
