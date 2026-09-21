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

def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")

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

def state_directory() -> Path:
    return Path(tempfile.gettempdir()) / "high-agency-claude-code"

def state_path(transcript_path: str) -> Path:
    digest = hashlib.sha256(transcript_path.encode("utf-8", "replace")).hexdigest()[:24]
    return state_directory() / f"{digest}.json"

def cleanup_old_states() -> None:
    directory = state_directory()
    if not directory.exists():
        return
    cutoff = time.time() - STATE_TTL_SECONDS
    for path in directory.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
        except OSError:
            pass

def load_count(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return max(0, int(data.get("continuations", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0

def save_count(path: Path, count: int, limit: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {"continuations": count, "limit": limit, "updated_at": int(time.time())},
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    tmp.replace(path)

def clear_state(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    transcript_raw = payload.get("transcript_path")
    if not isinstance(transcript_raw, str) or not transcript_raw:
        return 0

    message = last_assistant_message(Path(transcript_raw))
    cleanup_old_states()
    path = state_path(transcript_raw)

    if not message:
        clear_state(path)
        return 0

    match = MARKER_RE.search(message)
    if not match:
        clear_state(path)
        return 0

    requested = int(match.group(1)) if match.group(1) else DEFAULT_MAX
    limit = min(max(requested, 1), HARD_CAP)
    count = load_count(path)

    if count >= limit:
        clear_state(path)
        return 0

    count += 1
    save_count(path, count, limit)

    if count == limit:
        reason = (
            f"Final bounded-autonomy continuation {count}/{limit}. Continue the same task from "
            "the current repository state. Make the highest-value remaining progress using an "
            "independently verifiable step, run fresh relevant verification, and do not weaken "
            "verification to manufacture success. Do not emit another high-agency continuation "
            "marker. Finish by reporting what is verified, what remains incomplete, or what is blocked."
        )
    else:
        reason = (
            f"Bounded-autonomy continuation {count}/{limit}. Continue the same task from the "
            "current repository state. Work on the highest-value unresolved acceptance criterion "
            "using an independently verifiable step. Use fresh evidence, do not repeat an unchanged "
            "failed approach, and do not weaken verification. Request another continuation only if "
            "this pass produces meaningful new progress and more actionable work remains. If so, "
            f"end with exactly <!-- high-agency:continue max={limit} -->. If complete, blocked, or "
            "no meaningful new progress was made, finish without a marker and report the evidence."
        )

    emit({
        "decision": "block",
        "reason": reason,
        "systemMessage": f"High Agency continuation {count}/{limit}",
    })
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
