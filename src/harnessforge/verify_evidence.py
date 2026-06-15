from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .paths import path_from_relative_text

VERIFY_EVIDENCE_PREFIX = "docs/harness/evidence/"
VERIFY_SCHEMA_VERSION = "harnessforge.verify.v1"
STALE_AFTER_DAYS = 14


@dataclass(frozen=True)
class VerifyEvidenceItem:
    path: str
    schema_valid: bool
    mode: str | None
    verdict: str | None
    recorded_at: str | None
    updated_at: str
    age_days: int
    summary: dict[str, Any]
    issues: tuple[str, ...]


@dataclass(frozen=True)
class VerifyEvidenceReport:
    latest: VerifyEvidenceItem | None
    reports: tuple[VerifyEvidenceItem, ...]
    warnings: tuple[str, ...]
    next_actions: tuple[str, ...]


def analyze_verify_evidence(root: Path, files: tuple[str, ...]) -> VerifyEvidenceReport:
    reports = tuple(
        item
        for item in (_read_verify_report(root, file) for file in sorted(files))
        if item is not None
    )
    valid_reports = tuple(item for item in reports if item.schema_valid)
    latest = max(valid_reports, key=_sort_timestamp, default=None)
    warnings: list[str] = []
    for item in reports:
        if not item.schema_valid:
            warnings.append(f"invalid verify evidence report at {item.path}.")
            continue
        if item.verdict in {"failed", "blocked"}:
            warnings.append(
                f"stored verify evidence report {item.path} verdict is {item.verdict}."
            )
        if item.summary.get("timedOut", 0):
            warnings.append(
                f"stored verify evidence report {item.path} includes timed_out checks."
            )
    if latest and "stale" in latest.issues:
        warnings.append(
            f"latest verify evidence report {latest.path} is stale "
            f"({latest.age_days} days old)."
        )

    next_actions: list[str] = []
    if warnings:
        next_actions.append(
            "Review stored verify evidence before relying on readiness or release signals."
        )
    return VerifyEvidenceReport(
        latest=latest,
        reports=reports,
        warnings=tuple(_dedupe(warnings)),
        next_actions=tuple(next_actions),
    )


def verify_evidence_report_to_dict(report: VerifyEvidenceReport) -> dict[str, Any]:
    return {
        "latest": (
            verify_evidence_item_to_dict(report.latest)
            if report.latest is not None
            else None
        ),
        "reports": [verify_evidence_item_to_dict(item) for item in report.reports],
    }


def verify_evidence_item_to_dict(item: VerifyEvidenceItem) -> dict[str, Any]:
    return {
        "path": item.path,
        "schemaValid": item.schema_valid,
        "mode": item.mode,
        "verdict": item.verdict,
        "recordedAt": item.recorded_at,
        "updatedAt": item.updated_at,
        "ageDays": item.age_days,
        "summary": item.summary,
        "issues": list(item.issues),
    }


def _read_verify_report(root: Path, file: str) -> VerifyEvidenceItem | None:
    if not _is_verify_evidence_file(file):
        return None
    path = root / path_from_relative_text(file)
    updated_at, age_days, stale = _file_age(path)
    issues: list[str] = []
    if stale:
        issues.append("stale")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        issues.append("invalid-json")
        return VerifyEvidenceItem(
            path=file,
            schema_valid=False,
            mode=None,
            verdict=None,
            recorded_at=None,
            updated_at=updated_at,
            age_days=age_days,
            summary={},
            issues=tuple(issues),
        )
    if not isinstance(payload, dict):
        issues.append("invalid-payload")
        return VerifyEvidenceItem(
            path=file,
            schema_valid=False,
            mode=None,
            verdict=None,
            recorded_at=None,
            updated_at=updated_at,
            age_days=age_days,
            summary={},
            issues=tuple(issues),
        )
    mode = payload.get("mode")
    verdict = payload.get("verdict")
    execution = payload.get("execution")
    checks = payload.get("checks")
    schema_valid = payload.get("schemaVersion") == VERIFY_SCHEMA_VERSION
    if not schema_valid:
        issues.append("invalid-schema")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        summary = {}
        schema_valid = False
        issues.append("invalid-summary")
    if not isinstance(mode, str) or mode not in {"plan", "run"}:
        schema_valid = False
        issues.append("invalid-mode")
    if not isinstance(verdict, str):
        schema_valid = False
        issues.append("invalid-verdict")
    if not isinstance(execution, dict):
        schema_valid = False
        issues.append("invalid-execution")
    if not isinstance(checks, list):
        schema_valid = False
        issues.append("invalid-checks")
    recorded_at = None
    if isinstance(execution, dict):
        ended_at = execution.get("endedAt")
        started_at = execution.get("startedAt")
        recorded_at = ended_at if isinstance(ended_at, str) else None
        if recorded_at is None and isinstance(started_at, str):
            recorded_at = started_at
    if recorded_at is None:
        recorded_at = updated_at
    return VerifyEvidenceItem(
        path=file,
        schema_valid=schema_valid,
        mode=mode if isinstance(mode, str) else None,
        verdict=verdict if isinstance(verdict, str) else None,
        recorded_at=recorded_at,
        updated_at=updated_at,
        age_days=age_days,
        summary=dict(summary),
        issues=tuple(_dedupe(issues)),
    )


def _is_verify_evidence_file(file: str) -> bool:
    path = Path(file)
    return (
        file.startswith(VERIFY_EVIDENCE_PREFIX)
        and path.name.startswith("verify")
        and path.suffix.lower() == ".json"
    )


def _file_age(path: Path) -> tuple[str, int, bool]:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    updated = datetime.fromtimestamp(mtime, UTC)
    now = datetime.now(UTC)
    age_days = max(0, int((now - updated).total_seconds() // 86400))
    return _format_timestamp(updated), age_days, age_days > STALE_AFTER_DAYS


def _sort_timestamp(item: VerifyEvidenceItem) -> str:
    return item.recorded_at or item.updated_at


def _format_timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
