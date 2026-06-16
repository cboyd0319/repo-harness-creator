from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.paths import is_absolute_path_text, is_inside_root, path_from_relative_text
from .first_agent import EVIDENCE_PATH

SCHEMA_VERSION = "harnessforge.highRiskAcceptance.v1"
ACCEPTED_REVIEW_STATUSES = {"accepted_advisory", "accepted", "reviewed"}
ACCEPTED_SURFACE_DECISIONS = {"accepted", "accepted_advisory", "reviewed"}
NEUTRAL_REVIEW_STATUSES = {"pending", "absent"}


@dataclass(frozen=True)
class HighRiskAcceptedSurface:
    path: str
    category: str
    decision: str


@dataclass(frozen=True)
class HighRiskAcceptanceReport:
    evidence_path: str | None
    status: str
    accepted_surfaces: tuple[HighRiskAcceptedSurface, ...]
    warnings: tuple[str, ...]

    def accepts_path(self, path: str) -> bool:
        return path in {surface.path for surface in self.accepted_surfaces}


def analyze_high_risk_acceptance(
    root: Path,
    files: tuple[str, ...],
) -> HighRiskAcceptanceReport:
    if EVIDENCE_PATH not in set(files):
        return HighRiskAcceptanceReport(
            evidence_path=None,
            status="absent",
            accepted_surfaces=(),
            warnings=(),
        )
    path = root / path_from_relative_text(EVIDENCE_PATH)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return HighRiskAcceptanceReport(
            evidence_path=EVIDENCE_PATH,
            status="invalid",
            accepted_surfaces=(),
            warnings=("high-risk surface review evidence is invalid JSON.",),
        )
    return high_risk_acceptance_from_payload(root, payload, evidence_path=EVIDENCE_PATH)


def high_risk_acceptance_from_payload(
    root: Path,
    payload: Any,
    *,
    evidence_path: str | None,
) -> HighRiskAcceptanceReport:
    if not isinstance(payload, dict):
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status="invalid",
            accepted_surfaces=(),
            warnings=("high-risk surface review evidence must be an object.",),
        )
    review = payload.get("highRiskSurfaceReview")
    if review is None:
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status="absent",
            accepted_surfaces=(),
            warnings=(),
        )
    if not isinstance(review, dict):
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status="invalid",
            accepted_surfaces=(),
            warnings=("highRiskSurfaceReview must be an object.",),
        )
    status = review.get("status")
    warnings: list[str] = []
    if status in NEUTRAL_REVIEW_STATUSES:
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status=str(status),
            accepted_surfaces=(),
            warnings=(),
        )
    if status not in ACCEPTED_REVIEW_STATUSES:
        warnings.append("highRiskSurfaceReview.status is not accepted.")
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status=str(status) if isinstance(status, str) else "invalid",
            accepted_surfaces=(),
            warnings=tuple(warnings),
        )
    surfaces = review.get("surfaces")
    if not isinstance(surfaces, list):
        return HighRiskAcceptanceReport(
            evidence_path=evidence_path,
            status=str(status),
            accepted_surfaces=(),
            warnings=("highRiskSurfaceReview.surfaces must be a list.",),
        )
    accepted: list[HighRiskAcceptedSurface] = []
    for index, item in enumerate(surfaces):
        if not isinstance(item, dict):
            warnings.append(f"highRiskSurfaceReview.surfaces[{index}] must be an object.")
            continue
        path_text = item.get("path")
        category = item.get("category")
        decision = item.get("decision")
        normalized_path = _target_relative_path(root, path_text)
        if normalized_path is None:
            warnings.append(
                f"highRiskSurfaceReview.surfaces[{index}].path must be target-relative."
            )
            continue
        if not isinstance(category, str) or not category.strip():
            warnings.append(
                f"highRiskSurfaceReview.surfaces[{index}].category is required."
            )
            continue
        if decision not in ACCEPTED_SURFACE_DECISIONS:
            warnings.append(
                f"highRiskSurfaceReview.surfaces[{index}].decision is not accepted."
            )
            continue
        accepted.append(
            HighRiskAcceptedSurface(
                path=normalized_path,
                category=category.strip(),
                decision=str(decision),
            )
        )
    return HighRiskAcceptanceReport(
        evidence_path=evidence_path,
        status=str(status),
        accepted_surfaces=tuple(_dedupe_surfaces(accepted)),
        warnings=tuple(_dedupe(warnings)),
    )


def high_risk_acceptance_to_dict(report: HighRiskAcceptanceReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "evidencePath": report.evidence_path,
        "status": report.status,
        "summary": {
            "acceptedCount": len(report.accepted_surfaces),
            "warningCount": len(report.warnings),
        },
        "acceptedSurfaces": [
            {
                "path": surface.path,
                "category": surface.category,
                "decision": surface.decision,
            }
            for surface in report.accepted_surfaces
        ],
        "warnings": list(report.warnings),
    }


def _target_relative_path(root: Path, value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    if is_absolute_path_text(value):
        return None
    try:
        relative_path = path_from_relative_text(value)
    except ValueError:
        return None
    target = root / relative_path
    if not is_inside_root(target, root):
        return None
    return relative_path.as_posix()


def _dedupe_surfaces(
    surfaces: list[HighRiskAcceptedSurface],
) -> list[HighRiskAcceptedSurface]:
    seen: set[str] = set()
    result: list[HighRiskAcceptedSurface] = []
    for surface in surfaces:
        if surface.path in seen:
            continue
        seen.add(surface.path)
        result.append(surface)
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
