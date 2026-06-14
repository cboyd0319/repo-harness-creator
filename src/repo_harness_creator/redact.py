from __future__ import annotations

import re
from pathlib import Path

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\r\n]+"),
    re.compile(r"/home/[^/\r\n]+"),
    re.compile(r"[A-Z]:\\Users\\[^\\\r\n]+", re.IGNORECASE),
)


def redact_local_paths(text: str) -> str:
    redacted = text
    for pattern in (*LOCAL_PATH_PATTERNS, *_current_home_patterns()):
        redacted = pattern.sub("<home>", redacted)
    return redacted


def _current_home_patterns() -> tuple[re.Pattern[str], ...]:
    try:
        home = str(Path.home())
    except RuntimeError:
        return ()
    if not home or home == ".":
        return ()
    flags = re.IGNORECASE if "\\" in home else 0
    return (re.compile(re.escape(home), flags),)
