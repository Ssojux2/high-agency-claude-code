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
                if not isinstance(message, dict):
                    continue

                if message.get("role") != "assistant":
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
    digest = hashlib.sha256(
        transcript_path.encode("utf-8", "replace")
    ).hexdigest()[:24]
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
            {
                "continuations": count,
                "limit": limit,
                "updated_at": int(time.time()),
            },
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

    transcript_path = Path(transcript_raw)
    message = last_assistant_message(transcript_path)

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

    reason = (
        f"Bounded-autonomy continuation {count}/{limit}. "
        "Continue the same task from the current repository state. "
        "Work on the highest-value unresolved acceptance criterion. "
        "Use fresh evidence, do not repeat an unchanged failed approach, "
        "and run relevant verification before stopping. "
        "If more actionable work remains, end with exactly "
        f"<!-- high-agency:continue max={limit} -->. "
        "If complete or blocked, finish without a continuation marker "
        "and report the evidence or blocker."
    )

    emit(
        {
            "decision": "block",
            "reason": reason,
            "systemMessage": f"High Agency continuation {count}/{limit}",
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
