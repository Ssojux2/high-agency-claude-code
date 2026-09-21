#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import time
from pathlib import Path

MARKER_RE = re.compile(
    r"<!--\s*high-agency:continue(?:\s+max=(\d+))?\s*-->\s*$",
    re.IGNORECASE | re.DOTALL,
)
DEFAULT_MAX = 3
HARD_CAP = 12
STATE_TTL_SECONDS = 7 * 24 * 60 * 60
DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}
DOC_NAMES = {"LICENSE", "README", "CHANGELOG", "CONTRIBUTING", "CODE_OF_CONDUCT"}

def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")

def bounded_dir() -> Path:
    return Path(tempfile.gettempdir()) / "high-agency-claude-code"

def verification_dir() -> Path:
    return Path(tempfile.gettempdir()) / "high-agency-claude-code-verification"

def bounded_path(transcript_path: str) -> Path:
    digest = hashlib.sha256(transcript_path.encode("utf-8", "replace")).hexdigest()[:24]
    return bounded_dir() / f"{digest}.json"

def verification_path(payload: dict) -> Path:
    raw = str(payload.get("session_id") or payload.get("turn_id") or "default")
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", raw)[:120]
    return verification_dir() / f"{safe}.json"

def cleanup_old_states(directory: Path) -> None:
    if not directory.exists():
        return
    cutoff = time.time() - STATE_TTL_SECONDS
    for path in directory.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
        except OSError:
            pass

def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)

def clear(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass

def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    return ""

def last_assistant_message(transcript_path: Path) -> str:
    last = ""
    try:
        with transcript_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                message = entry.get("message")
                if not isinstance(message, dict) or message.get("role") != "assistant":
                    continue
                text = extract_text(message.get("content"))
                if text:
                    last = text
    except OSError:
        return ""
    return last

def needs_verification(files: list[str]) -> bool:
    for raw in files:
        name = Path(raw).name
        if name.upper() in DOC_NAMES or name.startswith("README"):
            continue
        if Path(raw).suffix.lower() in DOC_EXTS:
            continue
        return True
    return False

def reset_pass(vpath: Path, data: dict) -> None:
    if not data.get("active"):
        return
    data["edited_files"] = []
    data["verification_seen"] = False
    data["verification_commands"] = []
    data["guard_warned"] = False
    save_json(vpath, data)

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    transcript_raw = payload.get("transcript_path")
    if not isinstance(transcript_raw, str) or not transcript_raw:
        return 0

    message = last_assistant_message(Path(transcript_raw))
    if not message:
        return 0

    cleanup_old_states(bounded_dir())
    cleanup_old_states(verification_dir())

    bpath = bounded_path(transcript_raw)
    vpath = verification_path(payload)
    vdata = load_json(vpath)
    marker = MARKER_RE.search(message)

    edited_files = list(vdata.get("edited_files") or [])
    if (
        vdata.get("active")
        and needs_verification(edited_files)
        and not vdata.get("verification_seen")
        and not vdata.get("guard_warned")
    ):
        vdata["guard_warned"] = True
        save_json(vpath, vdata)
        suffix = ""
        if marker:
            requested = int(marker.group(1)) if marker.group(1) else DEFAULT_MAX
            limit = min(max(requested, 1), HARD_CAP)
            suffix = (
                f" If meaningful work still remains after verification, preserve the bounded-autonomy "
                f"contract and end with <!-- high-agency:continue max={limit} -->."
            )
        emit({
            "decision": "block",
            "reason": (
                "High Agency verification guard: code/config edits were detected but no verification "
                "command was observed in this pass. Run the narrowest relevant verification for the "
                "touched or affected scope first. Prefer related/affected tests, package/module checks, "
                "or a focused runtime probe. Do not run the full suite unless dependency or integration "
                "risk justifies it." + suffix
            ),
            "systemMessage": "High Agency: targeted verification required before stopping",
        })
        return 0

    if not marker:
        clear(bpath)
        clear(vpath)
        return 0

    requested = int(marker.group(1)) if marker.group(1) else DEFAULT_MAX
    limit = min(max(requested, 1), HARD_CAP)
    bdata = load_json(bpath)
    count = max(0, int(bdata.get("continuations", 0)))

    if count >= limit:
        clear(bpath)
        clear(vpath)
        return 0

    count += 1
    save_json(bpath, {"continuations": count, "limit": limit, "updated_at": int(time.time())})
    reset_pass(vpath, vdata)

    if count == limit:
        reason = (
            f"Final bounded-autonomy continuation {count}/{limit}. Continue the same task from the "
            "current repository state. Make the highest-value remaining progress using an independently "
            "verifiable step. Verify the touched or affected scope first and broaden only if risk requires "
            "it. Do not weaken verification and do not emit another high-agency continuation marker. "
            "Finish by reporting what is verified, what remains incomplete, or what is blocked."
        )
    else:
        reason = (
            f"Bounded-autonomy continuation {count}/{limit}. Continue the same task from the current "
            "repository state. Work on the highest-value unresolved acceptance criterion using an "
            "independently verifiable step. Verify the touched or affected scope first; broaden only for "
            "dependency or integration risk. Request another continuation only if this pass produces "
            "meaningful new progress and more actionable work remains. If so, end with exactly "
            f"<!-- high-agency:continue max={limit} -->. Otherwise finish without a marker."
        )

    emit({
        "decision": "block",
        "reason": reason,
        "systemMessage": f"High Agency continuation {count}/{limit}",
    })
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
