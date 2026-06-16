from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.paths import path_from_relative_text

SCHEMA_VERSION = "harnessforge.featureState.v1"
FEATURE_LIST_PATH = "feature_list.json"
EVIDENCE_STATUSES = {"passing", "validated", "shipped"}


@dataclass(frozen=True)
class FeatureStateReport:
    status: str
    summary: dict[str, Any]
    active_features: tuple[dict[str, Any], ...]
    findings: tuple[str, ...]
    warnings: tuple[str, ...]
    next_actions: tuple[str, ...]
    scope_drift: dict[str, Any]


def build_feature_state_report(
    root: Path,
    *,
    diff_plan: Any | None = None,
) -> dict[str, Any]:
    report = analyze_feature_state(root, diff_plan=diff_plan)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": report.status,
        "summary": report.summary,
        "activeFeatures": list(report.active_features),
        "findings": list(report.findings),
        "warnings": list(report.warnings),
        "nextActions": list(report.next_actions),
        "scopeDrift": report.scope_drift,
    }


def analyze_feature_state(
    root: Path,
    *,
    diff_plan: Any | None = None,
) -> FeatureStateReport:
    path = root / path_from_relative_text(FEATURE_LIST_PATH)
    if not path.exists():
        return FeatureStateReport(
            status="absent",
            summary={
                "featureCount": 0,
                "activeCount": 0,
                "evidenceGated": False,
                "singleActiveRequired": False,
                "statusCounts": {},
            },
            active_features=(),
            findings=("feature_list.json is missing.",),
            warnings=("Feature-state gate is unavailable without feature_list.json.",),
            next_actions=("Add feature_list.json or document the project-owned planning system.",),
            scope_drift=_scope_drift_summary(diff_plan, active_features=()),
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return FeatureStateReport(
            status="invalid",
            summary={
                "featureCount": 0,
                "activeCount": 0,
                "evidenceGated": False,
                "singleActiveRequired": False,
                "statusCounts": {},
            },
            active_features=(),
            findings=("feature_list.json is not valid JSON.",),
            warnings=("Feature-state gate is blocked by invalid feature_list.json.",),
            next_actions=("Repair feature_list.json before relying on feature-state signals.",),
            scope_drift=_scope_drift_summary(diff_plan, active_features=()),
        )
    features = payload.get("features", [])
    if not isinstance(features, list):
        features = []
    rules = payload.get("rules", {})
    if not isinstance(rules, dict):
        rules = {}
    status_counts = Counter(
        str(feature.get("status", "unknown"))
        for feature in features
        if isinstance(feature, dict)
    )
    active = tuple(
        _feature_summary(feature)
        for feature in features
        if isinstance(feature, dict) and str(feature.get("status")) == "active"
    )
    findings: list[str] = []
    warnings: list[str] = []
    next_actions: list[str] = []
    single_active_required = bool(rules.get("single_active_feature"))
    evidence_gated = bool(rules.get("passing_requires_evidence"))
    if single_active_required and len(active) != 1:
        findings.append(
            f"single_active_feature expects exactly one active feature; found {len(active)}."
        )
    for feature in features:
        if not isinstance(feature, dict):
            findings.append("feature record is not an object.")
            continue
        feature_id = str(feature.get("id", "unknown"))
        status = str(feature.get("status", "unknown"))
        verification = feature.get("verification", [])
        evidence = feature.get("evidence", [])
        if not feature.get("user_visible_behavior"):
            findings.append(f"{feature_id} is missing user_visible_behavior.")
        if not isinstance(verification, list) or not verification:
            findings.append(f"{feature_id} is missing verification criteria.")
        if status in EVIDENCE_STATUSES and (not isinstance(evidence, list) or not evidence):
            findings.append(f"{feature_id} is {status} without evidence.")
    scope_drift = _scope_drift_summary(diff_plan, active_features=active)
    warnings.extend(scope_drift.get("warnings", []))
    if findings:
        warnings.append("Feature-state evidence needs review before release gating.")
        next_actions.append(
            "Align feature status, verification criteria, and evidence before marking work complete."
        )
    if scope_drift.get("status") == "review":
        next_actions.append(
            "Review scope drift before updating feature state or release evidence."
        )
    status = "needs_review" if findings or warnings else "aligned"
    return FeatureStateReport(
        status=status,
        summary={
            "featureCount": len(features),
            "activeCount": len(active),
            "evidenceGated": evidence_gated,
            "singleActiveRequired": single_active_required,
            "statusCounts": dict(sorted(status_counts.items())),
        },
        active_features=active,
        findings=tuple(_dedupe(findings)),
        warnings=tuple(_dedupe(warnings)),
        next_actions=tuple(_dedupe(next_actions)),
        scope_drift=scope_drift,
    )


def _feature_summary(feature: dict[str, Any]) -> dict[str, Any]:
    verification = feature.get("verification", [])
    evidence = feature.get("evidence", [])
    return {
        "id": str(feature.get("id", "")),
        "title": str(feature.get("title", "")),
        "area": str(feature.get("area", "")),
        "status": str(feature.get("status", "")),
        "verificationCount": len(verification) if isinstance(verification, list) else 0,
        "evidenceCount": len(evidence) if isinstance(evidence, list) else 0,
    }


def _scope_drift_summary(
    diff_plan: Any | None,
    *,
    active_features: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    if diff_plan is None:
        return {
            "status": "not_requested",
            "base": None,
            "changedFileCount": 0,
            "activeFeatureIds": [item["id"] for item in active_features],
            "touchedAreas": [],
            "unexpectedAreas": [],
            "warnings": [],
        }
    blocked = list(getattr(diff_plan, "blocked_reasons", ()))
    if blocked:
        return {
            "status": "unavailable",
            "base": getattr(diff_plan, "base", None),
            "changedFileCount": 0,
            "activeFeatureIds": [item["id"] for item in active_features],
            "touchedAreas": [],
            "unexpectedAreas": [],
            "warnings": blocked,
        }
    changed_files = tuple(getattr(diff_plan, "changed_files", ()))
    touched = sorted({area for file in changed_files for area in _areas_for_file(file)})
    active_areas = {str(item.get("area", "")) for item in active_features if item.get("area")}
    allowed = _allowed_areas(active_areas)
    unexpected = [area for area in touched if allowed and area not in allowed]
    warnings: list[str] = []
    if not active_features and changed_files:
        warnings.append("Changed files exist but no active feature is recorded.")
    if unexpected:
        warnings.append(
            "Changed files touch areas outside the active feature scope: "
            + ", ".join(unexpected)
            + "."
        )
    status = "review" if warnings else "aligned" if changed_files else "no_changes"
    return {
        "status": status,
        "base": getattr(diff_plan, "base", None),
        "changedFileCount": len(changed_files),
        "changedFiles": list(changed_files),
        "activeFeatureIds": [item["id"] for item in active_features],
        "activeAreas": sorted(active_areas),
        "touchedAreas": touched,
        "unexpectedAreas": unexpected,
        "warnings": warnings,
    }


def _areas_for_file(path: str) -> set[str]:
    normalized = path.replace("\\", "/").lower()
    areas: set[str] = set()
    if normalized.startswith("src/harnessforge/"):
        areas.add("cli")
    if (
        normalized.startswith("src/harnessforge/templates/")
        or normalized.startswith("src/harnessforge/generation/")
        or normalized.startswith(".agents/skills/harness/")
    ):
        areas.add("generated")
    if normalized.startswith("tests/"):
        areas.add("tests")
    if normalized.startswith("docs/") or normalized in {
        "readme.md",
        "agents.md",
        "feature_list.json",
        "current-state.md",
    }:
        areas.add("docs")
    if normalized.startswith(".github/") or normalized == "action.yml":
        areas.add("action")
    if "release" in normalized or normalized == "pyproject.toml":
        areas.add("release")
    if normalized.startswith("scripts/"):
        areas.add("scripts")
    return areas or {"other"}


def _allowed_areas(active_areas: set[str]) -> set[str]:
    if not active_areas:
        return set()
    allowed = set(active_areas)
    allowed.update({"tests", "docs"})
    if "cli" in active_areas:
        allowed.update({"generated", "action", "scripts", "release"})
    if "generated" in active_areas:
        allowed.update({"cli", "action"})
    if "docs" in active_areas:
        allowed.update({"generated"})
    return allowed


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
