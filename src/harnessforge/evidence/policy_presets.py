from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from ..core.models import ProjectProfile
from ..core.paths import path_from_relative_text
from ..generation.blueprints import BLUEPRINT_ROOT, Blueprint, list_blueprints

SCHEMA_VERSION = "harnessforge.policyPresets.v1"


def build_policy_preset_report(
    profile: ProjectProfile,
    index_report: dict[str, Any],
) -> dict[str, Any]:
    available = list_blueprints()
    applied = _applied_presets(profile.root)
    recommendations = _recommended_presets(profile, index_report, available)
    applied_ids = {item["id"] for item in applied}
    recommended_ids = {item["id"] for item in recommendations}
    status = (
        "applied"
        if applied_ids
        else "recommendation_available"
        if recommended_ids
        else "no_recommendation"
    )
    warnings: list[str] = []
    if recommended_ids - applied_ids:
        warnings.append(
            "Policy preset recommendations are advisory until the project applies "
            "and reviews a preset."
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "mode": "read_only",
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "availablePresets": [_preset_summary(item) for item in available],
        "appliedPresets": applied,
        "recommendedPresets": recommendations,
        "warnings": warnings,
        "nextActions": _next_actions(recommendations, applied_ids),
    }


def _preset_summary(blueprint: Blueprint) -> dict[str, Any]:
    return {
        "id": blueprint.id,
        "title": blueprint.title,
        "domains": list(blueprint.domains),
    }


def _applied_presets(root: Path) -> list[dict[str, Any]]:
    manifest = root / BLUEPRINT_ROOT / "manifest.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    applied = payload.get("appliedBlueprints", {})
    if not isinstance(applied, dict):
        return []
    result: list[dict[str, Any]] = []
    for preset_id, metadata in sorted(applied.items()):
        if not isinstance(metadata, dict):
            continue
        result.append(
            {
                "id": preset_id,
                "title": str(metadata.get("title", preset_id)),
                "reviewRequired": bool(metadata.get("reviewRequired", True)),
                "ownership": str(
                    metadata.get(
                        "ownership",
                        "generated-blueprint-project-reviewed",
                    )
                ),
            }
        )
    return result


def _recommended_presets(
    profile: ProjectProfile,
    index_report: dict[str, Any],
    available: tuple[Blueprint, ...],
) -> list[dict[str, Any]]:
    available_by_id = {item.id: item for item in available}
    scores: dict[str, list[str]] = {}

    def add(preset_id: str, reason: str) -> None:
        if preset_id in available_by_id:
            scores.setdefault(preset_id, []).append(reason)

    files = set(profile.files)
    lower_files = {file.lower(): file for file in files}
    manifest_kinds = {
        str(item.get("kind", ""))
        for item in index_report.get("repoMap", {}).get("manifestKinds", [])
        if isinstance(item, dict)
    }
    languages = set(profile.languages)
    package_managers = set(profile.package_managers)
    file_parts = {
        part.lower()
        for file in files
        for part in PurePosixPath(file).parts
    }

    if "LICENSE" in files or "license" in lower_files:
        add("open-source-library", "License file detected.")
    if {"pyproject.toml", "package.json", "Cargo.toml", "go.mod"} & files:
        add("open-source-library", "Package manifest detected.")
    if "README.md" in files or "readme.md" in lower_files:
        add("open-source-library", "README detected.")
    if profile.stack in {"python", "go", "rust"} and (
        "Makefile" in files or "Justfile" in files or "scripts" in file_parts
    ):
        add("cli-dev-tool", "Developer-tool stack and command entrypoints detected.")
    if profile.components and len(profile.components) > 1:
        add("monorepo", "Multiple component boundaries detected.")
    if profile.workspace_markers:
        add("monorepo", "Workspace markers detected.")
    if any(file.startswith(("specs/", ".specify/", "aspec/")) for file in files):
        add("spec-driven", "Structured specification files detected.")
    if {"terraform", "hcl"} & languages or {"terraform"} & manifest_kinds:
        add("infrastructure-iac", "Terraform or IaC markers detected.")
    if any(file.startswith((".github/workflows/", ".gitea/workflows/")) for file in files):
        add("workflow-automation", "Workflow automation files detected.")
    if {"Dockerfile", "Containerfile", "compose.yaml", "docker-compose.yml"} & files:
        add("internal-service", "Container or service runtime files detected.")
    if {"javascript", "typescript"} & languages and (
        "package.json" in files or package_managers
    ):
        add("web-service", "JavaScript or TypeScript app markers detected.")
    if {"notebooks", "data", "datasets", "models"} & file_parts:
        add("data-ml", "Data, notebook, or model paths detected.")
    if any("security" in file.lower() for file in files):
        add("security-sensitive", "Security documentation or code paths detected.")
    if any(file.endswith((".tf", ".tfvars")) for file in files):
        add("security-sensitive", "Infrastructure files may affect trust boundaries.")
    if {"Package.swift"} & files or "swift" in languages:
        add("mobile-desktop", "Swift package or app markers detected.")
    if {"docs", "documentation"} & file_parts and not (
        languages & {"python", "go", "rust", "java", "typescript", "javascript"}
    ):
        add("docs-research", "Docs-heavy repository shape detected.")
    if {"legacy", "migration", "migrations"} & file_parts:
        add("legacy-migration", "Legacy or migration paths detected.")
    if {"training", "education", "examples", "fixtures"} & file_parts:
        add("education-training", "Education, examples, or fixture paths detected.")
    if any(file.startswith(".agents/") for file in files):
        add("agentic-app", "Agent skill or harness surfaces detected.")

    recommendations = []
    for preset_id, reasons in sorted(
        scores.items(),
        key=lambda item: (-len(item[1]), item[0]),
    ):
        blueprint = available_by_id[preset_id]
        confidence = "high" if len(reasons) >= 2 else "medium"
        recommendations.append(
            {
                "id": preset_id,
                "title": blueprint.title,
                "confidence": confidence,
                "reasons": reasons,
                "reviewRequired": True,
            }
        )
    return recommendations[:6]


def _next_actions(
    recommendations: list[dict[str, Any]],
    applied_ids: set[str],
) -> list[str]:
    missing = [item for item in recommendations if item["id"] not in applied_ids]
    if not missing:
        return []
    first = missing[0]["id"]
    return [
        f"Review policy preset `{first}` with `harnessforge blueprint show {first}`.",
        f"Apply only after review with `harnessforge blueprint apply {first} --target <repo> --dry-run`.",
    ]
