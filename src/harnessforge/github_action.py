from __future__ import annotations

import os
import sys
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .assessment.audit import audit_target, audit_to_dict, format_audit, render_html_report
from .core.doctor import doctor_report, format_doctor
from .core.redact import redact_local_paths
from .core.reports import relative_to_target, report_path, write_json_payload
from .evidence.release_check import (
    build_release_check,
    format_release_check,
    release_check_exit_code,
    write_markdown_release_check,
)
from .evidence.report import build_report, format_report, write_markdown_report
from .generation.generate import create_harness
from .generation.update import plan_or_apply_update
from .project.detect import detect_project
from .project.finalize_review import (
    build_review_finalization_plan,
    format_review_finalization_plan,
)
from .project.readiness import inspect_readiness
from .project.state_migration import (
    build_state_migration_plan,
    format_state_migration_plan,
)
from .project.sync import format_sync_check, sync_check_to_dict, sync_exit_code
from .project.verify import (
    DEFAULT_TIMEOUT_SECONDS,
    build_verify_plan,
    compact_verify_report_to_dict,
    format_verify_plan,
    run_verify_checks,
    verify_report_to_dict,
)


def main() -> int:
    try:
        return run_from_env(os.environ)
    except ValueError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {redact_local_paths(str(exc))}", file=sys.stderr)
        return 2


def run_from_env(env: Mapping[str, str]) -> int:
    command = env.get("INPUT_COMMAND", "audit").strip().lower()
    target = Path(env.get("INPUT_TARGET", ".")).resolve()
    min_score = _score_input(env.get("INPUT_MIN_SCORE", "85"), "min-score")
    fail_on_score = _bool_input(env.get("INPUT_FAIL_ON_SCORE", "true"))
    html_report = env.get("INPUT_HTML_REPORT", "").strip()
    json_report = env.get("INPUT_JSON_REPORT", "").strip()
    markdown_report = env.get("INPUT_MARKDOWN_REPORT", "").strip()
    generation_max_files = _int_input(
        env.get("INPUT_GENERATION_MAX_FILES", "4000"),
        "generation-max-files",
    )
    if generation_max_files <= 0:
        raise ValueError("generation-max-files must be greater than 0")
    generation_component_limit = _int_input(
        env.get("INPUT_GENERATION_COMPONENT_LIMIT", "80"),
        "generation-component-limit",
    )
    if generation_component_limit <= 0:
        raise ValueError("generation-component-limit must be greater than 0")
    changed_files = 0

    if command == "doctor":
        report = doctor_report()
        text = format_doctor(report)
        print(text)
        _summary(env, "HarnessForge Doctor", text)
        _output(
            env,
            {
                "overall-score": "",
                "bottleneck": "",
                "report-json": "",
                "report-html": "",
                "report-markdown": "",
                "changed-files": "0",
                "verify-verdict": "",
                "readiness-verdict": "",
                "sync-exit-code": "",
                "docs-fanout-verdict": "",
                "release-verdict": "",
            }
        )
        return 0 if report["ok"] else 1

    if command == "init":
        _, writes = create_harness(
            target,
            agent_file=env.get("INPUT_AGENT_FILE", "AGENTS.md"),
            force=_bool_input(env.get("INPUT_FORCE", "false")),
            enhance_existing=_bool_input(env.get("INPUT_ENHANCE_EXISTING", "false")),
            with_ci_workflow=_bool_input(env.get("INPUT_WITH_CI_WORKFLOW", "false")),
            platform_contract=env.get("INPUT_PLATFORM_CONTRACT", "cross-platform"),
            max_files=generation_max_files,
            max_components=generation_component_limit,
        )
        changed_files = sum(
            1 for write in writes if write.status in {"written", "enhanced"}
        )
        result = audit_target(target)
        _print_writes(target, writes)
    elif command == "update":
        _, _, writes = plan_or_apply_update(
            target,
            apply=_bool_input(env.get("INPUT_APPLY", "false")),
            force=_bool_input(env.get("INPUT_FORCE", "false")),
            enhance_existing=_bool_input(env.get("INPUT_ENHANCE_EXISTING", "false")),
            agent_file=env.get("INPUT_AGENT_FILE", "AGENTS.md"),
            with_ci_workflow=_bool_input(env.get("INPUT_WITH_CI_WORKFLOW", "false")),
            platform_contract=env.get("INPUT_PLATFORM_CONTRACT", "cross-platform"),
            max_files=generation_max_files,
            max_components=generation_component_limit,
        )
        changed_files = sum(
            1 for write in writes if write.status in {"written", "enhanced"}
        )
        result = audit_target(target)
        if writes:
            _print_writes(target, writes)
        else:
            print("No files changed. Set apply=true to create safe missing artifacts.")
    elif command == "audit":
        result = audit_target(target)
    elif command == "sync":
        return _run_sync_command(env, target, json_report, html_report)
    elif command == "verify":
        return _run_verify_command(env, target, json_report, html_report)
    elif command == "report":
        return _run_report_command(
            env,
            target,
            json_report,
            html_report,
            markdown_report,
        )
    elif command == "release-check":
        return _run_release_check_command(
            env,
            target,
            json_report,
            html_report,
            markdown_report,
        )
    elif command == "finalize-review":
        return _run_finalize_review_command(
            env,
            target,
            json_report,
            html_report,
            markdown_report,
        )
    elif command == "migrate-state":
        return _run_migrate_state_command(
            env,
            target,
            json_report,
            html_report,
            markdown_report,
        )
    else:
        raise ValueError(
            "command must be one of: audit, init, update, sync, verify, "
            "report, release-check, finalize-review, migrate-state, doctor"
        )

    json_path = _write_json_report(json_report, target, result)
    html_path = _write_html_report(html_report, target, result)
    text_report = format_audit(result)
    print(text_report)
    _summary(env, "HarnessForge Audit", _summary_markdown(result, changed_files))
    _output(
        env,
        {
            "overall-score": str(result.overall),
            "bottleneck": result.bottleneck,
            "report-json": json_path,
            "report-html": html_path,
            "report-markdown": "",
            "changed-files": str(changed_files),
            "verify-verdict": "",
            "readiness-verdict": "",
            "sync-exit-code": "",
            "docs-fanout-verdict": "",
            "release-verdict": "",
        }
    )
    if fail_on_score and result.overall < min_score:
        return 1
    return 0


def _run_sync_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=sync")
    commands = _commands_input(env.get("INPUT_SYNC_COMMAND", ""))
    profile = detect_project(target, explicit_commands=commands)
    report = inspect_readiness(
        profile,
        require_verify_evidence=_bool_input(
            env.get("INPUT_REQUIRE_VERIFY_EVIDENCE", "false")
        ),
    )
    exit_code = sync_exit_code(report)
    payload = sync_check_to_dict(report, exit_code)
    json_path = write_json_payload(json_report, target, payload)
    text_report = format_sync_check(report)
    print(text_report)
    _summary(env, "HarnessForge Sync", _sync_summary_markdown(report, exit_code))
    _output(
        env,
        {
            "overall-score": "",
            "bottleneck": "",
            "report-json": json_path,
            "report-html": "",
            "report-markdown": "",
            "changed-files": "0",
            "verify-verdict": "",
            "readiness-verdict": report.verdict,
            "sync-exit-code": str(exit_code),
            "docs-fanout-verdict": "",
            "release-verdict": "",
        },
    )
    return exit_code


def _run_verify_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=verify")
    commands = _commands_input(env.get("INPUT_VERIFY_COMMAND", ""))
    timeout_seconds = _float_input(
        env.get("INPUT_VERIFY_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)),
        "verify-timeout-seconds",
    )
    if timeout_seconds <= 0:
        raise ValueError("verify-timeout-seconds must be greater than 0")
    profile = detect_project(target, explicit_commands=commands)
    if _bool_input(env.get("INPUT_VERIFY_RUN", "false")):
        report = run_verify_checks(
            profile,
            explicit_commands=commands,
            timeout_seconds=timeout_seconds,
        )
    else:
        report = build_verify_plan(profile, explicit_commands=commands)

    payload = verify_report_to_dict(report)
    json_path = write_json_payload(json_report, target, payload)
    verify_summary_path = write_json_payload(
        env.get("INPUT_VERIFY_SUMMARY", "").strip(),
        target,
        compact_verify_report_to_dict(report),
    )
    text_report = format_verify_plan(report)
    print(text_report)
    _summary(env, "HarnessForge Verify", _verify_summary_markdown(report))
    _output(
        env,
        {
            "overall-score": "",
            "bottleneck": "",
            "report-json": json_path,
            "report-html": "",
            "report-markdown": "",
            "verify-summary": verify_summary_path,
            "changed-files": "0",
            "verify-verdict": report.verdict,
            "readiness-verdict": "",
            "sync-exit-code": "",
            "docs-fanout-verdict": "",
            "release-verdict": "",
        },
    )
    if report.mode != "run":
        return 0
    if report.verdict == "passed":
        return 0
    if report.verdict == "failed":
        return 1
    return 2


def _run_report_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
    markdown_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=report")
    max_files = _int_input(
        env.get("INPUT_REPORT_MAX_FILES", "4000"),
        "report-max-files",
    )
    if max_files <= 0:
        raise ValueError("report-max-files must be greater than 0")
    max_components = _int_input(
        env.get("INPUT_REPORT_COMPONENT_LIMIT", "80"),
        "report-component-limit",
    )
    if max_components <= 0:
        raise ValueError("report-component-limit must be greater than 0")
    payload = build_report(
        target,
        explicit_commands=_commands_input(env.get("INPUT_REPORT_COMMAND", "")),
        max_files=max_files,
        max_components=max_components,
        since=env.get("INPUT_REPORT_SINCE", "").strip() or None,
        require_verify_evidence=_bool_input(
            env.get("INPUT_REQUIRE_VERIFY_EVIDENCE", "false")
        ),
        require_docs_fanout_budget=_bool_input(
            env.get("INPUT_REQUIRE_DOCS_FANOUT_BUDGET", "false")
        ),
    )
    json_path = write_json_payload(json_report, target, payload)
    markdown_path = write_markdown_report(markdown_report, target, payload)
    text_report = format_report(payload)
    print(text_report)
    _summary(env, "HarnessForge Report", _report_summary_markdown(payload))
    _output(
        env,
        {
            "overall-score": str(payload["audit"]["overall"]),
            "bottleneck": payload["audit"]["bottleneck"],
            "report-json": json_path,
            "report-html": "",
            "report-markdown": markdown_path,
            "changed-files": "0",
            "verify-verdict": "",
            "readiness-verdict": payload["readiness"]["verdict"],
            "sync-exit-code": "",
            "docs-fanout-verdict": payload["docsFanout"]["contract"]["verdict"],
            "release-verdict": "",
        },
    )
    return 2 if payload["docsFanout"]["contract"]["verdict"] == "blocked" else 0


def _run_release_check_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
    markdown_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=release-check")
    max_files = _int_input(
        env.get("INPUT_REPORT_MAX_FILES", "4000"),
        "report-max-files",
    )
    if max_files <= 0:
        raise ValueError("report-max-files must be greater than 0")
    max_components = _int_input(
        env.get("INPUT_REPORT_COMPONENT_LIMIT", "80"),
        "report-component-limit",
    )
    if max_components <= 0:
        raise ValueError("report-component-limit must be greater than 0")
    payload = build_release_check(
        target,
        explicit_commands=_commands_input(env.get("INPUT_REPORT_COMMAND", "")),
        max_files=max_files,
        max_components=max_components,
        min_score=_score_input(env.get("INPUT_MIN_SCORE", "85"), "min-score"),
        since=env.get("INPUT_REPORT_SINCE", "").strip() or None,
        require_docs_fanout_budget=_bool_input(
            env.get("INPUT_REQUIRE_DOCS_FANOUT_BUDGET", "false")
        ),
        require_sbom=_bool_input(env.get("INPUT_REQUIRE_SBOM", "false")),
    )
    json_path = write_json_payload(json_report, target, payload)
    markdown_path = write_markdown_release_check(markdown_report, target, payload)
    text_report = format_release_check(payload)
    print(text_report)
    _summary(env, "HarnessForge Release Check", _release_check_summary_markdown(payload))
    _output(
        env,
        {
            "overall-score": str(payload["summary"]["auditScore"]),
            "bottleneck": payload["sourceReport"]["audit"]["bottleneck"],
            "report-json": json_path,
            "report-html": "",
            "report-markdown": markdown_path,
            "changed-files": "0",
            "verify-verdict": "",
            "readiness-verdict": payload["summary"]["readinessVerdict"],
            "sync-exit-code": "",
            "docs-fanout-verdict": payload["summary"]["docsFanoutVerdict"],
            "release-verdict": payload["verdict"],
        },
    )
    return release_check_exit_code(payload)


def _run_finalize_review_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
    markdown_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=finalize-review")
    if markdown_report:
        raise ValueError("markdown-report is not supported for command=finalize-review")
    plan = build_review_finalization_plan(
        target,
        apply=_bool_input(env.get("INPUT_APPLY", "false")),
        accept_detected_high_risk=_bool_input(
            env.get("INPUT_ACCEPT_DETECTED_HIGH_RISK", "false")
        ),
        explicit_commands=_commands_input(env.get("INPUT_REPORT_COMMAND", "")),
        reviewed_by=_commands_input(env.get("INPUT_REVIEWED_BY", "")),
        evidence_refs=_commands_input(env.get("INPUT_EVIDENCE_REF", "")),
    )
    payload = plan.payload
    json_path = write_json_payload(json_report, target, payload)
    text_report = format_review_finalization_plan(payload)
    print(text_report)
    _summary(
        env,
        "HarnessForge Review Finalization",
        _finalize_review_summary_markdown(payload),
    )
    _output(
        env,
        {
            "overall-score": "",
            "bottleneck": "",
            "report-json": json_path,
            "report-html": "",
            "report-markdown": "",
            "changed-files": str(payload["changedFiles"]),
            "verify-verdict": "",
            "readiness-verdict": payload["readinessBefore"]["verdict"],
            "sync-exit-code": "",
            "docs-fanout-verdict": "",
            "release-verdict": "",
        },
    )
    return 0


def _run_migrate_state_command(
    env: Mapping[str, str],
    target: Path,
    json_report: str,
    html_report: str,
    markdown_report: str,
) -> int:
    if html_report:
        raise ValueError("html-report is not supported for command=migrate-state")
    if markdown_report:
        raise ValueError("markdown-report is not supported for command=migrate-state")
    plan = build_state_migration_plan(
        target,
        apply=_bool_input(env.get("INPUT_APPLY", "false")),
    )
    payload = plan.payload
    json_path = write_json_payload(json_report, target, payload)
    text_report = format_state_migration_plan(payload)
    print(text_report)
    _summary(env, "HarnessForge State Migration", _state_migration_summary(payload))
    _output(
        env,
        {
            "overall-score": "",
            "bottleneck": "",
            "report-json": json_path,
            "report-html": "",
            "report-markdown": "",
            "changed-files": str(payload["changedFiles"]),
            "verify-verdict": "",
            "readiness-verdict": "",
            "sync-exit-code": "",
            "docs-fanout-verdict": "",
            "release-verdict": "",
        },
    )
    return 0


def _write_json_report(path_text: str, target: Path, result: Any) -> str:
    return write_json_payload(path_text, target, audit_to_dict(result))


def _write_html_report(path_text: str, target: Path, result: Any) -> str:
    path = report_path(path_text, target)
    if path is None:
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html_report(result), encoding="utf-8")
    return relative_to_target(path, target)


def _print_writes(root: Path, writes: tuple[Any, ...]) -> None:
    print("File changes:")
    for write in writes:
        try:
            rel = write.path.resolve().relative_to(root.resolve())
        except ValueError:
            rel = write.path
        suffix = f" ({write.reason})" if write.reason else ""
        print(f"  - {write.status.upper()} {redact_local_paths(str(rel))}{suffix}")


def _summary_markdown(result: Any, changed_files: int) -> str:
    lines = [
        f"- Overall score: `{result.overall}/100`",
        f"- Bottleneck: `{result.bottleneck}`",
        f"- Changed files: `{changed_files}`",
        "",
        "| Domain | Score | Passed |",
        "| --- | ---: | ---: |",
    ]
    for domain in result.domains:
        lines.append(f"| {domain.name} | {domain.score}/5 | {domain.passed}/{domain.total} |")
    if result.recommendations:
        lines.extend(["", "Recommended next actions:"])
        lines.extend(f"- {item}" for item in result.recommendations)
    return "\n".join(lines)


def _sync_summary_markdown(report: Any, exit_code: int) -> str:
    pending_surfaces = sum(
        1 for item in report.review_surfaces if item.status == "pending_review"
    )
    accepted_surfaces = sum(
        1 for item in report.review_surfaces if item.status == "accepted_advisory"
    )
    lines = [
        f"- Verdict: `{report.verdict}`",
        f"- Exit code: `{exit_code}`",
        f"- Warnings: `{len(report.warnings)}`",
        f"- Review-required surfaces: `{len(report.review_required)}`",
        "- Review surface statuses: "
        f"`{pending_surfaces}` pending, `{accepted_surfaces}` accepted",
        "- Accepted high-risk surfaces: "
        f"`{len(report.high_risk_acceptance.accepted_surfaces)}`",
        f"- Runnable checks: `{len(report.runnable_checks)}`",
        f"- Instruction quality: `{report.instruction_quality.status}`",
        f"- Skill wiring: `{report.skill_wiring.status}`",
        f"- First-agent lifecycle: `{report.first_agent_lifecycle.lifecycle_status}`",
        f"- Verify evidence required: `{str(report.verify_evidence_required).lower()}`",
    ]
    if report.blocked_reasons:
        lines.extend(["", "Blocked reasons:"])
        lines.extend(f"- {reason}" for reason in report.blocked_reasons)
    if report.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    if report.review_required:
        lines.extend(["", "Review required:"])
        lines.extend(f"- {item}" for item in report.review_required)
    return "\n".join(lines)


def _verify_summary_markdown(report: Any) -> str:
    summary = verify_report_to_dict(report)["summary"]
    lines = [
        f"- Mode: `{report.mode}`",
        f"- Verdict: `{report.verdict}`",
        f"- Commands executed: `{str(report.commands_executed).lower()}`",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for key in ("planned", "blocked", "passed", "failed", "timedOut", "errors"):
        lines.append(f"| {key} | {summary[key]} |")
    if report.blocked_reasons:
        lines.extend(["", "Blocked reasons:"])
        lines.extend(f"- {reason}" for reason in report.blocked_reasons)
    return "\n".join(lines)


def _report_summary_markdown(payload: dict[str, Any]) -> str:
    latest_verify = payload["verifyEvidence"]["latest"]
    verify_status = latest_verify["verdict"] if latest_verify else "missing"
    repo_map = payload["index"]["repoMap"]["summary"]
    file_coverage = payload["index"]["fileCoverage"]
    verification = payload["index"]["verificationCommands"]["summary"]
    verification_classes = ", ".join(sorted(verification["classes"])) or "none"
    total_files = (
        file_coverage["totalFileCount"]
        if file_coverage["totalFileCount"] is not None
        else "unknown"
    )
    lines = [
        "| Signal | Value |",
        "| --- | --- |",
        f"| Readiness | `{payload['readiness']['verdict']}` |",
        "| Accepted high-risk surfaces | "
        f"`{payload['readiness']['highRiskAcceptance']['summary']['acceptedCount']}` |",
        f"| Audit score | `{payload['audit']['overall']}/100` |",
        f"| Generated drift | `{payload['drift']['summary']['actionable']}` actionable |",
        "| Review surfaces | "
        f"`{payload['readiness']['reviewStatusSummary']['pendingReview']}` pending, "
        f"`{payload['readiness']['reviewStatusSummary']['acceptedAdvisory']}` accepted |",
        "| Actionable review work | "
        f"`{payload['reviewWork']['unresolvedActionable']['count']}` unresolved |",
        "| Advisory review inventory | "
        f"`{payload['reviewWork']['acceptedAdvisory']['count']}` accepted |",
        "| Docs fan-out verdict | "
        f"`{payload['docsFanout']['contract']['verdict']}` "
        f"({payload['docsFanout']['diff']['classification']}) |",
        f"| Verify evidence | `{verify_status}` |",
        f"| Effectiveness | `{payload['effectiveness']['verdict']}` |",
        f"| Instruction quality | `{payload['instructionQuality']['summary']['status']}` |",
        f"| Skill wiring | `{payload['skillWiring']['status']}` |",
        f"| First-agent lifecycle | `{payload['firstAgentTask']['lifecycle']['status']}` |",
        f"| Maturity level | `{payload['maturity']['currentLevel']}` |",
        "| Policy presets | "
        f"`{payload['policyPresets']['status']}` "
        f"({len(payload['policyPresets']['recommendedPresets'])} recommended) |",
        f"| SBOM adapter | `{payload['sbomAdapter']['status']}` |",
        f"| Feature state | `{payload['featureState']['status']}` |",
        f"| Observability | `{payload['observability']['status']}` |",
        f"| Index adapters | `{payload['indexAdapters']['status']}` |",
        "| Nested instruction plan | "
        f"`{payload['nestedInstructionPlan']['status']}` "
        f"({payload['nestedInstructionPlan']['candidateCount']} candidates) |",
        "| Repo map | "
        f"`{payload['index']['summary']['componentCount']}`/"
        f"`{payload['index']['summary']['componentTotalCount']}` components, "
        f"`{repo_map['sourceOfTruthCount']}` source docs |",
        "| Verification commands | "
        f"`{verification['commandCount']}` "
        f"({verification_classes}) |",
        "| File coverage | "
        f"`{file_coverage['scannedFileCount']}` scanned / `{total_files}` total "
        f"from `{file_coverage['inventorySource']}` |",
        f"| SBOM files | `{repo_map['sbomCount']}` |",
    ]
    if payload["nextActions"]:
        lines.extend(["", "Next actions:"])
        lines.extend(f"- {item}" for item in payload["nextActions"][:5])
    return "\n".join(lines)


def _release_check_summary_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"- Verdict: `{payload['verdict']}`",
        f"- Audit score: `{payload['summary']['auditScore']}/100`",
        f"- Readiness: `{payload['summary']['readinessVerdict']}`",
        "- Accepted high-risk surfaces: "
        f"`{payload['summary']['acceptedHighRiskSurfaces']}`",
        f"- Verify evidence: `{payload['summary']['verifyEvidenceVerdict']}`",
        f"- Maturity level: `{payload['summary']['maturityLevel']}`",
        f"- Skill wiring: `{payload['summary']['skillWiringStatus']}`",
        f"- Feature state: `{payload['summary']['featureStateStatus']}`",
        f"- Observability: `{payload['summary']['observabilityStatus']}`",
        "",
        "| Gate | Status |",
        "| --- | --- |",
    ]
    for gate in payload["gates"]:
        lines.append(f"| {gate['id']} | `{gate['status']}` |")
    if payload["nextActions"]:
        lines.extend(["", "Next actions:"])
        lines.extend(f"- {item}" for item in payload["nextActions"][:5])
    return "\n".join(lines)


def _finalize_review_summary_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- Mode: `{payload['mode']}`",
            f"- Readiness before: `{payload['readinessBefore']['verdict']}`",
            f"- Planned writes: `{len(payload['plannedWrites'])}`",
            f"- Changed files: `{payload['changedFiles']}`",
            f"- High-risk surfaces: `{len(payload['highRiskSurfaces'])}`",
            "- Requires high-risk acceptance flag: "
            f"`{str(payload['review']['requiresHighRiskAcceptanceFlag']).lower()}`",
        ]
    )


def _state_migration_summary(payload: dict[str, Any]) -> str:
    legacy_count = sum(1 for item in payload["legacyFiles"] if item["exists"])
    truncated_count = sum(1 for item in payload["legacyFiles"] if item["truncated"])
    return "\n".join(
        [
            f"- Mode: `{payload['mode']}`",
            f"- Legacy files found: `{legacy_count}`",
            f"- Planned writes: `{len(payload['plannedWrites'])}`",
            f"- Changed files: `{payload['changedFiles']}`",
            f"- Truncated excerpts: `{truncated_count}`",
        ]
    )


def _summary(env: Mapping[str, str], title: str, body: str) -> None:
    path_text = env.get("GITHUB_STEP_SUMMARY")
    if not path_text:
        return
    path = Path(path_text)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {title}\n\n{body}\n")


def _output(env: Mapping[str, str], values: dict[str, str]) -> None:
    path_text = env.get("GITHUB_OUTPUT")
    if not path_text:
        return
    path = Path(path_text)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            delimiter = _output_delimiter(value)
            handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def _output_delimiter(value: str) -> str:
    value_lines = set(value.splitlines())
    while True:
        delimiter = f"harnessforge_output_{uuid.uuid4().hex}"
        if delimiter not in value_lines:
            return delimiter


def _bool_input(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_input(value: str | None, name: str) -> int:
    try:
        return int(str(value or "").strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _score_input(value: str | None, name: str) -> int:
    score = _int_input(value, name)
    if score < 0 or score > 100:
        raise ValueError(f"{name} must be between 0 and 100")
    return score


def _float_input(value: str | None, name: str) -> float:
    try:
        return float(str(value or "").strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def _commands_input(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(line.strip() for line in value.splitlines() if line.strip())


if __name__ == "__main__":
    raise SystemExit(main())
