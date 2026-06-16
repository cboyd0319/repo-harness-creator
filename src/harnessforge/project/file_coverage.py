from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from ..core.models import ProjectProfile

SCHEMA_VERSION = "harnessforge.fileCoverage.v1"
GIT_TIMEOUT_SECONDS = 10
EXAMPLE_LIMIT = 5
MANIFEST_NAMES = {
    ".bazelversion",
    ".buckconfig",
    ".nvmrc",
    ".python-version",
    "Cargo.toml",
    "Containerfile",
    "Dockerfile",
    "Gemfile",
    "Justfile",
    "Makefile",
    "MODULE.bazel",
    "Package.swift",
    "Pipfile",
    "WORKSPACE",
    "WORKSPACE.bazel",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "go.mod",
    "go.work",
    "justfile",
    "package.json",
    "pants.toml",
    "pnpm-workspace.yaml",
    "pom.xml",
    "pyproject.toml",
    "rush.json",
    "settings.gradle",
    "settings.gradle.kts",
    "turbo.json",
    "turbo.jsonc",
}
SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}


def build_file_coverage_report(profile: ProjectProfile) -> dict[str, Any]:
    tracked_files = _git_tracked_files(profile.root)
    if tracked_files is None:
        inventory_source = "filesystem_scan"
        inventory_files = list(profile.files)
        total_known = not profile.file_scan_truncated
    else:
        inventory_source = "git_tracked"
        inventory_files = tracked_files
        total_known = True
    scanned_set = set(profile.files)
    categories = _category_reports(
        inventory_files=inventory_files,
        scanned_set=scanned_set,
        total_known=total_known,
        scan_truncated=profile.file_scan_truncated,
    )
    total_file_count = len(inventory_files) if total_known else None
    budget_limited = any(category["budgetLimited"] for category in categories)
    warnings = []
    if inventory_source == "filesystem_scan" and profile.file_scan_truncated:
        warnings.append(
            "File coverage is based on the bounded filesystem scan; use a git "
            "checkout for exact tracked-file coverage."
        )
    if budget_limited:
        warnings.append(
            "One or more file categories were budget-limited by the file scan."
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "inventorySource": inventory_source,
        "fileScanLimit": profile.file_scan_limit,
        "scannedFileCount": len(profile.files),
        "totalFileCount": total_file_count,
        "coverageComplete": not budget_limited,
        "categories": categories,
        "warnings": warnings,
    }


def _git_tracked_files(root: Path) -> list[str] | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    files = [
        line
        for line in result.stdout.splitlines()
        if _is_safe_relative_path(line)
    ]
    return sorted(dict.fromkeys(files))


def _is_safe_relative_path(path: str) -> bool:
    pure = PurePosixPath(path)
    return bool(path) and not pure.is_absolute() and ".." not in pure.parts


def _category_reports(
    *,
    inventory_files: list[str],
    scanned_set: set[str],
    total_known: bool,
    scan_truncated: bool,
) -> list[dict[str, Any]]:
    by_category: dict[str, list[str]] = {}
    scanned_by_category: dict[str, list[str]] = {}
    for path in inventory_files:
        category = _category_for_path(path)
        by_category.setdefault(category, []).append(path)
        if path in scanned_set:
            scanned_by_category.setdefault(category, []).append(path)
    reports = []
    for category_id, label in _category_order():
        total_paths = by_category.get(category_id, [])
        scanned_paths = scanned_by_category.get(category_id, [])
        if not total_paths and not scanned_paths:
            continue
        total = len(total_paths) if total_known else None
        budget_limited = (
            len(scanned_paths) < len(total_paths)
            if total_known
            else scan_truncated
        )
        omitted = [path for path in total_paths if path not in scanned_set]
        reports.append(
            {
                "id": category_id,
                "label": label,
                "scannedFiles": len(scanned_paths),
                "totalFiles": total,
                "fullyCovered": not budget_limited,
                "budgetLimited": budget_limited,
                "examples": scanned_paths[:EXAMPLE_LIMIT],
                "omittedExamples": omitted[:EXAMPLE_LIMIT],
            }
        )
    return reports


def _category_order() -> tuple[tuple[str, str], ...]:
    return (
        ("root_instructions", "Root agent instructions"),
        ("runtime_manifests", "Runtime and package manifests"),
        ("workflows", "Workflow and action files"),
        ("source_of_truth", "Source-of-truth docs"),
        ("sbom", "SBOM files"),
        ("harness", "Harness files"),
        ("source", "Source files"),
        ("tests", "Test files"),
        ("remaining", "Remaining tracked files"),
    )


def _category_for_path(path: str) -> str:
    pure = PurePosixPath(path)
    name = pure.name
    lower = path.lower()
    suffix = pure.suffix.lower()
    if path in {
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        ".github/copilot-instructions.md",
    }:
        return "root_instructions"
    if path.startswith(".github/workflows/") or path.startswith(".github/actions/"):
        return "workflows"
    if path.startswith("docs/harness/") or path.startswith(".agents/skills/harness/"):
        return "harness"
    if name in MANIFEST_NAMES or name.endswith(
        (".csproj", ".fsproj", ".sln", ".slnx", ".vbproj")
    ):
        return "runtime_manifests"
    if _is_source_of_truth(path, name, lower):
        return "source_of_truth"
    if "sbom" in lower and suffix in {".json", ".spdx", ".xml"}:
        return "sbom"
    if _is_test_path(path, name, lower):
        return "tests"
    if suffix in SOURCE_SUFFIXES:
        return "source"
    return "remaining"


def _is_source_of_truth(path: str, name: str, lower: str) -> bool:
    if name in {"README.md", "CONTRIBUTING.md", "ARCHITECTURE.md", "SECURITY.md"}:
        return True
    if lower.startswith(("docs/architecture", "docs/spec", "docs/design")):
        return True
    return lower.startswith("specs/") and lower.endswith(".md")


def _is_test_path(path: str, name: str, lower: str) -> bool:
    if lower.startswith(("test/", "tests/", "spec/", "specs/")):
        return True
    return name.startswith("test_") or name.endswith(
        ("_test.py", ".test.ts", ".spec.ts")
    )
