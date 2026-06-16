from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


SCHEMA_VERSION = "harnessforge.tokenEconomicsMetric.v1"
METADATA_REQUIRED = (
    "target",
    "task",
    "agent",
    "harnessProfile",
    "mechanism",
    "context",
    "outcome",
    "evidenceRefs",
    "limitations",
    "promotionStatus",
)


def normalize_codex_jsonl_trace(
    trace_path: Path,
    metadata: Mapping[str, Any],
    *,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    """Normalize a Codex JSONL event stream into the token metric schema."""

    events = _load_jsonl_events(trace_path)
    missing = [field for field in METADATA_REQUIRED if field not in metadata]
    if missing:
        raise ValueError(f"metadata missing required field(s): {', '.join(missing)}")

    record: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "recordedAt": recorded_at
        or _string_or_none(metadata.get("recordedAt"))
        or _utc_now(),
    }
    for field in METADATA_REQUIRED:
        record[field] = copy.deepcopy(metadata[field])
    if "cost" in metadata:
        record["cost"] = copy.deepcopy(metadata["cost"])

    record["tokens"] = _codex_token_summary(events)
    record["trajectory"] = _codex_trajectory_summary(events)
    return record


def load_metadata(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: metadata must be a JSON object")
    return data


def write_metric_record(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load_jsonl_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSON on line {line_number}") from exc
            if not isinstance(event, dict):
                raise ValueError(f"{path}: line {line_number} must be a JSON object")
            events.append(event)
    return events


def _codex_token_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    usage_events = [
        event.get("usage")
        for event in events
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict)
    ]
    first_usage = usage_events[0] if usage_events else {}
    startup_input = _int_or_none(first_usage.get("input_tokens"))

    input_tokens = 0
    cached_input_tokens = 0
    output_tokens = 0
    reasoning_output_tokens = 0
    explicit_total_tokens = 0
    saw_explicit_total = False

    for usage in usage_events:
        input_tokens += _int_or_zero(usage.get("input_tokens"))
        cached_input_tokens += _int_or_zero(usage.get("cached_input_tokens"))
        output_tokens += _int_or_zero(usage.get("output_tokens"))
        reasoning_output_tokens += _int_or_zero(usage.get("reasoning_output_tokens"))
        total = _int_or_none(usage.get("total_tokens"))
        if total is not None:
            explicit_total_tokens += total
            saw_explicit_total = True

    total_tokens = (
        explicit_total_tokens
        if saw_explicit_total
        else input_tokens + output_tokens + reasoning_output_tokens
    )

    return {
        "source": "agent_usage_report",
        "startupInput": startup_input,
        "cacheWriteInput": None,
        "cacheReadInput": cached_input_tokens if usage_events else None,
        "uncachedRepeatedInput": None,
        "output": output_tokens if usage_events else None,
        "reasoningOutput": reasoning_output_tokens if usage_events else None,
        "total": total_tokens if usage_events else None,
    }


def _codex_trajectory_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    tool_events = [
        _tool_text(event)
        for event in events
        if _is_completed_event(event) and _is_tool_event(event)
    ]
    return {
        "turns": sum(1 for event in events if event.get("type") == "turn.completed"),
        "toolCalls": len(tool_events),
        "fileReads": sum(
            1 for text in tool_events if _matches_any(text, _FILE_READ_TERMS)
        ),
        "searchCalls": sum(
            1 for text in tool_events if _matches_any(text, _SEARCH_TERMS)
        ),
        "editCalls": sum(1 for text in tool_events if _matches_any(text, _EDIT_TERMS)),
        "verificationRuns": sum(
            1 for text in tool_events if _matches_any(text, _VERIFICATION_TERMS)
        ),
        "retries": sum(1 for event in events if _is_retry_event(event)),
        "durationSeconds": _duration_seconds(events),
    }


_FILE_READ_TERMS = (
    "read_file",
    "open",
    "cat ",
    "head ",
    "sed ",
    "nl ",
    "view",
)
_SEARCH_TERMS = (
    "rg ",
    "grep ",
    "find ",
    "ripgrep",
    "search_query",
    "web_search",
    "tool_search",
)
_EDIT_TERMS = ("apply_patch", "edit", "file_change", "write_file", "patch")
_VERIFICATION_TERMS = (
    "unittest",
    "pytest",
    "compileall",
    "check_pins",
    "refresh_research",
    "harnessforge audit",
    "harnessforge verify",
    "./init.sh",
    "init.ps1",
)


def _is_tool_event(event: Mapping[str, Any]) -> bool:
    event_type = str(event.get("type", "")).lower()
    if "tool" in event_type:
        return True
    item = event.get("item")
    if isinstance(item, Mapping):
        item_type = str(item.get("type", "")).lower()
        if item_type == "file_change":
            return True
        if "tool" in item_type or "function" in item_type or "command" in item_type:
            return True
        for key in ("name", "tool_name"):
            value = str(item.get(key, "")).lower()
            if value in {"shell", "exec", "apply_patch", "read_file", "write_file"}:
                return True
    return False


def _is_completed_event(event: Mapping[str, Any]) -> bool:
    event_type = str(event.get("type", "")).lower()
    return event_type.endswith("completed")


def _tool_text(event: Mapping[str, Any]) -> str:
    fragments: list[str] = [str(event.get("type", ""))]
    item = event.get("item")
    if isinstance(item, Mapping):
        for key in (
            "type",
            "name",
            "tool_name",
            "command",
            "path",
            "arguments",
            "input",
        ):
            value = item.get(key)
            if value is not None:
                fragments.append(str(value))
    for key in ("name", "tool_name", "command", "path", "arguments", "input"):
        value = event.get(key)
        if value is not None:
            fragments.append(str(value))
    return " ".join(fragments).lower()


def _matches_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _is_retry_event(event: Mapping[str, Any]) -> bool:
    event_type = str(event.get("type", "")).lower()
    if "retry" in event_type:
        return True
    attempt = _int_or_none(event.get("attempt"))
    return attempt is not None and attempt > 1


def _duration_seconds(events: list[dict[str, Any]]) -> float | None:
    durations_ms = [
        _int_or_none(event.get("duration_ms"))
        for event in events
        if _int_or_none(event.get("duration_ms")) is not None
    ]
    if durations_ms:
        return sum(duration for duration in durations_ms if duration is not None) / 1000
    return None


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _int_or_zero(value: object) -> int:
    parsed = _int_or_none(value)
    return parsed if parsed is not None else 0


def _int_or_none(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
