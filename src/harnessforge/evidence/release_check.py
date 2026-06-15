from __future__ import annotations

from pathlib import Path
from typing import Any

from .report import build_report
from ..reports import relative_to_target, report_path

SCHEMA_VERSION = "harnessforge.releaseCheck.v1"
DEFAULT_MIN_SCORE = 85


def build_release_check(
    target: Path,
    *,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
    max_files: int = 4000,
    min_score: int = DEFAULT_MIN_SCORE,
    require_docs_fanout_budget: bool = False,
    require_sbom: bool = False,
    since: str | None = None,
) -> dict[str, Any]:
    if min_score < 0 or min_score > 100:
        raise ValueError("min-score must be between 0 and 100")
    report = build_report(
        target,
        explicit_package_manager=explicit_package_manager,
        explicit_commands=explicit_commands,
        max_files=max_files,
        require_verify_evidence=True,
        require_docs_fanout_budget=require_docs_fanout_budget,
        since=since,
    )
    gates = _release_gates(
        report,
        min_score=min_score,
        require_sbom=require_sbom,
        release_controls_present=bool(report["releaseControls"]["present"]),
    )
    verdict = _verdict(gates)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "target": report["target"],
        "mode": "read_only",
        "generatedAt": report["generatedAt"],
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
            "publishesPerformed": False,
        },
        "policy": {
            "minAuditScore": min_score,
            "verifyEvidenceRequired": True,
            "docsFanoutBudgetRequired": require_docs_fanout_budget,
            "sbomRequired": require_sbom,
        },
        "verdict": verdict,
        "summary": _summary(report),
        "gates": gates,
        "nextActions": _next_actions(report, gates),
        "sourceReport": _source_report_summary(report),
    }


def format_release_check(payload: dict[str, Any]) -> str:
    lines = [
        "# HarnessForge Release Check",
        "",
        f"- Target: `{payload['target']['name']}`",
        f"- Verdict: `{payload['verdict']}`",
        f"- Mode: `{payload['mode']}`",
        "- Commands executed: `false`",
        "- Writes performed: `false`",
        "- Publishes performed: `false`",
        "",
        "## Summary",
        "",
    ]
    summary = payload["summary"]
    lines.extend(
        [
            f"- Audit score: {summary['auditScore']}/100",
            f"- Readiness: `{summary['readinessVerdict']}`",
            f"- Verify evidence: `{summary['verifyEvidenceVerdict']}`",
            f"- Generated drift: {summary['generatedDriftActionable']} actionable",
            f"- Instruction quality: `{summary['instructionQualityStatus']}`",
            f"- First-agent lifecycle: `{summary['firstAgentLifecycleStatus']}`",
            f"- Maturity level: `{summary['maturityLevel']}`",
            f"- Docs fan-out: `{summary['docsFanoutVerdict']}`",
            f"- SBOM files: {summary['sbomCount']}",
            "",
            "## Gates",
            "",
        ]
    )
    for gate in payload["gates"]:
        lines.append(
            f"- `{gate['status']}` {gate['id']}: {gate['message']}"
        )
    lines.extend(["", "## Next Actions", ""])
    for action in payload["nextActions"]:
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def write_markdown_release_check(
    path_text: str,
    target: Path,
    payload: dict[str, Any],
) -> str:
    path = report_path(path_text, target)
    if path is None:
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_release_check(payload), encoding="utf-8")
    return relative_to_target(path, target)


def release_check_exit_code(payload: dict[str, Any]) -> int:
    verdict = payload.get("verdict")
    if verdict == "passed":
        return 0
    if verdict == "warning":
        return 1
    return 2


def _release_gates(
    report: dict[str, Any],
    *,
    min_score: int,
    require_sbom: bool,
    release_controls_present: bool,
) -> list[dict[str, Any]]:
    gates = [
        _audit_gate(report, min_score),
        _readiness_gate(report),
        _verify_evidence_gate(report),
        _generated_drift_gate(report),
        _instruction_quality_gate(report),
        _first_agent_gate(report),
        _docs_fanout_gate(report),
        _release_controls_gate(release_controls_present),
        _effectiveness_gate(report),
        _sbom_gate(report, require_sbom=require_sbom),
    ]
    return gates


def _audit_gate(report: dict[str, Any], min_score: int) -> dict[str, Any]:
    score = int(report["audit"]["overall"])
    if score >= min_score:
        return _gate(
            "audit-score",
            "passed",
            f"audit score {score}/100 meets the {min_score} minimum",
            value=score,
        )
    return _gate(
        "audit-score",
        "blocked",
        f"audit score {score}/100 is below the {min_score} minimum",
        value=score,
    )


def _readiness_gate(report: dict[str, Any]) -> dict[str, Any]:
    readiness = report["readiness"]
    verdict = str(readiness["verdict"])
    if verdict == "ready":
        status = "passed"
    elif verdict == "warning":
        status = "warning"
    else:
        status = "blocked"
    return _gate(
        "readiness",
        status,
        (
            f"readiness is {verdict} with "
            f"{readiness['blockedCount']} blockers, "
            f"{readiness['warningCount']} warnings, and "
            f"{readiness['reviewRequiredCount']} review-required surfaces"
        ),
        value=verdict,
    )


def _verify_evidence_gate(report: dict[str, Any]) -> dict[str, Any]:
    evidence = report["verifyEvidence"]
    reports = evidence.get("reports", [])
    latest = evidence.get("latest")
    blockers: list[str] = []
    if not reports:
        blockers.append("no stored verify evidence report found")
    for item in reports:
        if not item.get("schemaValid"):
            blockers.append(f"{item.get('path', 'unknown')} is invalid")
    if not latest:
        blockers.append("no valid latest verify evidence report found")
    else:
        if latest.get("mode") != "run":
            blockers.append(
                f"{latest.get('path', 'latest report')} is not run-mode evidence"
            )
        if latest.get("verdict") != "passed":
            blockers.append(
                f"{latest.get('path', 'latest report')} verdict is "
                f"{latest.get('verdict') or 'missing'}"
            )
        if "stale" in latest.get("issues", []):
            blockers.append(
                f"{latest.get('path', 'latest report')} is stale "
                f"({latest.get('ageDays', 'unknown')} days old)"
            )
        summary = latest.get("summary", {})
        for key in ("blocked", "failed", "timedOut", "errors"):
            value = summary.get(key, 0) if isinstance(summary, dict) else 0
            if isinstance(value, int) and value > 0:
                blockers.append(
                    f"{latest.get('path', 'latest report')} includes {key} checks"
                )
    if blockers:
        return _gate(
            "verify-evidence",
            "blocked",
            "; ".join(_dedupe(blockers)),
            value=latest.get("verdict") if latest else None,
        )
    return _gate(
        "verify-evidence",
        "passed",
        f"latest run-mode verify evidence passed at {latest['path']}",
        value=latest.get("verdict"),
    )


def _generated_drift_gate(report: dict[str, Any]) -> dict[str, Any]:
    actionable = int(report["drift"]["summary"]["actionable"])
    if actionable:
        return _gate(
            "generated-drift",
            "warning",
            f"{actionable} generated-file drift items need review",
            value=actionable,
        )
    return _gate(
        "generated-drift",
        "passed",
        "no actionable generated-file drift detected",
        value=0,
    )


def _instruction_quality_gate(report: dict[str, Any]) -> dict[str, Any]:
    quality = report["instructionQuality"]["summary"]
    status = str(quality["status"])
    if status in {"absent", "weak"}:
        gate_status = "blocked"
    elif status == "needs_review":
        gate_status = "warning"
    else:
        gate_status = "passed"
    average = quality.get("averageScore")
    return _gate(
        "instruction-quality",
        gate_status,
        f"instruction quality is {status} with average score {average or 'none'}",
        value=status,
    )


def _first_agent_gate(report: dict[str, Any]) -> dict[str, Any]:
    lifecycle = report["firstAgentTask"]["lifecycle"]
    status = str(lifecycle["status"])
    if status in {"completed", "retired"}:
        gate_status = "passed"
    elif status in {"pending"}:
        gate_status = "warning"
    else:
        gate_status = "blocked"
    return _gate(
        "first-agent-lifecycle",
        gate_status,
        f"first-agent harness review lifecycle is {status}",
        value=status,
    )


def _docs_fanout_gate(report: dict[str, Any]) -> dict[str, Any]:
    contract = report["docsFanout"]["contract"]
    verdict = str(contract["verdict"])
    if verdict == "blocked":
        gate_status = "blocked"
    elif verdict == "warning":
        gate_status = "warning"
    else:
        gate_status = "passed"
    return _gate(
        "docs-fanout",
        gate_status,
        f"docs fan-out contract is {verdict}",
        value=verdict,
    )


def _release_controls_gate(present: bool) -> dict[str, Any]:
    if present:
        return _gate(
            "release-controls",
            "passed",
            "release controls document is present",
            value=True,
        )
    return _gate(
        "release-controls",
        "warning",
        "no release controls document was detected",
        value=False,
    )


def _effectiveness_gate(report: dict[str, Any]) -> dict[str, Any]:
    verdict = str(report["effectiveness"]["verdict"])
    if verdict in {"passed", "reviewable"}:
        gate_status = "passed"
    elif verdict == "blocked":
        gate_status = "warning"
    else:
        gate_status = "warning"
    return _gate(
        "effectiveness-evidence",
        gate_status,
        f"stored effectiveness evidence is {verdict}",
        value=verdict,
    )


def _sbom_gate(report: dict[str, Any], *, require_sbom: bool) -> dict[str, Any]:
    count = int(report["index"]["summary"]["sbomCount"])
    if count:
        return _gate("sbom", "passed", f"{count} SBOM file(s) detected", value=count)
    if require_sbom:
        return _gate(
            "sbom",
            "blocked",
            "SBOM evidence is required but no SPDX or CycloneDX SBOM was detected",
            value=0,
        )
    return _gate(
        "sbom",
        "not_required",
        "no SBOM detected; record a not-applicable reason before publishing artifacts",
        value=0,
    )


def _gate(
    gate_id: str,
    status: str,
    message: str,
    *,
    value: object,
) -> dict[str, Any]:
    return {
        "id": gate_id,
        "status": status,
        "value": value,
        "message": message,
    }


def _verdict(gates: list[dict[str, Any]]) -> str:
    statuses = {str(gate["status"]) for gate in gates}
    if "blocked" in statuses:
        return "blocked"
    if "warning" in statuses:
        return "warning"
    return "passed"


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    latest = report["verifyEvidence"]["latest"]
    return {
        "auditScore": report["audit"]["overall"],
        "readinessVerdict": report["readiness"]["verdict"],
        "verifyEvidenceVerdict": latest["verdict"] if latest else "missing",
        "generatedDriftActionable": report["drift"]["summary"]["actionable"],
        "instructionQualityStatus": report["instructionQuality"]["summary"]["status"],
        "firstAgentLifecycleStatus": report["firstAgentTask"]["lifecycle"]["status"],
        "docsFanoutVerdict": report["docsFanout"]["contract"]["verdict"],
        "effectivenessVerdict": report["effectiveness"]["verdict"],
        "maturityLevel": report["maturity"]["currentLevel"],
        "maturityNextLevel": report["maturity"]["nextLevel"],
        "repoMapUnknowns": len(report["index"]["repoMap"]["unknowns"]),
        "sbomCount": report["index"]["summary"]["sbomCount"],
    }


def _source_report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": report["schemaVersion"],
        "generatedAt": report["generatedAt"],
        "detectedStack": report["detectedStack"],
        "readiness": report["readiness"],
        "audit": report["audit"],
        "verifyEvidence": report["verifyEvidence"],
        "maturity": report["maturity"],
        "releaseControls": report["releaseControls"],
        "docsFanout": report["docsFanout"],
        "nextActions": report["nextActions"],
    }


def _next_actions(report: dict[str, Any], gates: list[dict[str, Any]]) -> list[str]:
    actions = [
        f"Resolve release-check gate {gate['id']}: {gate['message']}"
        for gate in gates
        if gate["status"] in {"blocked", "warning"}
    ]
    actions.extend(report["nextActions"])
    return _dedupe(actions)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
