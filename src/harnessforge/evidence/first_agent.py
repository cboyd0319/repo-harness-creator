from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..harness_paths import harness_path
from ..paths import is_absolute_path_text, is_inside_root, path_from_relative_text

SCHEMA_VERSION = "harnessforge.firstAgentReview.v1"
EVIDENCE_PATH = "docs/harness/evidence/first-agent-review.json"
STALE_AFTER_DAYS = 14
VALID_STATUSES = {"pending", "completed", "retired", "blocked"}
VALID_FRESH_SESSION_VALUES = {"verified", "not_applicable"}
REQUIRED_FRESH_SESSION_KEYS = (
    "purpose",
    "organization",
    "startup",
    "verification",
    "currentWork",
    "sourceOfTruth",
)


@dataclass(frozen=True)
class FirstAgentLifecycleReport:
    task_path: str | None
    task_status: str
    task_review_required: bool
    evidence_path: str | None
    evidence_status: str
    lifecycle_status: str
    age_days: int | None
    schema_valid: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_actions: tuple[str, ...]


def analyze_first_agent_lifecycle(
    root: Path,
    files: tuple[str, ...],
) -> FirstAgentLifecycleReport:
    file_set = set(files)
    task_path = harness_path("first_agent_task")
    task_status, task_review_required = _task_status(root, task_path)
    evidence_path = EVIDENCE_PATH if EVIDENCE_PATH in file_set else None
    if evidence_path is None:
        lifecycle_status = "absent" if task_status == "absent" else "pending"
        warnings = (
            (f"first-agent review evidence is missing at {EVIDENCE_PATH}.",)
            if task_status != "absent"
            else ()
        )
        return FirstAgentLifecycleReport(
            task_path=None if task_status == "absent" else task_path,
            task_status=task_status,
            task_review_required=task_review_required,
            evidence_path=None,
            evidence_status="absent",
            lifecycle_status=lifecycle_status,
            age_days=None,
            schema_valid=False,
            blockers=(),
            warnings=warnings,
            next_actions=_next_actions(lifecycle_status, task_path, warnings),
        )

    age_days, stale = _file_age(root / path_from_relative_text(evidence_path))
    evidence_status, schema_valid, blockers, warnings = _read_evidence(
        root,
        evidence_path,
        task_path=task_path,
        task_review_required=task_review_required,
    )
    lifecycle_status = evidence_status
    if evidence_status == "pending" and stale:
        lifecycle_status = "stale"
        warnings.append(
            f"first-agent review evidence is stale ({age_days} days old)."
        )
    return FirstAgentLifecycleReport(
        task_path=None if task_status == "absent" else task_path,
        task_status=task_status,
        task_review_required=task_review_required,
        evidence_path=evidence_path,
        evidence_status=evidence_status,
        lifecycle_status=lifecycle_status,
        age_days=age_days,
        schema_valid=schema_valid,
        blockers=tuple(_dedupe(blockers)),
        warnings=tuple(_dedupe(warnings)),
        next_actions=_next_actions(lifecycle_status, task_path, warnings),
    )


def first_agent_lifecycle_to_dict(
    report: FirstAgentLifecycleReport,
) -> dict[str, Any]:
    return {
        "taskPath": report.task_path,
        "taskStatus": report.task_status,
        "taskReviewRequired": report.task_review_required,
        "evidencePath": report.evidence_path,
        "evidenceStatus": report.evidence_status,
        "status": report.lifecycle_status,
        "ageDays": report.age_days,
        "schemaValid": report.schema_valid,
        "blockers": list(report.blockers),
        "warnings": list(report.warnings),
        "nextActions": list(report.next_actions),
    }


def _task_status(root: Path, relative_path: str) -> tuple[str, bool]:
    path = root / path_from_relative_text(relative_path)
    if not path.exists():
        return "absent", False
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return "unreadable", True
    review_required = "REVIEW REQUIRED" in content
    return "pending_review" if review_required else "reviewed_or_retired", review_required


def _read_evidence(
    root: Path,
    relative_path: str,
    *,
    task_path: str,
    task_review_required: bool,
) -> tuple[str, bool, list[str], list[str]]:
    path = root / path_from_relative_text(relative_path)
    blockers: list[str] = []
    warnings: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "invalid", False, ["first-agent review evidence is invalid JSON."], []
    if not isinstance(payload, dict):
        return "invalid", False, ["first-agent review evidence must be an object."], []

    if payload.get("schemaVersion") != SCHEMA_VERSION:
        blockers.append("first-agent evidence schemaVersion is not recognized.")
    status = payload.get("status")
    if not isinstance(status, str) or status not in VALID_STATUSES:
        blockers.append("first-agent evidence status is not recognized.")
        status = "invalid"
    if payload.get("taskPath") != task_path:
        blockers.append("first-agent evidence taskPath does not match generated task.")

    if status == "pending":
        return "pending", not blockers, blockers, warnings
    if status == "blocked":
        blockers.append("first-agent review is blocked.")
        return "blocked", not blockers, blockers, warnings
    if status in {"completed", "retired"}:
        _validate_completed(root, payload, blockers, warnings)
        if task_review_required:
            warnings.append(
                "first-agent task still contains REVIEW REQUIRED after review evidence."
            )
        if blockers:
            return "incomplete", False, blockers, warnings
        return status, True, blockers, warnings
    return "invalid", False, blockers, warnings


def _validate_completed(
    root: Path,
    payload: dict[str, Any],
    blockers: list[str],
    warnings: list[str],
) -> None:
    if not _string(payload.get("reviewedAt")):
        blockers.append("completed first-agent evidence requires reviewedAt.")
    reviewed_by = payload.get("reviewedBy")
    if not isinstance(reviewed_by, list) or not any(_string(item) for item in reviewed_by):
        blockers.append("completed first-agent evidence requires reviewedBy.")
    fresh_session = payload.get("freshSession")
    if not isinstance(fresh_session, dict):
        blockers.append("completed first-agent evidence requires freshSession.")
    else:
        for key in REQUIRED_FRESH_SESSION_KEYS:
            value = fresh_session.get(key)
            if value not in VALID_FRESH_SESSION_VALUES:
                blockers.append(f"freshSession.{key} must be verified or not_applicable.")

    updated = payload.get("updatedSurfaces")
    if not isinstance(updated, list) or not updated:
        warnings.append("completed first-agent evidence does not list updated surfaces.")
    else:
        for ref in updated:
            if not _is_target_relative(root, ref):
                blockers.append("updatedSurfaces must be target-relative paths.")

    verification = payload.get("verification")
    if not isinstance(verification, dict):
        blockers.append("completed first-agent evidence requires verification.")
    else:
        evidence_refs = verification.get("evidenceRefs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            warnings.append("completed first-agent evidence has no verification evidenceRefs.")
        else:
            for ref in evidence_refs:
                if not _is_target_relative(root, ref):
                    blockers.append("verification evidenceRefs must be target-relative paths.")

    remaining = payload.get("remainingReview")
    if isinstance(remaining, list) and remaining:
        warnings.append("completed first-agent evidence still lists remaining review.")
    retirement = payload.get("retirement")
    if isinstance(retirement, dict) and retirement.get("taskRetired") is not True:
        warnings.append("completed first-agent evidence has not retired the task.")


def _is_target_relative(root: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if is_absolute_path_text(value):
        return False
    target = root / path_from_relative_text(value)
    return is_inside_root(target, root)


def _file_age(path: Path) -> tuple[int, bool]:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    updated = datetime.fromtimestamp(mtime, UTC)
    now = datetime.now(UTC)
    age_days = max(0, int((now - updated).total_seconds() // 86400))
    return age_days, age_days > STALE_AFTER_DAYS


def _next_actions(
    lifecycle_status: str,
    task_path: str,
    warnings: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    actions: list[str] = []
    if lifecycle_status in {"pending", "stale", "absent"}:
        actions.append(
            f"Complete {task_path} and record {EVIDENCE_PATH} before treating the "
            "generated harness as reviewed."
        )
    if lifecycle_status == "stale":
        actions.append("Refresh stale first-agent review evidence.")
    if lifecycle_status in {"invalid", "incomplete", "blocked"}:
        actions.append("Fix first-agent review evidence before relying on it.")
    if warnings and lifecycle_status in {"completed", "retired"}:
        actions.append("Review first-agent lifecycle warnings before promotion.")
    return tuple(_dedupe(actions))


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _dedupe(items: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
