from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from ..models import ProjectProfile

SCHEMA_VERSION = "harnessforge.sbomAdapter.v1"


def build_sbom_adapter_plan(
    profile: ProjectProfile,
    index_report: dict[str, Any],
) -> dict[str, Any]:
    existing = list(index_report.get("sbom", []))
    project_tools = _project_owned_tools(profile.files)
    adapters = [
        {
            "id": "existing-spdx-cyclonedx",
            "status": "available" if existing else "not_detected",
            "mode": "read_existing",
            "writesPerformed": False,
            "requiresExplicitOptIn": False,
            "evidence": [item.get("path", "") for item in existing[:10]],
        },
        {
            "id": "project-owned-sbom-command",
            "status": "available" if project_tools else "not_detected",
            "mode": "import_project_owned_output",
            "writesPerformed": False,
            "requiresExplicitOptIn": True,
            "evidence": project_tools,
        },
        {
            "id": "external-sbom-generator",
            "status": "design_only",
            "mode": "explicit_generation",
            "writesPerformed": False,
            "requiresExplicitOptIn": True,
            "evidence": [],
        },
    ]
    status = "existing_sbom_detected" if existing else "explicit_adapter_available"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "defaultBehavior": "detect_existing_only",
        "generationEnabled": False,
        "explicitOptInRequired": True,
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": False,
        },
        "detectedExistingSbomCount": len(existing),
        "detectedExistingSboms": existing[:10],
        "adapters": adapters,
        "requirements": [
            "Require an explicit command or flag before generating an SBOM.",
            "Prefer installed or project-owned tooling and record tool version.",
            "Write only target-relative reports and avoid vulnerability or compliance claims without policy evidence.",
        ],
        "nextActions": _next_actions(existing, project_tools),
    }


def _project_owned_tools(files: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for file in files:
        pure = PurePosixPath(file)
        lower_name = pure.name.lower()
        lower_path = file.lower()
        if "sbom" not in lower_path and "cyclonedx" not in lower_path and "spdx" not in lower_path:
            continue
        if pure.parts and pure.parts[0] in {"scripts", "tools", ".github"}:
            result.append(file)
        elif lower_name in {
            "makefile",
            "justfile",
            "package.json",
            "pyproject.toml",
            "cargo.toml",
        }:
            result.append(file)
    return result[:10]


def _next_actions(existing: list[dict[str, Any]], project_tools: list[str]) -> list[str]:
    if existing:
        return ["Review detected SBOM files before using them as release evidence."]
    if project_tools:
        return ["Review project-owned SBOM tooling before enabling adapter import."]
    return [
        "Keep default behavior to existing-SBOM detection only.",
        "Add an explicit SBOM adapter only if it improves generated output or release evidence.",
    ]
