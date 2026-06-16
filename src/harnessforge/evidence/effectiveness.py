from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.models import ProjectProfile
from ..core.paths import is_absolute_path_text, is_inside_root, path_from_relative_text

ASSESSMENT_SCHEMA_VERSION = "harnessforge.effectivenessAssessment.v1"
EVIDENCE_SCHEMA_VERSION = "harnessforge.effectivenessEvidence.v1"
EVIDENCE_PREFIX = "docs/harness/evidence/"
EVIDENCE_NAME_PREFIX = "effectiveness"
VALID_CLAIM_VERDICTS = {
    "candidate_better",
    "candidate_not_better",
    "inconclusive",
    "blocked",
}
VALID_PROMOTION_STATUSES = {"proposal", "promoted", "rejected", "deferred"}
VALID_REPLAY_TYPES = {"live", "counterfactual_replay", "frozen_replay"}
VALID_METRIC_DIRECTIONS = {"higher_is_better", "lower_is_better"}
REQUIRED_TOP_LEVEL = (
    "schemaVersion",
    "claim",
    "target",
    "candidate",
    "baseline",
    "evaluation",
    "metrics",
    "safety",
    "cost",
    "evidence",
    "promotion",
)


def build_effectiveness_assessment(
    profile: ProjectProfile,
    *,
    evidence_paths: tuple[str, ...] = (),
) -> dict[str, Any]:
    paths = (
        _explicit_evidence_paths(profile.root, evidence_paths)
        if evidence_paths
        else _detected_evidence_paths(profile.files)
    )
    reports = [
        _read_effectiveness_report(profile.root, relative)
        for relative in sorted(dict.fromkeys(paths))
    ]
    summary = _summary(reports)
    blocked_reasons = _blocked_reasons(reports)
    warnings = _warnings(reports)
    return {
        "schemaVersion": ASSESSMENT_SCHEMA_VERSION,
        "target": {
            "name": profile.name,
            "root": None,
        },
        "mode": "read_only",
        "verdict": _verdict(reports),
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "summary": summary,
        "reports": reports,
        "blockedReasons": blocked_reasons,
        "warnings": warnings,
        "nextActions": _next_actions(reports, blocked_reasons, warnings),
    }


def format_effectiveness_assessment(report: dict[str, Any]) -> str:
    lines = [
        f"Effectiveness assessment: {report['verdict']}",
        f"Reports: {report['summary']['reports']}",
        "",
    ]
    _append_section(lines, "Blocked reasons", report["blockedReasons"])
    _append_section(lines, "Warnings", report["warnings"])
    if report["reports"]:
        lines.append("Evidence reports:")
        for item in report["reports"]:
            claim = item["claim"]
            lines.append(
                f"  - {item['path']}: {item['assessmentStatus']}, "
                f"claim={claim['id'] or 'unknown'}, "
                f"verdict={claim['verdict'] or 'unknown'}"
            )
            if item["primaryMetric"]:
                metric = item["primaryMetric"]
                lines.append(
                    f"    primary: {metric['name']} delta={metric['delta']}"
                )
            for blocker in item["blockers"]:
                lines.append(f"    blocker: {blocker}")
    _append_section(lines, "Next actions", report["nextActions"])
    return "\n".join(lines).rstrip()


def _read_effectiveness_report(root: Path, relative: str) -> dict[str, Any]:
    path = root / path_from_relative_text(relative)
    if not is_inside_root(path, root):
        return _invalid_report(relative, ("path escapes target root",))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return _invalid_report(relative, ("invalid json",))
    if not isinstance(payload, dict):
        return _invalid_report(relative, ("payload must be an object",))

    blockers, warnings = _evaluate_payload(payload)
    claim = payload.get("claim") if isinstance(payload.get("claim"), dict) else {}
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
    primary = metrics.get("primary") if isinstance(metrics.get("primary"), dict) else {}
    promotion = (
        payload.get("promotion") if isinstance(payload.get("promotion"), dict) else {}
    )
    schema_valid = not any(blocker.startswith("invalid schema") for blocker in blockers)
    assessment_status = _assessment_status(
        schema_valid=schema_valid,
        blockers=blockers,
        claim_verdict=_string(claim.get("verdict")),
    )
    return {
        "path": relative,
        "schemaValid": schema_valid,
        "assessmentStatus": assessment_status,
        "claim": {
            "id": _string(claim.get("id")),
            "summary": _string(claim.get("summary")),
            "scope": _string(claim.get("scope")),
            "verdict": _string(claim.get("verdict")),
        },
        "promotion": {
            "status": _string(promotion.get("status")),
            "humanApproved": promotion.get("humanApproved")
            if isinstance(promotion.get("humanApproved"), bool)
            else False,
        },
        "primaryMetric": _metric_summary(primary),
        "blockers": blockers,
        "warnings": warnings,
    }


def _evaluate_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    missing = [field for field in REQUIRED_TOP_LEVEL if field not in payload]
    if missing:
        blockers.append(f"invalid schema: missing fields: {', '.join(missing)}")
        return blockers, warnings
    if payload.get("schemaVersion") != EVIDENCE_SCHEMA_VERSION:
        blockers.append("invalid schema: schemaVersion is not effectiveness evidence v1")

    claim = _object(payload, "claim", blockers)
    candidate = _object(payload, "candidate", blockers)
    baseline = _object(payload, "baseline", blockers)
    evaluation = _object(payload, "evaluation", blockers)
    metrics = _object(payload, "metrics", blockers)
    safety = _object(payload, "safety", blockers)
    evidence = _object(payload, "evidence", blockers)
    promotion = _object(payload, "promotion", blockers)
    target = _object(payload, "target", blockers)

    claim_verdict = _string(claim.get("verdict"))
    if claim_verdict not in VALID_CLAIM_VERDICTS:
        blockers.append("invalid schema: claim verdict is not recognized")
    target_root = target.get("root")
    if isinstance(target_root, str) and is_absolute_path_text(target_root):
        blockers.append("target root must be omitted, null, or redacted")

    _validate_snapshot(candidate, "candidate", blockers)
    _validate_snapshot(baseline, "baseline", blockers)
    if claim_verdict == "candidate_better" and not candidate.get("changedSurfaces"):
        blockers.append("candidate_better claims must name changed harness surfaces")

    _validate_evaluation(evaluation, blockers, warnings, claim_verdict)
    _validate_metrics(metrics, blockers, warnings, claim_verdict)
    _validate_safety(safety, blockers, claim_verdict)
    _validate_evidence(evidence, blockers, warnings)
    _validate_promotion(promotion, blockers, warnings, claim_verdict)
    return _dedupe(blockers), _dedupe(warnings)


def _validate_snapshot(
    value: dict[str, Any], label: str, blockers: list[str]
) -> None:
    snapshot = value.get("snapshot")
    if not isinstance(snapshot, dict):
        blockers.append(f"{label} snapshot is required")
        return
    artifact_refs = snapshot.get("artifactRefs")
    if not isinstance(artifact_refs, list) or not artifact_refs:
        blockers.append(f"{label} snapshot artifactRefs are required")
        return
    for ref in artifact_refs:
        if not isinstance(ref, str) or not _is_repo_relative(ref):
            blockers.append(f"{label} snapshot artifactRefs must be repo-relative")


def _validate_evaluation(
    evaluation: dict[str, Any],
    blockers: list[str],
    warnings: list[str],
    claim_verdict: str,
) -> None:
    replay_type = _string(evaluation.get("replayType"))
    if replay_type not in VALID_REPLAY_TYPES:
        blockers.append("evaluation replayType is not recognized")
    if replay_type == "frozen_replay" and claim_verdict == "candidate_better":
        blockers.append("frozen replay cannot support candidate_better quality claims")
    feedback = evaluation.get("feedbackChannels")
    if not isinstance(feedback, list) or not feedback:
        blockers.append("evaluation feedbackChannels are required")
    task_set = evaluation.get("taskSet")
    if not isinstance(task_set, dict):
        blockers.append("evaluation taskSet is required")
    else:
        if task_set.get("heldOut") is not True:
            blockers.append("effectiveness claims require held-out tasks")
        if _positive_int(task_set.get("sampleCount")) is None:
            blockers.append("taskSet sampleCount must be a positive integer")
        controls = task_set.get("contaminationControls")
        if not isinstance(controls, list) or not controls:
            blockers.append("contamination controls are required")
    if not _string(evaluation.get("reproductionCommand")):
        blockers.append("reproductionCommand is required")
    for key in ("runtimeBudget", "workspaceContract", "adapterContract"):
        if not isinstance(evaluation.get(key), dict):
            blockers.append(f"evaluation {key} is required")
    if replay_type == "counterfactual_replay":
        warnings.append("counterfactual replay requires careful human review")


def _validate_metrics(
    metrics: dict[str, Any],
    blockers: list[str],
    warnings: list[str],
    claim_verdict: str,
) -> None:
    primary = metrics.get("primary")
    worst_case = metrics.get("worstCase")
    floor = metrics.get("doNoHarmFloor")
    if not isinstance(primary, dict):
        blockers.append("primary metric is required")
        return
    if not isinstance(worst_case, dict):
        blockers.append("worst-case metric is required")
    if not isinstance(floor, dict):
        blockers.append("do-no-harm floor is required")
    if primary.get("candidateSensitive") is not True:
        blockers.append("primary metric must be candidate-sensitive")
    if isinstance(worst_case, dict) and worst_case.get("candidateSensitive") is not True:
        blockers.append("worst-case metric must be candidate-sensitive")
    if isinstance(floor, dict) and floor.get("met") is not True:
        blockers.append("do-no-harm floor must be met")
    delta = _metric_delta(primary)
    if claim_verdict == "candidate_better" and delta is not None and delta <= 0:
        blockers.append("candidate_better claim requires a positive primary delta")
    if delta is None:
        warnings.append("primary metric delta could not be computed")


def _validate_safety(
    safety: dict[str, Any], blockers: list[str], claim_verdict: str
) -> None:
    if claim_verdict != "candidate_better":
        return
    if safety.get("trajectoryReviewed") is not True:
        blockers.append("trajectory safety review is required")
    if safety.get("permissionBoundaryReviewed") is not True:
        blockers.append("permission-boundary review is required")
    violations = safety.get("violations")
    if isinstance(violations, list) and violations:
        blockers.append("safety violations must be resolved before promotion")


def _validate_evidence(
    evidence: dict[str, Any], blockers: list[str], warnings: list[str]
) -> None:
    artifacts = evidence.get("resultArtifacts")
    if not isinstance(artifacts, list) or not artifacts:
        blockers.append("result artifacts are required")
    else:
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                blockers.append("result artifacts must be objects")
                continue
            path = artifact.get("path")
            if not isinstance(path, str) or not _is_repo_relative(path):
                blockers.append("result artifact paths must be repo-relative")
            if artifact.get("redacted") is not True:
                blockers.append("result artifacts must be redacted")
    reviewed_by = evidence.get("reviewedBy")
    if not isinstance(reviewed_by, list) or not reviewed_by:
        warnings.append("human reviewer metadata is missing")
    if not _string(evidence.get("reviewedAt")):
        warnings.append("review timestamp is missing")


def _validate_promotion(
    promotion: dict[str, Any],
    blockers: list[str],
    warnings: list[str],
    claim_verdict: str,
) -> None:
    status = _string(promotion.get("status"))
    if status not in VALID_PROMOTION_STATUSES:
        blockers.append("promotion status is not recognized")
    human_approved = promotion.get("humanApproved")
    if claim_verdict == "candidate_better":
        if status != "promoted":
            blockers.append("candidate_better claims require promoted status")
        if human_approved is not True:
            blockers.append("candidate_better claims require human approval")
    elif status == "promoted":
        warnings.append("promoted evidence does not claim candidate_better")
    if not _string(promotion.get("rollback")):
        blockers.append("rollback instructions are required")


def _metric_summary(metric: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(metric, dict) or not metric:
        return None
    return {
        "name": _string(metric.get("name")),
        "direction": _string(metric.get("direction")),
        "baselineValue": metric.get("baselineValue"),
        "candidateValue": metric.get("candidateValue"),
        "delta": _metric_delta(metric),
        "unit": _string(metric.get("unit")),
        "candidateSensitive": metric.get("candidateSensitive") is True,
    }


def _metric_delta(metric: dict[str, Any]) -> float | None:
    baseline = metric.get("baselineValue")
    candidate = metric.get("candidateValue")
    direction = metric.get("direction")
    if (
        not isinstance(baseline, (int, float))
        or isinstance(baseline, bool)
        or not isinstance(candidate, (int, float))
        or isinstance(candidate, bool)
    ):
        return None
    if direction not in VALID_METRIC_DIRECTIONS:
        return None
    raw_delta = candidate - baseline
    delta = raw_delta if direction == "higher_is_better" else -raw_delta
    return round(float(delta), 10)


def _assessment_status(
    *,
    schema_valid: bool,
    blockers: list[str],
    claim_verdict: str,
) -> str:
    if not schema_valid or blockers:
        return "blocked"
    if claim_verdict == "candidate_better":
        return "reviewable"
    if claim_verdict == "candidate_not_better":
        return "not_better"
    return "inconclusive"


def _detected_evidence_paths(files: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(file for file in files if _is_effectiveness_evidence_file(file))


def _explicit_evidence_paths(root: Path, values: tuple[str, ...]) -> tuple[str, ...]:
    paths: list[str] = []
    for value in values:
        value = value.strip()
        if is_absolute_path_text(value):
            raise ValueError("--evidence must be a target-relative path")
        relative = path_from_relative_text(value).as_posix()
        if relative == "." or ".." in Path(relative).parts:
            raise ValueError("--evidence must not escape the target repository")
        path = root / path_from_relative_text(relative)
        if not is_inside_root(path, root):
            raise ValueError("--evidence must stay inside the target repository")
        paths.append(relative)
    return tuple(paths)


def _is_effectiveness_evidence_file(file: str) -> bool:
    path = Path(file)
    return (
        file.startswith(EVIDENCE_PREFIX)
        and path.name.startswith(EVIDENCE_NAME_PREFIX)
        and path.suffix.lower() == ".json"
    )


def _invalid_report(relative: str, blockers: tuple[str, ...]) -> dict[str, Any]:
    return {
        "path": relative,
        "schemaValid": False,
        "assessmentStatus": "blocked",
        "claim": {
            "id": "",
            "summary": "",
            "scope": "",
            "verdict": "",
        },
        "promotion": {
            "status": "",
            "humanApproved": False,
        },
        "primaryMetric": None,
        "blockers": list(blockers),
        "warnings": [],
    }


def _summary(reports: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "reports": len(reports),
        "validReports": sum(1 for report in reports if report["schemaValid"]),
        "reviewableReports": sum(
            1 for report in reports if report["assessmentStatus"] == "reviewable"
        ),
        "blockedReports": sum(
            1 for report in reports if report["assessmentStatus"] == "blocked"
        ),
        "inconclusiveReports": sum(
            1 for report in reports if report["assessmentStatus"] == "inconclusive"
        ),
        "notBetterReports": sum(
            1 for report in reports if report["assessmentStatus"] == "not_better"
        ),
    }


def _verdict(reports: list[dict[str, Any]]) -> str:
    if not reports:
        return "blocked"
    statuses = {report["assessmentStatus"] for report in reports}
    if "reviewable" in statuses:
        return "reviewable"
    if statuses == {"blocked"}:
        return "blocked"
    if "inconclusive" in statuses:
        return "inconclusive"
    if "not_better" in statuses:
        return "not_better"
    return "blocked"


def _blocked_reasons(reports: list[dict[str, Any]]) -> list[str]:
    if not reports:
        return ["No effectiveness evidence reports found."]
    reasons: list[str] = []
    for report in reports:
        for blocker in report["blockers"]:
            reasons.append(f"{report['path']}: {blocker}")
    return _dedupe(reasons)


def _warnings(reports: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for report in reports:
        for warning in report["warnings"]:
            warnings.append(f"{report['path']}: {warning}")
    return _dedupe(warnings)


def _next_actions(
    reports: list[dict[str, Any]],
    blocked_reasons: list[str],
    warnings: list[str],
) -> list[str]:
    if not reports:
        return [
            "Record representative effectiveness evidence before making harness performance claims."
        ]
    if blocked_reasons:
        return ["Fix blocked effectiveness evidence before relying on the claim."]
    if warnings:
        return ["Review effectiveness warnings before promotion."]
    return ["Use human review before promoting candidate harness changes."]


def _object(
    payload: dict[str, Any], key: str, blockers: list[str]
) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        blockers.append(f"invalid schema: {key} must be an object")
        return {}
    return value


def _positive_int(value: object) -> int | None:
    if isinstance(value, int) and value > 0:
        return value
    return None


def _is_repo_relative(path_text: str) -> bool:
    if is_absolute_path_text(path_text):
        return False
    path = Path(path_text.replace("\\", "/"))
    return path.as_posix() != "." and ".." not in path.parts


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _append_section(lines: list[str], title: str, values: list[str]) -> None:
    if not values:
        return
    lines.append(f"{title}:")
    for value in values:
        lines.append(f"  - {value}")
    lines.append("")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
