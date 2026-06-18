from __future__ import annotations

import re
from pathlib import Path

LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[^/\r\n]+"),
    re.compile(r"/home/[^/\r\n]+"),
    re.compile(r"[A-Z]:\\Users\\[^\\\r\n]+", re.IGNORECASE),
)

SECRET_ASSIGNMENT_RE = re.compile(
    r"\b("
    r"[A-Z0-9_.-]*"
    r"(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|PASSWD|PWD|CREDENTIAL|"
    r"PRIVATE[_-]?KEY|ACCESS[_-]?TOKEN|REFRESH[_-]?TOKEN|CLIENT[_-]?SECRET)"
    r"[A-Z0-9_.-]*"
    r"\s*[:=]\s*)"
    r"([\"']?)"
    r"([^\s\"'\r\n,;]+)"
    r"([\"']?)",
    re.IGNORECASE,
)

AUTHORIZATION_VALUE_RE = re.compile(
    r"\b(authorization\s*[:=]\s*(?:bearer|basic|token)\s+)([^\s,;]+)",
    re.IGNORECASE,
)

SAFE_SECRET_VALUES = {
    "",
    "***",
    "****",
    "<redacted>",
    "<secret>",
    "redacted",
    "masked",
    "null",
    "none",
    "false",
    "true",
}


def redact_local_paths(text: str) -> str:
    redacted = text
    for pattern in (*LOCAL_PATH_PATTERNS, *_current_home_patterns()):
        redacted = pattern.sub("<home>", redacted)
    redacted = SECRET_ASSIGNMENT_RE.sub(_redact_secret_assignment, redacted)
    redacted = AUTHORIZATION_VALUE_RE.sub(r"\1<redacted>", redacted)
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


def _redact_secret_assignment(match: re.Match[str]) -> str:
    prefix, quote, value, closing_quote = match.groups()
    normalized = value.strip().lower()
    if (
        normalized in SAFE_SECRET_VALUES
        or value.startswith("${{")
        or value.startswith("$")
    ):
        return match.group(0)
    return f"{prefix}{quote}<redacted>{closing_quote}"
