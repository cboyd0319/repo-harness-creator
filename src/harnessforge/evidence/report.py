from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .effectiveness import build_effectiveness_assessment
from .first_agent import (
    analyze_first_agent_lifecycle,
    first_agent_lifecycle_to_dict,
)
from .maturity import build_maturity_report
from .policy_presets import build_policy_preset_report
from .sbom_adapter import build_sbom_adapter_plan
from ..audit import audit_target, audit_to_dict
from ..detect import detect_project
from ..harness_paths import existing_harness_path, harness_path
from ..indexer import build_index_report
from ..planner import DiffPlanReport, build_diff_plan
from ..readiness import inspect_readiness, readiness_to_dict
from ..reports import report_path, relative_to_target
from ..update import build_drift_report

SCHEMA_VERSION = "harnessforge.report.v1"
FIRST_AGENT_TASK = harness_path("first_agent_task")
AUTHORITATIVE_FACTS = harness_path("authoritative_facts")
MANIFEST = harness_path("manifest")
DOCS_FANOUT_SURFACES = (
    ("local_repo_harness", "Local repo harness"),
    ("generated_harness", "Generated harness files"),
    ("cli_runtime", "CLI/runtime behavior"),
    ("existing_project_files", "Existing project files"),
    ("github_action_or_ci", "GitHub Action or CI workflows"),
    ("optional_workflow_scaffolds", "Optional workflow scaffolds"),
    ("tests_and_fixtures", "Tests and fixture corpus"),
    ("release_package", "Release/package surface"),
    ("research_sources", "Research and source records"),
    ("security_privacy", "Security and privacy"),
    ("platform_contracts", "Platform contracts"),
    ("docs_ux", "Docs and UX"),
)
DOCS_FACT_SCAN_LIMIT = 32
MIN_DUPLICATE_FACT_CHARS = 120


def build_report(
    target: Path,
    *,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
    max_files: int = 4000,
    require_verify_evidence: bool = False,
    require_docs_fanout_budget: bool = False,
    since: str | None = None,
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
    policy_presets = build_policy_preset_report(profile, index)
    sbom_adapter = build_sbom_adapter_plan(profile, index)
    readiness_payload = readiness_to_dict(readiness)
    audit_payload = audit_to_dict(audit)
    manifest = _read_manifest(profile.root)
    first_agent_lifecycle = analyze_first_agent_lifecycle(profile.root, profile.files)
    first_agent = _first_agent_task_status(first_agent_lifecycle)
    diff_plan = (
        build_diff_plan(profile, since=since, explicit_commands=explicit_commands)
        if since
        else None
    )
    docs_fanout = _docs_fanout_summary(
        profile.root,
        manifest,
        diff_plan,
        require_budget=require_docs_fanout_budget,
    )
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
        "instructionQuality": readiness_payload["instructionQuality"],
        "firstAgentTask": first_agent,
        "platform": _platform_summary(manifest),
        "policyPresets": policy_presets,
        "sbomAdapter": sbom_adapter,
        "releaseControls": _release_controls_summary(profile.root),
        "docsFanout": docs_fanout,
    }
    payload["maturity"] = build_maturity_report(payload)
    payload["nextActions"] = _next_actions(
        readiness_payload,
        audit_payload,
        drift,
        effectiveness,
        first_agent,
        docs_fanout,
        payload["maturity"],
        policy_presets,
        sbom_adapter,
    )
    return payload


def format_report(payload: dict[str, Any]) -> str:
    instruction_average = payload["instructionQuality"]["summary"]["averageScore"]
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
        f"- SBOM files: {payload['index']['summary']['sbomCount']}",
        f"- Repo-map unknowns: {len(payload['index']['repoMap']['unknowns'])}",
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
            "## Instruction Quality",
            "",
            f"- Status: `{payload['instructionQuality']['summary']['status']}`",
            f"- Average score: `{instruction_average if instruction_average is not None else 'none'}`",
            f"- Startup files: {payload['instructionQuality']['summary']['fileCount']}",
            f"- Largest files tracked: {len(payload['instructionQuality']['largestFiles'])}",
            "",
            "## First-Agent Task",
            "",
            f"- Status: `{payload['firstAgentTask']['status']}`",
            f"- Lifecycle: `{payload['firstAgentTask']['lifecycle']['status']}`",
            f"- Path: `{payload['firstAgentTask']['path'] or 'none'}`",
            f"- Evidence: `{payload['firstAgentTask']['lifecycle']['evidencePath'] or 'none'}`",
            "",
            "## Platform",
            "",
            f"- Contract: `{payload['platform']['contract']}`",
            "",
            "## Policy Presets",
            "",
            f"- Status: `{payload['policyPresets']['status']}`",
            f"- Available: {len(payload['policyPresets']['availablePresets'])}",
            f"- Applied: {len(payload['policyPresets']['appliedPresets'])}",
            f"- Recommended: {len(payload['policyPresets']['recommendedPresets'])}",
            "",
            "## SBOM Adapter",
            "",
            f"- Status: `{payload['sbomAdapter']['status']}`",
            f"- Default behavior: `{payload['sbomAdapter']['defaultBehavior']}`",
            f"- Existing SBOMs: {payload['sbomAdapter']['detectedExistingSbomCount']}",
            f"- Generation enabled: `{str(payload['sbomAdapter']['generationEnabled']).lower()}`",
            "",
            "## Maturity",
            "",
            f"- Current level: `{payload['maturity']['currentLevel']}`",
            f"- Next level: `{payload['maturity']['nextLevel'] or 'none'}`",
            "",
            "## Release Controls",
            "",
            f"- Present: `{str(payload['releaseControls']['present']).lower()}`",
            f"- Path: `{payload['releaseControls']['path']}`",
            "",
            "## Docs Fan-Out",
            "",
            f"- Contract verdict: `{payload['docsFanout']['contract']['verdict']}`",
            f"- Routing map: `{payload['docsFanout']['authoritativeMap']['status']}`",
            f"- Covered surfaces: {payload['docsFanout']['coveredSurfaceCount']}/{payload['docsFanout']['surfaceCount']}",
            f"- Routine budget: {payload['docsFanout']['fanoutBudgets']['routine']}",
            f"- Diff status: `{payload['docsFanout']['diff']['status']}`",
            f"- Touched surfaces: {payload['docsFanout']['diff']['touchedSurfaceCount']}",
            f"- Duplicate fact blocks: {payload['docsFanout']['duplicateFacts']['summary']['blocks']}",
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
        "repoMap": index["repoMap"],
        "sbom": index["sbom"],
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


def _first_agent_task_status(lifecycle: Any) -> dict[str, Any]:
    return {
        "path": lifecycle.task_path,
        "status": lifecycle.task_status,
        "reviewRequired": lifecycle.task_review_required,
        "lifecycle": first_agent_lifecycle_to_dict(lifecycle),
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


def _release_controls_summary(root: Path) -> dict[str, Any]:
    path = "docs/harness/release/release-controls.md"
    return {
        "path": path,
        "present": (root / path).is_file(),
    }


def _docs_fanout_summary(
    root: Path,
    manifest: dict[str, Any],
    diff_plan: DiffPlanReport | None,
    *,
    require_budget: bool,
) -> dict[str, Any]:
    relative_path = existing_harness_path(root, "authoritative_facts")
    path = root / relative_path
    present = path.exists()
    review_required = False
    if present:
        try:
            review_required = "REVIEW REQUIRED" in path.read_text(encoding="utf-8")
        except OSError:
            review_required = True
    manifest_paths = _manifest_paths(manifest)
    generated_or_required = any(
        path_text in manifest_paths
        for path_text in {AUTHORITATIVE_FACTS, relative_path}
    )
    covered = present and (generated_or_required or not manifest_paths)
    surfaces = [
        {
            "id": surface_id,
            "label": label,
            "covered": bool(covered),
            "ownerMap": relative_path if present else None,
        }
        for surface_id, label in DOCS_FANOUT_SURFACES
    ]
    warnings: list[str] = []
    if not present:
        warnings.append(
            "No authoritative facts map found; docs fan-out routing is unavailable."
        )
    elif review_required:
        warnings.append(
            "Authoritative facts map still contains REVIEW REQUIRED markers."
        )
    elif not generated_or_required and manifest_paths:
        warnings.append(
            "Authoritative facts map exists but is not tracked in the harness manifest."
        )
    diff_summary = _docs_fanout_diff_summary(diff_plan)
    warnings.extend(diff_summary["warnings"])
    duplicate_facts = _duplicate_fact_summary(root, manifest)
    warnings.extend(duplicate_facts["warnings"])
    contract = _docs_fanout_contract(
        required=require_budget,
        diff_summary=diff_summary,
        duplicate_facts=duplicate_facts,
    )
    return {
        "contract": contract,
        "authoritativeMap": {
            "path": relative_path,
            "present": present,
            "reviewRequired": review_required,
            "manifestTracked": generated_or_required,
            "status": (
                "pending_review"
                if present and review_required
                else "present"
                if present
                else "missing"
            ),
        },
        "surfaceCount": len(surfaces),
        "coveredSurfaceCount": sum(1 for surface in surfaces if surface["covered"]),
        "surfaces": surfaces,
        "diff": diff_summary,
        "duplicateFacts": duplicate_facts,
        "fanoutBudgets": {
            "routine": "0-1 durable doc/state updates",
            "userVisible": "1-3 durable doc/state updates",
            "exception": "more than 3 only for boundary, platform, security, release, README, or generated-contract changes",
        },
        "warnings": warnings,
    }


def _docs_fanout_contract(
    *,
    required: bool,
    diff_summary: dict[str, Any],
    duplicate_facts: dict[str, Any],
) -> dict[str, Any]:
    blocked: list[str] = []
    if required:
        if diff_summary["status"] == "not_requested":
            blocked.append(
                "Docs fan-out budget enforcement requires --since or report-since."
            )
        elif diff_summary["status"] == "unavailable":
            blocked.extend(diff_summary["blockedReasons"])
        elif diff_summary["classification"] == "exception_review":
            blocked.append(
                "Changed files touch more than three product boundary surfaces."
            )
        if duplicate_facts["summary"]["blocks"]:
            blocked.append(
                "Duplicate durable Markdown fact blocks are present."
            )
    if blocked:
        verdict = "blocked"
    elif required:
        verdict = "passed"
    elif (
        diff_summary["warnings"]
        or diff_summary["blockedReasons"]
        or duplicate_facts["warnings"]
    ):
        verdict = "warning"
    else:
        verdict = "not_required"
    return {
        "required": required,
        "verdict": verdict,
        "blockedReasons": blocked,
    }


def _docs_fanout_diff_summary(diff_plan: DiffPlanReport | None) -> dict[str, Any]:
    if diff_plan is None:
        return {
            "status": "not_requested",
            "base": None,
            "changedFileCount": 0,
            "changedFiles": [],
            "touchedSurfaceCount": 0,
            "touchedSurfaceIds": [],
            "files": [],
            "classification": "unknown",
            "recommendedBudget": "not estimated",
            "blockedReasons": [],
            "warnings": [],
        }
    if diff_plan.blocked_reasons:
        return {
            "status": "unavailable",
            "base": diff_plan.base,
            "changedFileCount": 0,
            "changedFiles": [],
            "touchedSurfaceCount": 0,
            "touchedSurfaceIds": [],
            "files": [],
            "classification": "unknown",
            "recommendedBudget": "not estimated",
            "blockedReasons": list(diff_plan.blocked_reasons),
            "warnings": list(diff_plan.warnings),
        }
    file_items = [
        {
            "path": path,
            "surfaceIds": sorted(_surface_ids_for_file(path)),
        }
        for path in diff_plan.changed_files
    ]
    touched = sorted(
        {
            surface_id
            for item in file_items
            for surface_id in item["surfaceIds"]
        }
    )
    classification, budget = _fanout_classification(len(touched))
    warnings = list(diff_plan.warnings)
    if len(touched) > 3:
        warnings.append(
            "Docs fan-out warning: changed files touch more than three product "
            "boundary surfaces; review authoritative owners before updating docs."
        )
    return {
        "status": "available" if diff_plan.changed_files else "no_changes",
        "base": diff_plan.base,
        "changedFileCount": len(diff_plan.changed_files),
        "changedFiles": list(diff_plan.changed_files),
        "touchedSurfaceCount": len(touched),
        "touchedSurfaceIds": touched,
        "files": file_items,
        "classification": classification,
        "recommendedBudget": budget,
        "blockedReasons": [],
        "warnings": warnings,
    }


def _surface_ids_for_file(path: str) -> set[str]:
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    name = lower.rsplit("/", 1)[-1]
    surfaces: set[str] = set()
    if lower.startswith("docs/harness/") or lower.startswith(".agents/skills/harness/") or name in {
        "agents.md",
        "claude.md",
        "gemini.md",
    }:
        surfaces.add("local_repo_harness")
    if lower.startswith("src/harnessforge/templates/") or lower in {
        "src/harnessforge/generate.py",
        "src/harnessforge/public_repo_corpus.py",
    }:
        surfaces.add("generated_harness")
    if lower.startswith("src/harnessforge/") or lower == "pyproject.toml":
        surfaces.add("cli_runtime")
    if lower.startswith(".github/workflows/") or lower in {
        "action.yml",
        "docs/action.md",
        "src/harnessforge/github_action.py",
    }:
        surfaces.add("github_action_or_ci")
    if lower.startswith(".github/workflows/") or (
        lower.startswith("src/harnessforge/templates/") and "workflow" in lower
    ):
        surfaces.add("optional_workflow_scaffolds")
    if lower.startswith("tests/") or lower.startswith("fixtures/"):
        surfaces.add("tests_and_fixtures")
    if lower in {
        "readme.md",
        "pyproject.toml",
        "docs/installation.md",
        "docs/capabilities.md",
    } or "release" in lower:
        surfaces.add("release_package")
    if (
        lower.startswith("docs/harness/research")
        or lower in {
            "docs/harness/research/sources.md",
            "scripts/refresh_research.py",
        }
        or "source-record" in lower
    ):
        surfaces.add("research_sources")
    if "security" in lower or "privacy" in lower:
        surfaces.add("security_privacy")
    if lower in {
        "init.sh",
        "init.ps1",
        "docs/harness/manifest.json",
    } or "platform" in lower:
        surfaces.add("platform_contracts")
    if lower.startswith("docs/") or lower == "readme.md":
        surfaces.add("docs_ux")
    if not surfaces:
        surfaces.add("existing_project_files")
    return surfaces


def _fanout_classification(surface_count: int) -> tuple[str, str]:
    if surface_count == 0:
        return "no_changes", "0 durable doc/state updates"
    if surface_count <= 1:
        return "routine", "0-1 durable doc/state updates"
    if surface_count <= 3:
        return "user_visible", "1-3 durable doc/state updates"
    return (
        "exception_review",
        "more than 3 only for boundary, platform, security, release, README, or generated-contract changes",
    )


def _duplicate_fact_summary(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    markdown_paths = _markdown_fact_paths(manifest)
    texts: dict[str, str] = {}
    for path_text in markdown_paths[:DOCS_FACT_SCAN_LIMIT]:
        path = root / path_text
        if not path.is_file():
            continue
        try:
            texts[path_text] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    blocks: dict[str, set[str]] = {}
    previews: dict[str, str] = {}
    for path_text, text in texts.items():
        for block, preview in _normalized_fact_blocks(text):
            blocks.setdefault(block, set()).add(path_text)
            previews.setdefault(block, preview)
    duplicates = [
        {
            "paths": sorted(paths),
            "pathCount": len(paths),
            "preview": previews[block],
        }
        for block, paths in blocks.items()
        if len(paths) > 1
    ]
    duplicates.sort(key=lambda item: (-item["pathCount"], item["preview"]))
    warnings = (
        [
            "Duplicate fact warning: repeated durable docs text detected; route "
            "one copy through docs/harness/authoritative-facts.md when practical."
        ]
        if duplicates
        else []
    )
    return {
        "summary": {
            "scannedFiles": len(texts),
            "blocks": len(duplicates),
        },
        "items": duplicates[:10],
        "warnings": warnings,
    }


def _markdown_fact_paths(manifest: dict[str, Any]) -> list[str]:
    paths = [
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        ".github/copilot-instructions.md",
    ]
    for path in sorted(_manifest_paths(manifest)):
        if path.lower().endswith(".md"):
            paths.append(path)
    return list(dict.fromkeys(paths))


def _normalized_fact_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for paragraph in text.split("\n\n"):
        lines = [
            _normalize_fact_line(line)
            for line in paragraph.splitlines()
        ]
        lines = [line for line in lines if line]
        if not lines:
            continue
        normalized = " ".join(lines)
        if len(normalized) < MIN_DUPLICATE_FACT_CHARS:
            continue
        preview = " ".join(line.strip() for line in paragraph.splitlines())[:160]
        blocks.append((normalized, preview))
    return blocks


def _normalize_fact_line(line: str) -> str:
    stripped = " ".join(line.strip().split())
    if not stripped:
        return ""
    if stripped.startswith("#") or stripped in {"| --- | --- |", "| --- | --- | --- |"}:
        return ""
    if "REVIEW REQUIRED" in stripped:
        return ""
    return stripped.lower()


def _manifest_paths(manifest: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for key in ("requiredFiles", "reviewRequired"):
        value = manifest.get(key)
        if isinstance(value, list):
            paths.update(item for item in value if isinstance(item, str))
    snippets = manifest.get("requiredHarnessSnippets")
    if isinstance(snippets, dict):
        paths.update(key for key in snippets if isinstance(key, str))
    generated_files = manifest.get("generatedFiles")
    if isinstance(generated_files, dict):
        paths.update(key for key in generated_files if isinstance(key, str))
    return paths


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
    docs_fanout: dict[str, Any],
    maturity: dict[str, Any],
    policy_presets: dict[str, Any],
    sbom_adapter: dict[str, Any],
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
    actions.extend(first_agent["lifecycle"]["nextActions"])
    actions.extend(policy_presets["nextActions"])
    actions.extend(sbom_adapter["nextActions"])
    if docs_fanout["authoritativeMap"]["status"] == "missing":
        actions.append(
            "Add docs/harness/authoritative-facts.md to reduce harness docs fan-out."
        )
    elif docs_fanout["authoritativeMap"]["reviewRequired"]:
        actions.append(
            "Review "
            f"{docs_fanout['authoritativeMap']['path']} and remove REVIEW "
            "REQUIRED markers when accepted."
        )
    if docs_fanout["contract"]["blockedReasons"]:
        actions.extend(docs_fanout["contract"]["blockedReasons"])
    if maturity["nextLevel"]:
        blocked = ", ".join(
            requirement["id"] for requirement in maturity["blockedRequirements"]
        )
        actions.append(
            f"Advance harness maturity from {maturity['currentLevel']} to "
            f"{maturity['nextLevel']} by resolving: {blocked}."
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
