from __future__ import annotations

import re

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"/home/[^/\s]+"),
    re.compile(r"C:\\Users\\[^\\\s]+", re.IGNORECASE),
)


def redact_local_paths(text: str) -> str:
    redacted = text
    for pattern in LOCAL_PATH_PATTERNS:
        redacted = pattern.sub("<home>", redacted)
    return redacted
