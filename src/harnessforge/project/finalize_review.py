from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from ..core.harness_paths import harness_path
from ..core.models import WriteResult
from ..core.paths import is_absolute_path_text, is_inside_root, path_from_relative_text
from ..evidence.first_agent import EVIDENCE_PATH, SCHEMA_VERSION
from ..evidence.high_risk_acceptance import (
    ACCEPTED_REVIEW_STATUSES,
    ACCEPTED_SURFACE_DECISIONS,
)
from .detect import detect_project
from .readiness import REVIEW_STATUS_PENDING, ReadinessReport, inspect_readiness

REVIEW_FINALIZATION_SCHEMA_VERSION = "harnessforge.reviewFinalization.v1"
DEFAULT_REVIEWER = "maintainer"


@dataclass(frozen=True)
class FinalizationPlan:
    payload: dict[str, Any]
    writes: tuple[WriteResult, ...]
    changed_files: int


def build_review_finalization_plan(
    target: Path,
    *,
    apply: bool,
    accept_detected_high_risk: bool,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
    reviewed_by: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
) -> FinalizationPlan:
    profile = detect_project(
        target,
        explicit_package_manager=explicit_package_manager,
        explicit_commands=explicit_commands,
    )
    readiness = inspect_readiness(profile)
    detected_surfaces = _detected_high_risk_surfaces(readiness)
    if detected_surfaces and apply and not accept_detected_high_risk:
        raise ValueError(
            "review finalization detected high-risk surfaces; rerun with "
            "--accept-detected-high-risk to record accepted advisory evidence"
        )

    now = _now_text()
    reviewers = tuple(item.strip() for item in reviewed_by if item.strip()) or (
        DEFAULT_REVIEWER,
    )
    refs = _evidence_refs(profile.root, evidence_refs)
    preview = _build_preview(
        profile.root,
        readiness=readiness,
        detected_surfaces=detected_surfaces,
        accept_detected_high_risk=accept_detected_high_risk,
        reviewed_by=reviewers,
        evidence_refs=refs,
        now=now,
    )
    planned = _planned_writes(profile.root, preview)
    applied: tuple[WriteResult, ...] = ()
    if apply:
        applied = _apply_preview(profile.root, preview)
    changed_files = sum(
        1 for item in applied if item.status in {"updated", "written"}
    )

    payload = {
        "schemaVersion": REVIEW_FINALIZATION_SCHEMA_VERSION,
        "mode": "apply" if apply else "dry_run",
        "target": {
            "name": profile.name,
            "root": None,
        },
        "detectedStack": profile.stack,
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": bool(apply and applied),
        },
        "review": {
            "reviewedAt": now,
            "reviewedBy": list(reviewers),
            "evidenceRefs": list(refs),
            "acceptDetectedHighRisk": accept_detected_high_risk,
            "requiresHighRiskAcceptanceFlag": bool(
                detected_surfaces and not accept_detected_high_risk
            ),
        },
        "readinessBefore": {
            "verdict": readiness.verdict,
            "reviewRequiredCount": len(readiness.review_required),
            "acceptedHighRiskSurfaces": len(
                readiness.high_risk_acceptance.accepted_surfaces
            ),
        },
        "highRiskSurfaces": [_surface_to_dict(item) for item in detected_surfaces],
        "plannedWrites": [_write_to_dict(profile.root, item) for item in planned],
        "appliedWrites": [_write_to_dict(profile.root, item) for item in applied],
        "changedFiles": changed_files,
    }
    return FinalizationPlan(
        payload=payload,
        writes=applied if apply else planned,
        changed_files=changed_files,
    )


def format_review_finalization_plan(payload: dict[str, Any]) -> str:
    lines = [
        "HarnessForge Review Finalization",
        f"Mode: {payload['mode']}",
        f"Target: {payload['target']['name']}",
        f"Readiness before: {payload['readinessBefore']['verdict']}",
        "High-risk surfaces to accept: "
        f"{len(payload['highRiskSurfaces'])}",
        f"Writes performed: {str(payload['execution']['writesPerformed']).lower()}",
    ]
    if payload["review"]["requiresHighRiskAcceptanceFlag"]:
        lines.append(
            "Requires --accept-detected-high-risk before apply because "
            "unresolved high-risk surfaces were detected."
        )
    lines.extend(["", "Planned writes:"])
    for write in payload["plannedWrites"]:
        lines.append(f"  - {write['status'].upper()} {write['path']} ({write['reason']})")
    if payload["appliedWrites"]:
        lines.extend(["", "Applied writes:"])
        for write in payload["appliedWrites"]:
            lines.append(
                f"  - {write['status'].upper()} {write['path']} ({write['reason']})"
            )
    if payload["highRiskSurfaces"]:
        lines.extend(["", "High-risk surfaces:"])
        for surface in payload["highRiskSurfaces"]:
            lines.append(
                f"  - {surface['path']}: {surface['category']} "
                f"({surface['decision']})"
            )
    return "\n".join(lines).rstrip() + "\n"


def _build_preview(
    root: Path,
    *,
    readiness: ReadinessReport,
    detected_surfaces: tuple[dict[str, str], ...],
    accept_detected_high_risk: bool,
    reviewed_by: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    now: str,
) -> dict[str, str]:
    task_path = harness_path("first_agent_task")
    evidence_payload = _finalized_evidence_payload(
        root,
        readiness=readiness,
        task_path=task_path,
        detected_surfaces=detected_surfaces,
        accept_detected_high_risk=accept_detected_high_risk,
        reviewed_by=reviewed_by,
        evidence_refs=evidence_refs,
        now=now,
    )
    task_text = _retired_task_text(root, task_path)
    preview = {
        EVIDENCE_PATH: f"{json.dumps(evidence_payload, indent=2)}\n",
    }
    if task_text is not None:
        preview[task_path] = task_text
    manifest_text = _finalized_manifest_text(root, preview, now=now)
    if manifest_text is not None:
        preview[harness_path("manifest")] = manifest_text
    return preview


def _finalized_evidence_payload(
    root: Path,
    *,
    readiness: ReadinessReport,
    task_path: str,
    detected_surfaces: tuple[dict[str, str], ...],
    accept_detected_high_risk: bool,
    reviewed_by: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    now: str,
) -> dict[str, Any]:
    payload = _read_json(root, EVIDENCE_PATH)
    if not isinstance(payload, dict):
        payload = {}
    payload["schemaVersion"] = SCHEMA_VERSION
    payload["status"] = "retired"
    payload["reviewedAt"] = now
    payload["reviewedBy"] = list(
        _dedupe([*_payload_reviewers(payload), *reviewed_by])
    )
    payload["taskPath"] = task_path
    payload["freshSession"] = {
        key: "verified"
        for key in (
            "purpose",
            "organization",
            "startup",
            "verification",
            "currentWork",
            "sourceOfTruth",
        )
    }
    payload["updatedSurfaces"] = _updated_surfaces(
        task_path,
        EVIDENCE_PATH,
        detected_surfaces,
    )
    payload["verification"] = {
        "commands": [
            command
            for command in readiness.runnable_checks
            if not command.startswith("REVIEW REQUIRED:")
        ],
        "evidenceRefs": list(evidence_refs),
    }
    if accept_detected_high_risk:
        payload["highRiskSurfaceReview"] = {
            "status": "accepted_advisory",
            "reviewedAt": now,
            "surfaces": _merged_surfaces(
                payload.get("highRiskSurfaceReview"),
                detected_surfaces,
            ),
            "evidenceRefs": list(evidence_refs),
        }
    elif not isinstance(payload.get("highRiskSurfaceReview"), dict):
        payload["highRiskSurfaceReview"] = {
            "status": "pending",
            "reviewedAt": None,
            "surfaces": [],
            "evidenceRefs": [],
        }
    payload["remainingReview"] = []
    payload["retirement"] = {
        "taskRetired": True,
        "reason": "Maintainer finalized the first-agent harness review.",
    }
    return payload


def _payload_reviewers(payload: dict[str, Any]) -> list[str]:
    reviewers = payload.get("reviewedBy")
    if not isinstance(reviewers, list):
        return []
    return [item.strip() for item in reviewers if isinstance(item, str) and item.strip()]


def _retired_task_text(root: Path, task_path: str) -> str | None:
    path = root / path_from_relative_text(task_path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    lines = text.splitlines()
    replacement = [
        "Status: retired after first-agent review.",
        "",
        "Maintainers accepted the repo-specific harness guidance. Evidence is",
        f"recorded in `{EVIDENCE_PATH}`.",
    ]
    if len(lines) >= 3 and lines[2].startswith("REVIEW REQUIRED:"):
        end = 2
        while end < len(lines) and lines[end].strip():
            end += 1
        lines = [*lines[:2], *replacement, *lines[end:]]
        return "\n".join(lines).rstrip() + "\n"
    return text.replace("REVIEW REQUIRED: ", "").rstrip() + "\n"


def _finalized_manifest_text(
    root: Path,
    preview: dict[str, str],
    *,
    now: str,
) -> str | None:
    manifest_path = harness_path("manifest")
    manifest = _read_json(root, manifest_path)
    if not isinstance(manifest, dict):
        return None
    review_required = manifest.get("reviewRequired")
    if isinstance(review_required, list):
        manifest["reviewRequired"] = [
            item
            for item in review_required
            if item not in {harness_path("first_agent_task"), EVIDENCE_PATH}
        ]
    snippets = manifest.get("requiredHarnessSnippets")
    if isinstance(snippets, dict):
        _replace_snippet(
            snippets,
            harness_path("first_agent_task"),
            remove={"REVIEW REQUIRED"},
            add={"Status: retired"},
        )
        _replace_snippet(
            snippets,
            EVIDENCE_PATH,
            remove={"pending", "REVIEW REQUIRED"},
            add={"retired", "highRiskSurfaceReview"},
        )
        if "accepted_advisory" in preview[EVIDENCE_PATH]:
            _replace_snippet(
                snippets,
                EVIDENCE_PATH,
                remove=set(),
                add={"accepted_advisory"},
            )
    generated = manifest.get("generatedFiles")
    if isinstance(generated, dict):
        for relative_path in (harness_path("first_agent_task"), EVIDENCE_PATH):
            metadata = generated.get(relative_path)
            if not isinstance(metadata, dict) or relative_path not in preview:
                continue
            metadata["ownership"] = "project-owned"
            metadata["reviewRequired"] = False
            metadata["writeStatus"] = "review-finalized"
            metadata["reviewStatus"] = "retired"
            metadata["contentSha256"] = sha256(
                preview[relative_path].encode("utf-8")
            ).hexdigest()
    manifest["reviewFinalization"] = {
        "status": "retired",
        "finalizedAt": now,
        "firstAgentTaskRetired": harness_path("first_agent_task") in preview,
        "acceptedHighRiskSurfaceCount": _accepted_surface_count(
            preview[EVIDENCE_PATH]
        ),
    }
    return f"{json.dumps(manifest, separators=(',', ':'))}\n"


def _replace_snippet(
    snippets: dict[str, Any],
    path: str,
    *,
    remove: set[str],
    add: set[str],
) -> None:
    values = snippets.get(path)
    if not isinstance(values, list):
        return
    result = [item for item in values if item not in remove]
    for item in sorted(add):
        if item not in result:
            result.append(item)
    snippets[path] = result


def _planned_writes(root: Path, preview: dict[str, str]) -> tuple[WriteResult, ...]:
    writes: list[WriteResult] = []
    for relative_path in sorted(preview):
        path = _target_path(root, relative_path)
        status = "would_update" if path.exists() else "would_write"
        writes.append(WriteResult(path=path, status=status, reason="review-finalize"))
    return tuple(writes)


def _apply_preview(root: Path, preview: dict[str, str]) -> tuple[WriteResult, ...]:
    writes: list[WriteResult] = []
    for relative_path in sorted(preview):
        path = _target_path(root, relative_path)
        before = path.read_text(encoding="utf-8") if path.exists() else None
        after = preview[relative_path]
        if before == after:
            writes.append(
                WriteResult(path=path, status="unchanged", reason="review-finalize")
            )
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(after, encoding="utf-8")
        writes.append(
            WriteResult(
                path=path,
                status="updated" if before is not None else "written",
                reason="review-finalize",
            )
        )
    return tuple(writes)


def _target_path(root: Path, relative_path: str) -> Path:
    if is_absolute_path_text(relative_path):
        raise ValueError(f"review finalization path must be target-relative: {relative_path}")
    path = root / path_from_relative_text(relative_path)
    if not is_inside_root(path, root):
        raise ValueError(f"review finalization path escapes target: {relative_path}")
    return path


def _detected_high_risk_surfaces(
    readiness: ReadinessReport,
) -> tuple[dict[str, str], ...]:
    result: list[dict[str, str]] = []
    high_risk_sources = {
        "instruction-files",
        "workflow-inventory",
        "governance-inventory",
    }
    for item in readiness.review_surfaces:
        if item.status != REVIEW_STATUS_PENDING or item.source not in high_risk_sources:
            continue
        result.append(_surface(item.path, item.category))
    return tuple(_dedupe_surfaces(result))


def _surface(path: str, category: str) -> dict[str, str]:
    return {
        "path": path,
        "category": category,
        "decision": "accepted_advisory",
    }


def _merged_surfaces(
    existing_review: Any,
    detected_surfaces: tuple[dict[str, str], ...],
) -> list[dict[str, str]]:
    existing: list[dict[str, str]] = []
    if isinstance(existing_review, dict) and existing_review.get(
        "status"
    ) in ACCEPTED_REVIEW_STATUSES:
        surfaces = existing_review.get("surfaces")
        if isinstance(surfaces, list):
            for item in surfaces:
                if not isinstance(item, dict):
                    continue
                path = item.get("path")
                category = item.get("category")
                decision = item.get("decision")
                if (
                    isinstance(path, str)
                    and isinstance(category, str)
                    and decision in ACCEPTED_SURFACE_DECISIONS
                ):
                    existing.append(
                        {
                            "path": path,
                            "category": category,
                            "decision": str(decision),
                        }
                    )
    return _dedupe_surfaces([*existing, *detected_surfaces])


def _updated_surfaces(
    task_path: str,
    evidence_path: str,
    detected_surfaces: tuple[dict[str, str], ...],
) -> list[str]:
    values = [
        task_path,
        evidence_path,
        harness_path("manifest"),
        *(surface["path"] for surface in detected_surfaces),
    ]
    return _dedupe(values)


def _accepted_surface_count(evidence_text: str) -> int:
    try:
        payload = json.loads(evidence_text)
    except json.JSONDecodeError:
        return 0
    review = payload.get("highRiskSurfaceReview")
    if not isinstance(review, dict):
        return 0
    surfaces = review.get("surfaces")
    return len(surfaces) if isinstance(surfaces, list) else 0


def _read_json(root: Path, relative_path: str) -> Any:
    path = _target_path(root, relative_path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _evidence_refs(root: Path, values: tuple[str, ...]) -> tuple[str, ...]:
    refs = tuple(item.strip() for item in values if item.strip())
    for ref in refs:
        _target_path(root, ref)
    return refs or ("docs/harness/evidence/evidence-log.md",)


def _write_to_dict(root: Path, write: WriteResult) -> dict[str, str]:
    return {
        "path": write.path.resolve().relative_to(root.resolve()).as_posix(),
        "status": write.status,
        "reason": write.reason,
    }


def _surface_to_dict(surface: dict[str, str]) -> dict[str, str]:
    return {
        "path": surface["path"],
        "category": surface["category"],
        "decision": surface["decision"],
    }


def _dedupe_surfaces(values: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in values:
        path = item["path"]
        if path in seen:
            continue
        seen.add(path)
        result.append(item)
    return result


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _now_text() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
