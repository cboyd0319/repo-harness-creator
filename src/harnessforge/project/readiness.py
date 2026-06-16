from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.models import DriftResult, ProjectProfile
from ..core.paths import path_from_relative_text
from ..evidence.context_budget import (
    ContextBudgetReport,
    analyze_context_budget,
    context_budget_to_dict,
)
from ..evidence.effectiveness_inventory import (
    EffectivenessItem,
    analyze_effectiveness_inventory,
    effectiveness_item_to_dict,
)
from ..evidence.first_agent import (
    FirstAgentLifecycleReport,
    analyze_first_agent_lifecycle,
    first_agent_lifecycle_to_dict,
)
from ..evidence.governance_inventory import (
    GovernanceItem,
    analyze_governance_inventory,
    governance_item_to_dict,
)
from ..evidence.high_risk_acceptance import (
    HighRiskAcceptanceReport,
    analyze_high_risk_acceptance,
    high_risk_acceptance_to_dict,
)
from ..evidence.instruction_quality import (
    InstructionQualityReport,
    analyze_instruction_quality,
    instruction_quality_to_dict,
)
from ..evidence.skill_wiring import (
    SkillWiringReport,
    analyze_skill_wiring,
    skill_wiring_to_dict,
)
from ..evidence.verify_evidence import (
    VerifyEvidenceReport,
    analyze_verify_evidence,
    verify_evidence_gate_blockers,
    verify_evidence_report_to_dict,
)
from ..evidence.workflow_inventory import (
    WorkItem,
    WorkflowItem,
    analyze_workflow_inventory,
    work_item_to_dict,
    workflow_to_dict,
)
from ..generation.update import build_drift_report
from .detect import MISSING_VERIFICATION_COMMAND
from .spec_system import (
    SpecSystemReport,
    analyze_spec_system,
    instruction_routes_to_specs,
)


INSTRUCTION_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
)

AGENT_SETUP_WORKFLOWS = (
    ".github/workflows/copilot-setup-steps.yml",
    ".github/workflows/copilot-setup-steps.yaml",
)

REVIEW_STATUS_PENDING = "pending_review"
REVIEW_STATUS_ACCEPTED = "accepted_advisory"


@dataclass(frozen=True)
class ReviewSurface:
    path: str
    category: str
    status: str
    source: str
    message: str


@dataclass(frozen=True)
class ReadinessReport:
    target: str
    verdict: str
    warnings: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_actions: tuple[str, ...]
    source_of_truth: tuple[str, ...]
    runnable_checks: tuple[str, ...]
    generated_drift: tuple[DriftResult, ...]
    review_required: tuple[str, ...]
    review_surfaces: tuple[ReviewSurface, ...]
    config_precedence: tuple[str, ...]
    workflow_inventory: tuple[WorkflowItem, ...]
    work_item_inventory: tuple[WorkItem, ...]
    context_budget: ContextBudgetReport
    governance_inventory: tuple[GovernanceItem, ...]
    effectiveness_inventory: tuple[EffectivenessItem, ...]
    instruction_quality: InstructionQualityReport
    skill_wiring: SkillWiringReport
    verify_evidence: VerifyEvidenceReport
    verify_evidence_required: bool
    first_agent_lifecycle: FirstAgentLifecycleReport
    high_risk_acceptance: HighRiskAcceptanceReport


def inspect_readiness(
    profile: ProjectProfile, *, require_verify_evidence: bool = False
) -> ReadinessReport:
    file_set = set(profile.files)
    drift = build_drift_report(profile.root)
    ownership = _generated_ownership(profile.root)
    spec_report = analyze_spec_system(profile.root, profile.files)
    inventory = analyze_workflow_inventory(profile.root, profile.files)
    context_budget = analyze_context_budget(profile.root, profile.files)
    governance_inventory = analyze_governance_inventory(profile.files)
    effectiveness_inventory = analyze_effectiveness_inventory(profile.files)
    instruction_quality = analyze_instruction_quality(profile.root, profile.files)
    skill_wiring = analyze_skill_wiring(profile.root, profile.files)
    verify_evidence = analyze_verify_evidence(profile.root, profile.files)
    first_agent_lifecycle = analyze_first_agent_lifecycle(profile.root, profile.files)
    high_risk_acceptance = analyze_high_risk_acceptance(
        profile.root,
        profile.files,
    )
    runnable_checks = tuple(
        command
        for command in profile.verification_commands
        if not _is_missing_verification(command)
    )

    warnings: list[str] = []
    blocked: list[str] = []
    next_actions: list[str] = []
    review_surfaces: list[ReviewSurface] = []
    source_of_truth = _source_of_truth(profile, file_set, spec_report)

    if not runnable_checks:
        blocked.append("No project verification check detected.")
        next_actions.append(
            "Pass --command with the smallest reliable project check or add a "
            "repo-owned verification script."
        )

    drift_items = tuple(item for item in drift if _is_actionable_drift(item))
    if drift_items:
        warnings.append(
            "generated drift detected; review the drift report before updating."
        )
        next_actions.append(
            "Run harnessforge update --target <repo> --drift-report to inspect "
            "generated-file drift."
        )

    for file_name in INSTRUCTION_FILES:
        if file_name in file_set and ownership.get(file_name) != "generated":
            message = (
                f"{file_name} already exists; confirm it routes agents to "
                "current project instructions."
            )
            review_surfaces.append(
                _review_surface(
                    path=file_name,
                    category="instruction-router",
                    source="instruction-files",
                    message=message,
                    acceptance=high_risk_acceptance,
                )
            )

    for marker in source_of_truth:
        warnings.append(
            f"{marker} detected; confirm instruction files route agents to that "
            "source of truth."
        )
    warnings.extend(spec_report.quality_warnings)
    warnings.extend(_workflow_warnings(inventory, high_risk_acceptance))
    warnings.extend(context_budget.warnings)
    warnings.extend(
        _governance_warnings(governance_inventory.items, high_risk_acceptance)
    )
    warnings.extend(effectiveness_inventory.warnings)
    warnings.extend(instruction_quality.warnings)
    warnings.extend(skill_wiring.warnings)
    warnings.extend(verify_evidence.warnings)
    warnings.extend(first_agent_lifecycle.warnings)
    warnings.extend(high_risk_acceptance.warnings)
    if require_verify_evidence:
        verify_evidence_blockers = verify_evidence_gate_blockers(verify_evidence)
        blocked.extend(verify_evidence_blockers)
        if verify_evidence_blockers:
            next_actions.append(
                "Run harnessforge verify --target <repo> --run --json-report "
                "docs/harness/evidence/verify-<date>.json before release gating."
            )
    if source_of_truth:
        next_actions.append(
            "Review detected source-of-truth docs before enhancing or generating "
            "instruction files."
        )
    if (
        _unaccepted_workflow_review_required(inventory.workflows, high_risk_acceptance)
        or inventory.work_items
    ):
        next_actions.append(
            "Review workflow and work-item inventory before agent automation relies on it."
        )
    if context_budget.warnings:
        next_actions.append(
            "Review context budget findings before expanding instruction files."
        )
    if _unaccepted_governance_review_required(
        governance_inventory.items,
        high_risk_acceptance,
    ):
        next_actions.append(
            "Review governance inventory before giving agents tool, environment, or runner access."
        )
    if effectiveness_inventory.items:
        next_actions.append(
            "Review effectiveness eval inventory before making harness performance claims."
        )
    if instruction_quality.warnings:
        next_actions.append(
            "Review instruction quality and context budget findings before expanding startup instructions."
        )
    next_actions.extend(skill_wiring.next_actions)
    next_actions.extend(verify_evidence.next_actions)
    next_actions.extend(first_agent_lifecycle.next_actions)
    instruction_text = _instruction_text(profile.root, file_set)
    if instruction_text and not instruction_routes_to_specs(instruction_text, spec_report):
        review_surfaces.append(
            ReviewSurface(
                path=_primary_instruction_path(file_set),
                category="source-of-truth-routing",
                status=REVIEW_STATUS_PENDING,
                source="spec-system",
                message=(
                    "Instruction files do not route agents to detected "
                    "source-of-truth specs."
                ),
            )
        )

    review_surfaces.extend(
        _governance_review_surfaces(
            governance_inventory.items,
            high_risk_acceptance,
        )
    )
    review_surfaces.extend(_effectiveness_review_surfaces(effectiveness_inventory.items))
    review_surfaces.extend(
        _workflow_review_surfaces(
            inventory.workflows,
            high_risk_acceptance,
        )
    )
    if any(
        item in file_set and not high_risk_acceptance.accepts_path(item)
        for item in AGENT_SETUP_WORKFLOWS
    ):
        warnings.append(
            "GitHub agent setup workflow detected; review runner, permissions, "
            "and credential scope."
        )

    review_surfaces = _dedupe_review_surfaces(review_surfaces)
    review_required = [
        surface.message
        for surface in review_surfaces
        if surface.status == REVIEW_STATUS_PENDING
    ]

    if review_required:
        next_actions.append(
            "Review high-risk harness surfaces before relying on generated guidance."
        )

    verdict = (
        "blocked" if blocked else "warning" if warnings or review_required else "ready"
    )
    if verdict == "ready":
        next_actions.append(
            "Run harnessforge init --target <repo> --dry-run to preview generated files."
        )

    return ReadinessReport(
        target=profile.name,
        verdict=verdict,
        warnings=tuple(_dedupe(warnings)),
        blocked_reasons=tuple(_dedupe(blocked)),
        next_actions=tuple(_dedupe(next_actions)),
        source_of_truth=source_of_truth,
        runnable_checks=runnable_checks,
        generated_drift=drift_items,
        review_required=tuple(_dedupe(review_required)),
        review_surfaces=tuple(review_surfaces),
        config_precedence=profile.config_precedence,
        workflow_inventory=inventory.workflows,
        work_item_inventory=inventory.work_items,
        context_budget=context_budget,
        governance_inventory=governance_inventory.items,
        effectiveness_inventory=effectiveness_inventory.items,
        instruction_quality=instruction_quality,
        skill_wiring=skill_wiring,
        verify_evidence=verify_evidence,
        verify_evidence_required=require_verify_evidence,
        first_agent_lifecycle=first_agent_lifecycle,
        high_risk_acceptance=high_risk_acceptance,
    )


def readiness_to_dict(report: ReadinessReport) -> dict[str, Any]:
    return {
        "target": report.target,
        "verdict": report.verdict,
        "warnings": list(report.warnings),
        "blockedReasons": list(report.blocked_reasons),
        "nextActions": list(report.next_actions),
        "sourceOfTruth": list(report.source_of_truth),
        "runnableChecks": list(report.runnable_checks),
        "generatedDrift": [_drift_to_dict(item) for item in report.generated_drift],
        "reviewRequired": list(report.review_required),
        "reviewSurfaces": [
            _review_surface_to_dict(item) for item in report.review_surfaces
        ],
        "reviewStatusSummary": _review_status_summary(report.review_surfaces),
        "configPrecedence": list(report.config_precedence),
        "workflowInventory": [
            workflow_to_dict(item) for item in report.workflow_inventory
        ],
        "workItemInventory": [
            work_item_to_dict(item) for item in report.work_item_inventory
        ],
        "contextBudget": context_budget_to_dict(report.context_budget),
        "governanceInventory": [
            governance_item_to_dict(item) for item in report.governance_inventory
        ],
        "effectivenessInventory": [
            effectiveness_item_to_dict(item)
            for item in report.effectiveness_inventory
        ],
        "instructionQuality": instruction_quality_to_dict(report.instruction_quality),
        "skillWiring": skill_wiring_to_dict(report.skill_wiring),
        "verifyEvidence": verify_evidence_report_to_dict(report.verify_evidence),
        "verifyEvidenceRequired": report.verify_evidence_required,
        "firstAgentLifecycle": first_agent_lifecycle_to_dict(
            report.first_agent_lifecycle
        ),
        "highRiskAcceptance": high_risk_acceptance_to_dict(
            report.high_risk_acceptance
        ),
    }


def format_readiness(report: ReadinessReport) -> str:
    lines = [f"Readiness: {report.verdict}", ""]
    _append_section(lines, "Blocked reasons", report.blocked_reasons)
    _append_section(lines, "Warnings", report.warnings)
    _append_section(lines, "Source of truth", report.source_of_truth)
    _append_section(lines, "Runnable checks", report.runnable_checks)
    _append_section(
        lines,
        "Generated drift",
        tuple(
            f"{item.path}: file={item.file_status}, "
            f"template={item.template_status}, action={item.recommended_action}"
            for item in report.generated_drift
        ),
    )
    _append_section(lines, "Review required", report.review_required)
    _append_section(
        lines,
        "Review surfaces",
        tuple(
            f"{item.path}: {item.category}, status={item.status}, "
            f"source={item.source}"
            for item in report.review_surfaces
        ),
    )
    _append_section(lines, "Config precedence", report.config_precedence)
    _append_section(
        lines,
        "Workflow inventory",
        tuple(
            (
                f"{item.path}: {item.kind}, {item.format}, "
                f"surfaces={', '.join(item.surfaces) or 'none detected'}"
            )
            for item in report.workflow_inventory
        ),
    )
    _append_section(
        lines,
        "Work-item inventory",
        tuple(f"{item.path}: {item.kind}" for item in report.work_item_inventory),
    )
    _append_section(
        lines,
        "Context budget",
        tuple(
            f"{item.path}: {item.line_count} lines, {item.char_count} chars"
            for item in report.context_budget.instruction_files
        ),
    )
    _append_section(
        lines,
        "Instruction quality",
        tuple(
            f"{item.path}: {item.status}, score={item.score}/100, "
            f"budget={item.budget_status}, words={item.word_count}"
            for item in report.instruction_quality.files
        ),
    )
    _append_section(
        lines,
        "Skill wiring",
        (
            f"{report.skill_wiring.skill_path}: {report.skill_wiring.status}, "
            f"routes={', '.join(report.skill_wiring.instruction_routes) or 'none'}",
        ),
    )
    _append_section(
        lines,
        "Duplicate instruction blocks",
        tuple(
            f"{item.left} <-> {item.right}: {item.line_count} repeated lines"
            for item in report.context_budget.duplicate_instruction_blocks
        ),
    )
    _append_section(
        lines,
        "Governance inventory",
        tuple(
            f"{item.path}: {item.category}, surfaces={', '.join(item.surfaces)}"
            for item in report.governance_inventory
        ),
    )
    _append_section(
        lines,
        "High-risk acceptance",
        tuple(
            f"{item.path}: {item.category}, decision={item.decision}"
            for item in report.high_risk_acceptance.accepted_surfaces
        ),
    )
    _append_section(
        lines,
        "Effectiveness inventory",
        tuple(
            f"{item.path}: {item.category}, signals={', '.join(item.signals)}"
            for item in report.effectiveness_inventory
        ),
    )
    _append_section(
        lines,
        "Verify evidence",
        tuple(
            f"{item.path}: {item.verdict or 'invalid'}, "
            f"mode={item.mode or 'unknown'}, recorded={item.recorded_at or 'unknown'}, "
            f"issues={', '.join(item.issues) or 'none'}"
            for item in report.verify_evidence.reports
        ),
    )
    _append_section(lines, "Next actions", report.next_actions)
    return "\n".join(lines).rstrip()


def _review_surface(
    *,
    path: str,
    category: str,
    source: str,
    message: str,
    acceptance: HighRiskAcceptanceReport,
) -> ReviewSurface:
    return ReviewSurface(
        path=path,
        category=category,
        status=(
            REVIEW_STATUS_ACCEPTED
            if acceptance.accepts_path(path)
            else REVIEW_STATUS_PENDING
        ),
        source=source,
        message=message,
    )


def _workflow_review_surfaces(
    workflows: tuple[WorkflowItem, ...],
    acceptance: HighRiskAcceptanceReport,
) -> tuple[ReviewSurface, ...]:
    surfaces: list[ReviewSurface] = []
    for item in workflows:
        for message in item.review_required:
            surfaces.append(
                _review_surface(
                    path=item.path,
                    category="workflow",
                    source="workflow-inventory",
                    message=message,
                    acceptance=acceptance,
                )
            )
    return tuple(surfaces)


def _governance_review_surfaces(
    items: tuple[GovernanceItem, ...],
    acceptance: HighRiskAcceptanceReport,
) -> tuple[ReviewSurface, ...]:
    surfaces: list[ReviewSurface] = []
    for item in items:
        for message in item.review_required:
            surfaces.append(
                _review_surface(
                    path=item.path,
                    category=item.category,
                    source="governance-inventory",
                    message=message,
                    acceptance=acceptance,
                )
            )
    return tuple(surfaces)


def _effectiveness_review_surfaces(
    items: tuple[EffectivenessItem, ...],
) -> tuple[ReviewSurface, ...]:
    surfaces: list[ReviewSurface] = []
    for item in items:
        for message in item.review_required:
            surfaces.append(
                ReviewSurface(
                    path=item.path,
                    category=item.category,
                    status=REVIEW_STATUS_PENDING,
                    source="effectiveness-inventory",
                    message=message,
                )
            )
    return tuple(surfaces)


def _primary_instruction_path(file_set: set[str]) -> str:
    for file_name in INSTRUCTION_FILES:
        if file_name in file_set:
            return file_name
    return "AGENTS.md"


def _review_surface_to_dict(surface: ReviewSurface) -> dict[str, str]:
    return {
        "path": surface.path,
        "category": surface.category,
        "status": surface.status,
        "source": surface.source,
        "message": surface.message,
    }


def _review_status_summary(
    surfaces: tuple[ReviewSurface, ...],
) -> dict[str, int]:
    return {
        "total": len(surfaces),
        "pendingReview": sum(
            1 for item in surfaces if item.status == REVIEW_STATUS_PENDING
        ),
        "acceptedAdvisory": sum(
            1 for item in surfaces if item.status == REVIEW_STATUS_ACCEPTED
        ),
    }


def _source_of_truth(
    profile: ProjectProfile, file_set: set[str], spec_report: SpecSystemReport
) -> tuple[str, ...]:
    sources: list[str] = list(spec_report.source_labels)
    if "structured project specs" in set(profile.workspace_markers) | set(
        profile.routing_markers
    ):
        sources.append("structured project specs")
    if any(file.startswith("aspec/") for file in file_set):
        sources.append("aspec")
    for file in sorted(file_set):
        path = Path(file)
        if path.name == "0000-template.md" and any(
            part in {"work-items", "work_items", "workitems"} for part in path.parts
        ):
            sources.append(f"work-item template: {file}")
    return tuple(_dedupe(sources))


def _instruction_text(root: Path, file_set: set[str]) -> str:
    for file_name in INSTRUCTION_FILES:
        if file_name not in file_set:
            continue
        path = root / path_from_relative_text(file_name)
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return ""


def _generated_ownership(root: Path) -> dict[str, str]:
    manifest_path = root / "docs/harness/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    generated_files = manifest.get("generatedFiles", {})
    if not isinstance(generated_files, dict):
        return {}
    ownership: dict[str, str] = {}
    for path_text, metadata in generated_files.items():
        if not isinstance(path_text, str) or not isinstance(metadata, dict):
            continue
        try:
            normalized = str(path_from_relative_text(path_text))
        except ValueError:
            continue
        ownership[normalized] = str(metadata.get("ownership", "generated"))
    return ownership


def _is_missing_verification(command: str) -> bool:
    return command == MISSING_VERIFICATION_COMMAND or command.startswith(
        "REVIEW REQUIRED:"
    )


def _is_actionable_drift(item: DriftResult) -> bool:
    return item.file_status in {
        "missing",
        "modified",
        "unsafe-path",
    } or item.template_status in {"changed", "missing"}


def _workflow_warnings(
    inventory: Any,
    acceptance: HighRiskAcceptanceReport,
) -> tuple[str, ...]:
    if not inventory.warnings:
        return ()
    unresolved = _unaccepted_workflow_review_required(
        inventory.workflows,
        acceptance,
    )
    result: list[str] = []
    for warning in inventory.warnings:
        if warning.startswith("workflow inventory") and not unresolved:
            continue
        result.append(warning)
    return tuple(result)


def _governance_warnings(
    items: tuple[GovernanceItem, ...],
    acceptance: HighRiskAcceptanceReport,
) -> tuple[str, ...]:
    unresolved = _unaccepted_governance_review_required(items, acceptance)
    if not items or not unresolved:
        return ()
    return (
        f"governance inventory detected {len(items)} permission, "
        "environment, or agent-control surface(s).",
    )


def _unaccepted_workflow_review_required(
    workflows: tuple[WorkflowItem, ...],
    acceptance: HighRiskAcceptanceReport,
) -> tuple[str, ...]:
    result: list[str] = []
    for item in workflows:
        if item.review_required and acceptance.accepts_path(item.path):
            continue
        result.extend(item.review_required)
    return tuple(_dedupe(result))


def _unaccepted_governance_review_required(
    items: tuple[GovernanceItem, ...],
    acceptance: HighRiskAcceptanceReport,
) -> tuple[str, ...]:
    result: list[str] = []
    for item in items:
        if item.review_required and acceptance.accepts_path(item.path):
            continue
        result.extend(item.review_required)
    return tuple(_dedupe(result))


def _append_section(lines: list[str], title: str, values: tuple[str, ...]) -> None:
    if not values:
        return
    lines.append(f"{title}:")
    for value in values:
        lines.append(f"  - {value}")
    lines.append("")


def _drift_to_dict(item: DriftResult) -> dict[str, str]:
    return {
        "path": item.path,
        "ownership": item.ownership,
        "fileStatus": item.file_status,
        "templateStatus": item.template_status,
        "reason": item.reason,
        "recommendedAction": item.recommended_action,
    }


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _dedupe_review_surfaces(values: list[ReviewSurface]) -> list[ReviewSurface]:
    seen: set[tuple[str, str, str, str, str]] = set()
    result: list[ReviewSurface] = []
    for value in values:
        key = (
            value.path,
            value.category,
            value.status,
            value.source,
            value.message,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result
