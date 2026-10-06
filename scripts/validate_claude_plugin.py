#!/usr/bin/env python3
"""Validate with a real Claude CLI in an empty home, without model inference."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def native_cli(executable: str) -> Path | None:
    """Resolve a native CLI, including npm's Windows installation layout."""
    cli = shutil.which(executable)
    if not cli:
        return None
    cli_path = Path(cli).resolve()
    if os.name == "nt" and cli_path.suffix.lower() in {".cmd", ".bat"}:
        # npm's shim is a batch script, not an executable. Use the package's
        # native binary directly so paths never need cmd.exe quoting.
        candidates = [
            cli_path.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe",
            cli_path.parent.parent / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe",
            cli_path.parent / "node_modules" / "@anthropic-ai" / "claude-code-win32-x64" / "claude.exe",
            cli_path.parent.parent / "@anthropic-ai" / "claude-code-win32-x64" / "claude.exe",
        ]
        cli_path = next((item for item in candidates if item.is_file()), None)
    return cli_path


def validate(executable: str, root: Path) -> dict:
    cli_path = native_cli(executable)
    if cli_path is None:
        return {"passed": False, "error": "Claude CLI executable not found; pass --claude with a native binary path"}
    cli = str(cli_path)
    plugin = root / "plugins" / "high-agency"
    report = {"passed": False, "inference_run": False, "checks": []}
    with tempfile.TemporaryDirectory(prefix="high-agency-cli-") as temporary:
        home = Path(temporary)
        config = home / "config"
        config.mkdir()
        (home / "tmp").mkdir()
        env = {
            "PATH": os.environ.get("PATH", os.defpath),
            "HOME": str(home),
            "CLAUDE_CONFIG_DIR": str(config),
            "XDG_CONFIG_HOME": str(home / "xdg"),
            "TMPDIR": str(home / "tmp"),
            "LANG": "C.UTF-8",
            "TERM": "dumb",
            "CI": "true",
            "NO_COLOR": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "DISABLE_AUTOUPDATER": "1",
        }
        if os.name == "nt":
            for name in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "ProgramFiles", "ProgramFiles(x86)"):
                if name in os.environ:
                    env[name] = os.environ[name]
            env.update({"USERPROFILE": str(home), "APPDATA": str(home / "appdata"),
                        "LOCALAPPDATA": str(home / "localappdata"),
                        "TEMP": str(home / "tmp"), "TMP": str(home / "tmp")})

        def run(name: str, arguments: list[str]) -> bool:
            try:
                process = subprocess.run(
                    [cli, *arguments], cwd=home, env=env, stdin=subprocess.DEVNULL,
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, check=False,
                )
                item = {"name": name, "exit_code": process.returncode,
                        "stdout": process.stdout[-4000:], "stderr": process.stderr[-4000:]}
            except (OSError, subprocess.TimeoutExpired) as error:
                item = {"name": name, "exit_code": None, "error": type(error).__name__}
            report["checks"].append(item)
            return item["exit_code"] == 0

        if not run("version", ["--version"]):
            return report
        report["cli_version"] = report["checks"][-1]["stdout"].strip()
        for name, target in (("marketplace", root), ("manifest", plugin),
                             ("agents", plugin / "agents")):
            if not run(name, ["plugin", "validate", str(target)]):
                return report
        # A Windows Git checkout can use CRLF. The host's alternate frontmatter
        # parser exposed an unquoted colon that its LF fast path tolerated.
        # Exercise the actual parser under both line endings on every CI OS.
        crlf_plugin = home / "crlf-plugin"
        shutil.copytree(plugin, crlf_plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for markdown in crlf_plugin.rglob("*.md"):
            content = markdown.read_bytes().replace(b"\r\n", b"\n")
            markdown.write_bytes(content.replace(b"\n", b"\r\n"))
        if not run("crlf_manifest", ["plugin", "validate", str(crlf_plugin)]):
            return report
        log = home / "load.log"
        if not run("load", ["--plugin-dir", str(plugin), "--init-only", "--debug-file", str(log)]):
            return report
        logs = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
        expected = {
            "skills": len(list((plugin / "skills").glob("*/SKILL.md"))),
            "agents": len(list((plugin / "agents").glob("*.md"))),
            "commands": len(list((plugin / "commands").glob("*.md"))),
        }
        loaded = {}
        for kind in expected:
            match = re.search(rf"Loaded (\d+) {kind} from plugin high-agency default directory", logs)
            loaded[kind] = int(match.group(1)) if match else None
        report["components"] = {"expected": expected, "loaded": loaded}
        report["hooks_read"] = "Read hooks.json for plugin high-agency (enabled=true)" in logs
        report["hooks_loaded"] = "Loading hooks from plugin: high-agency" in logs
        report["passed"] = loaded == expected and report["hooks_read"] and report["hooks_loaded"]
        # init-only checks registration. It does not execute user tasks, model calls,
        # or background agent communication, even when its exit code is zero.
        report["scope"] = "manifest validation and component registration only"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default="claude", help="Claude executable or absolute path")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    arguments = parser.parse_args()
    report = validate(arguments.claude, Path(__file__).resolve().parents[1])
    output = json.dumps(report, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
