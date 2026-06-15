from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .audit import audit_target, audit_to_dict
from .detect import detect_project
from .effectiveness import build_effectiveness_assessment
from .indexer import build_index_report
from .readiness import inspect_readiness, readiness_to_dict
from .reports import report_path, relative_to_target
from .update import build_drift_report

SCHEMA_VERSION = "harnessforge.report.v1"
FIRST_AGENT_TASK = "docs/harness/first-agent-task.md"
MANIFEST = "docs/harness/manifest.json"


def build_report(
    target: Path,
    *,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
    max_files: int = 4000,
    require_verify_evidence: bool = False,
) -> dict[str, Any]:
    if max_files <= 0:
        raise ValueError("max-files must be greater than 0")
    profile = detect_project(
        target,
        explicit_package_manager=explicit_package_manager,
        explicit_commands=explicit_commands,
        max_files=max_files,
    )
    readiness = inspect_readiness(
        profile,
        require_verify_evidence=require_verify_evidence,
    )
    audit = audit_target(profile.root)
    drift = build_drift_report(profile.root)
    index = build_index_report(profile)
    effectiveness = build_effectiveness_assessment(profile)
    readiness_payload = readiness_to_dict(readiness)
    audit_payload = audit_to_dict(audit)
    manifest = _read_manifest(profile.root)
    first_agent = _first_agent_task_status(profile.root)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "target": {
            "name": profile.name,
            "root": None,
        },
        "mode": "read_only",
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "detectedStack": profile.stack,
        "readiness": _readiness_summary(readiness_payload),
        "audit": _audit_summary(audit_payload),
        "drift": _drift_summary(drift),
        "index": _index_summary(index),
        "verifyEvidence": readiness_payload["verifyEvidence"],
        "effectiveness": _effectiveness_summary(effectiveness),
        "firstAgentTask": first_agent,
        "platform": _platform_summary(manifest),
        "nextActions": _next_actions(
            readiness_payload,
            audit_payload,
            drift,
            effectiveness,
            first_agent,
        ),
    }
    return payload


def format_report(payload: dict[str, Any]) -> str:
    lines = [
        "# HarnessForge Report",
        "",
        f"- Target: `{payload['target']['name']}`",
        f"- Mode: `{payload['mode']}`",
        "- Commands executed: `false`",
        "- Writes performed: `false`",
        f"- Detected stack: `{payload['detectedStack']}`",
        "",
        "## Readiness",
        "",
        f"- Verdict: `{payload['readiness']['verdict']}`",
        f"- Warnings: {payload['readiness']['warningCount']}",
        f"- Blocked reasons: {payload['readiness']['blockedCount']}",
        f"- Review-required surfaces: {payload['readiness']['reviewRequiredCount']}",
        "",
        "## Audit",
        "",
        f"- Score: {payload['audit']['overall']}/100",
        f"- Bottleneck: `{payload['audit']['bottleneck']}`",
        f"- Failed checks: {len(payload['audit']['failedChecks'])}",
        "",
        "## Generated Drift",
        "",
        f"- Items: {payload['drift']['summary']['items']}",
        f"- Actionable: {payload['drift']['summary']['actionable']}",
        "",
        "## Index Summary",
        "",
        f"- Files: {payload['index']['summary']['fileCount']}",
        f"- Components: {payload['index']['summary']['componentCount']}",
        f"- Manifests: {payload['index']['summary']['manifestCount']}",
        f"- Source-of-truth docs: {payload['index']['summary']['sourceOfTruthCount']}",
        "",
        "## Verify Evidence",
        "",
    ]
    latest = payload["verifyEvidence"]["latest"]
    if latest:
        lines.extend(
            [
                f"- Latest: `{latest['path']}`",
                f"- Verdict: `{latest['verdict'] or 'unknown'}`",
                f"- Mode: `{latest['mode'] or 'unknown'}`",
            ]
        )
    else:
        lines.append("- Latest: none")
    lines.extend(
        [
            f"- Reports: {len(payload['verifyEvidence']['reports'])}",
            "",
            "## Effectiveness Evidence",
            "",
            f"- Verdict: `{payload['effectiveness']['verdict']}`",
            f"- Reports: {payload['effectiveness']['summary']['reports']}",
            "",
            "## First-Agent Task",
            "",
            f"- Status: `{payload['firstAgentTask']['status']}`",
            f"- Path: `{payload['firstAgentTask']['path'] or 'none'}`",
            "",
            "## Platform",
            "",
            f"- Contract: `{payload['platform']['contract']}`",
            "",
            "## Next Actions",
            "",
        ]
    )
    for action in payload["nextActions"]:
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(path_text: str, target: Path, payload: dict[str, Any]) -> str:
    path = report_path(path_text, target)
    if path is None:
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_report(payload), encoding="utf-8")
    return relative_to_target(path, target)


def _readiness_summary(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": readiness["verdict"],
        "warningCount": len(readiness["warnings"]),
        "blockedCount": len(readiness["blockedReasons"]),
        "reviewRequiredCount": len(readiness["reviewRequired"]),
        "warnings": readiness["warnings"],
        "blockedReasons": readiness["blockedReasons"],
        "reviewRequired": readiness["reviewRequired"],
        "nextActions": readiness["nextActions"],
    }


def _audit_summary(audit: dict[str, Any]) -> dict[str, Any]:
    failed_checks = []
    for domain_name, domain in audit["domains"].items():
        for check in domain["checks"]:
            if not check["passed"]:
                failed_checks.append(
                    {
                        "domain": domain_name,
                        "message": check["message"],
                        "detail": check.get("detail", ""),
                    }
                )
    return {
        "overall": audit["overall"],
        "bottleneck": audit["bottleneck"],
        "failedChecks": failed_checks,
        "recommendations": audit["recommendations"],
    }


def _drift_summary(drift: tuple[Any, ...]) -> dict[str, Any]:
    items = [
        {
            "path": item.path,
            "ownership": item.ownership,
            "fileStatus": item.file_status,
            "templateStatus": item.template_status,
            "recommendedAction": item.recommended_action,
            "reason": item.reason,
        }
        for item in drift
    ]
    actionable = [
        item for item in items if item["recommendedAction"] not in {"none", ""}
    ]
    return {
        "summary": {
            "items": len(items),
            "actionable": len(actionable),
        },
        "items": items,
    }


def _index_summary(index: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": index["summary"],
        "warnings": index["warnings"],
        "fileClasses": index["fileClasses"],
        "sourceOfTruth": index["sourceOfTruth"][:10],
        "reviewRequired": index["reviewRequired"][:10],
    }


def _effectiveness_summary(effectiveness: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": effectiveness["verdict"],
        "summary": effectiveness["summary"],
        "blockedReasons": effectiveness["blockedReasons"],
        "warnings": effectiveness["warnings"],
        "nextActions": effectiveness["nextActions"],
    }


def _first_agent_task_status(root: Path) -> dict[str, Any]:
    path = root / FIRST_AGENT_TASK
    if not path.exists():
        return {
            "path": None,
            "status": "absent",
            "reviewRequired": False,
        }
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {
            "path": FIRST_AGENT_TASK,
            "status": "unreadable",
            "reviewRequired": True,
        }
    review_required = "REVIEW REQUIRED" in content
    return {
        "path": FIRST_AGENT_TASK,
        "status": "pending_review" if review_required else "reviewed_or_retired",
        "reviewRequired": review_required,
    }


def _platform_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    source_review = manifest.get("platformSourceReview", {})
    return {
        "contract": str(manifest.get("platformContract", "unknown")),
        "sourceReviewDate": (
            (source_review.get("lastReviewed") or source_review.get("reviewedAt"))
            if isinstance(source_review, dict)
            else None
        ),
        "reviewRequiredBeforePlatformChange": (
            bool(source_review.get("reviewRequiredBeforePlatformChange"))
            if isinstance(source_review, dict)
            else False
        ),
    }


def _read_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _next_actions(
    readiness: dict[str, Any],
    audit: dict[str, Any],
    drift: tuple[Any, ...],
    effectiveness: dict[str, Any],
    first_agent: dict[str, Any],
) -> list[str]:
    actions: list[str] = [
        "Run harnessforge report --target <repo> --markdown-report "
        "docs/harness/evidence/report-<date>.md before release or large harness changes."
    ]
    actions.extend(readiness["nextActions"])
    actions.extend(audit["recommendations"])
    if any(item.recommended_action != "none" for item in drift):
        actions.append(
            "Review generated-file drift with harnessforge update --target <repo> --drift-report."
        )
    actions.extend(effectiveness["nextActions"])
    if first_agent["status"] == "pending_review":
        actions.append(
            "Complete or retire docs/harness/first-agent-task.md after repo-specific harness review."
        )
    return _dedupe(actions)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
