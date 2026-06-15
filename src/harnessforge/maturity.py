from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "harnessforge.maturity.v1"
LEVEL_ORDER = ("generated", "reviewed", "verified", "release-ready", "measured")
DEFAULT_MIN_SCORE = 85


def build_maturity_report(
    report: dict[str, Any],
    *,
    min_score: int = DEFAULT_MIN_SCORE,
) -> dict[str, Any]:
    levels = [
        _level("generated", _generated_requirements(report, min_score=min_score)),
        _level("reviewed", _reviewed_requirements(report)),
        _level("verified", _verified_requirements(report)),
        _level(
            "release-ready",
            _release_ready_requirements(report, min_score=min_score),
        ),
        _level("measured", _measured_requirements(report)),
    ]
    cumulative = True
    current = "none"
    next_level = None
    blocked: list[dict[str, Any]] = []
    for item in levels:
        if cumulative and item["status"] == "passed":
            current = item["id"]
            continue
        cumulative = False
        item["status"] = "blocked"
        if next_level is None:
            next_level = item["id"]
            blocked = [
                requirement
                for requirement in item["requirements"]
                if requirement["status"] != "passed"
            ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "currentLevel": current,
        "nextLevel": next_level,
        "levels": levels,
        "blockedRequirements": blocked,
        "summary": {
            "levelOrder": list(LEVEL_ORDER),
            "minAuditScore": min_score,
            "structuralAuditScore": report["audit"]["overall"],
            "evidenceBased": True,
        },
    }


def _generated_requirements(
    report: dict[str, Any],
    *,
    min_score: int,
) -> list[dict[str, Any]]:
    score = int(report["audit"]["overall"])
    instruction_status = str(report["instructionQuality"]["summary"]["status"])
    return [
        _requirement(
            "audit-baseline",
            score >= min_score,
            f"structural audit score {score}/100 meets {min_score}",
            value=score,
        ),
        _requirement(
            "instruction-surface",
            instruction_status not in {"absent", "weak"},
            f"instruction quality is {instruction_status}",
            value=instruction_status,
        ),
    ]


def _reviewed_requirements(report: dict[str, Any]) -> list[dict[str, Any]]:
    lifecycle = report["firstAgentTask"]["lifecycle"]
    lifecycle_status = str(lifecycle["status"])
    review_count = int(report["readiness"]["reviewRequiredCount"])
    return [
        _requirement(
            "first-agent-review",
            lifecycle_status in {"completed", "retired"},
            f"first-agent lifecycle is {lifecycle_status}",
            value=lifecycle_status,
        ),
        _requirement(
            "readiness-review-surfaces",
            review_count == 0,
            f"{review_count} readiness surfaces require review",
            value=review_count,
        ),
    ]


def _verified_requirements(report: dict[str, Any]) -> list[dict[str, Any]]:
    latest = report["verifyEvidence"]["latest"]
    if not latest:
        return [
            _requirement(
                "verify-evidence",
                False,
                "no stored verify evidence report found",
                value=None,
            )
        ]
    summary = latest.get("summary", {})
    bad_counts = [
        key
        for key in ("blocked", "failed", "timedOut", "errors")
        if isinstance(summary, dict) and _positive_count(summary.get(key)) > 0
    ]
    issues = latest.get("issues", [])
    stale = isinstance(issues, list) and "stale" in issues
    return [
        _requirement(
            "verify-evidence-mode",
            latest.get("mode") == "run",
            f"latest verify evidence mode is {latest.get('mode') or 'missing'}",
            value=latest.get("mode"),
        ),
        _requirement(
            "verify-evidence-verdict",
            latest.get("verdict") == "passed",
            f"latest verify evidence verdict is {latest.get('verdict') or 'missing'}",
            value=latest.get("verdict"),
        ),
        _requirement(
            "verify-evidence-freshness",
            not stale,
            "latest verify evidence is not stale",
            value=not stale,
        ),
        _requirement(
            "verify-evidence-clean-summary",
            not bad_counts,
            (
                "latest verify evidence has no blocked, failed, timed-out, "
                "or errored checks"
            ),
            value=bad_counts,
        ),
    ]


def _release_ready_requirements(
    report: dict[str, Any],
    *,
    min_score: int,
) -> list[dict[str, Any]]:
    score = int(report["audit"]["overall"])
    readiness = report["readiness"]
    drift_actionable = int(report["drift"]["summary"]["actionable"])
    quality_status = str(report["instructionQuality"]["summary"]["status"])
    fanout = str(report["docsFanout"]["contract"]["verdict"])
    controls = report.get("releaseControls", {})
    controls_present = (
        bool(controls.get("present")) if isinstance(controls, dict) else False
    )
    return [
        _requirement(
            "audit-release-minimum",
            score >= min_score,
            f"structural audit score {score}/100 meets {min_score}",
            value=score,
        ),
        _requirement(
            "readiness-clean",
            readiness["verdict"] == "ready",
            f"readiness verdict is {readiness['verdict']}",
            value=readiness["verdict"],
        ),
        _requirement(
            "generated-drift-clean",
            drift_actionable == 0,
            f"{drift_actionable} actionable generated drift items",
            value=drift_actionable,
        ),
        _requirement(
            "instruction-quality-release",
            quality_status in {"strong", "adequate"},
            f"instruction quality is {quality_status}",
            value=quality_status,
        ),
        _requirement(
            "docs-fanout-clean",
            fanout in {"passed", "not_required"},
            f"docs fan-out contract is {fanout}",
            value=fanout,
        ),
        _requirement(
            "release-controls-present",
            controls_present,
            "release controls document is present",
            value=controls_present,
        ),
    ]


def _measured_requirements(report: dict[str, Any]) -> list[dict[str, Any]]:
    verdict = str(report["effectiveness"]["verdict"])
    return [
        _requirement(
            "effectiveness-evidence-reviewable",
            verdict == "reviewable",
            f"stored effectiveness evidence is {verdict}",
            value=verdict,
        )
    ]


def _level(level_id: str, requirements: list[dict[str, Any]]) -> dict[str, Any]:
    status = (
        "passed"
        if all(item["status"] == "passed" for item in requirements)
        else "blocked"
    )
    return {
        "id": level_id,
        "status": status,
        "requirements": requirements,
    }


def _requirement(
    requirement_id: str,
    passed: bool,
    message: str,
    *,
    value: object,
) -> dict[str, Any]:
    return {
        "id": requirement_id,
        "status": "passed" if passed else "blocked",
        "value": value,
        "message": message,
    }


def _positive_count(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(value, 0)
    return 0
