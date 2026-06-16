from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..core.paths import is_absolute_path_text, is_inside_root, path_from_relative_text


@dataclass(frozen=True)
class SpecSystemReport:
    source_labels: tuple[str, ...]
    routing_targets: tuple[str, ...]
    workspace_markers: tuple[str, ...]
    routing_markers: tuple[str, ...]
    quality_warnings: tuple[str, ...]


def analyze_spec_system(
    root: Path, files: tuple[str, ...] | None = None
) -> SpecSystemReport:
    root = root.resolve()
    file_set = set(files) if files is not None else set(_list_files(root))
    source_labels: list[str] = []
    routing_targets: list[str] = []
    workspace_markers: list[str] = []
    routing_markers: list[str] = []
    quality_warnings: list[str] = []

    has_specify = any(file.startswith(".specify/") for file in file_set)
    if has_specify:
        source_labels.append("Spec Kit project (.specify)")
        routing_targets.append(".specify")
        workspace_markers.append("Spec Kit SDD")
        routing_markers.append("Spec Kit SDD")

    if ".specify/memory/constitution.md" in file_set:
        source_labels.append("Spec Kit constitution: .specify/memory/constitution.md")
        routing_targets.append(".specify/memory/constitution.md")
        routing_markers.append("Spec Kit constitution")

    active_feature = _active_feature_dir(root, file_set, quality_warnings)
    if active_feature:
        source_labels.append(f"active feature specs: {active_feature}")
        routing_targets.append(active_feature)
        workspace_markers.append("Spec Kit active feature")
        routing_markers.append("Spec Kit active feature")

    feature_dirs = _feature_dirs(file_set)
    if feature_dirs:
        source_labels.append("feature specs")
        routing_targets.append("specs/")
        routing_markers.append("feature specs")
        if not has_specify:
            workspace_markers.append("feature specs")

    if any(file.startswith("aspec/") for file in file_set):
        source_labels.append("aspec")
        routing_targets.append("aspec/")
        workspace_markers.append("aspec")
        routing_markers.append("aspec")

    for path in _work_item_templates(file_set):
        source_labels.append(f"work-item template: {path}")
        routing_targets.append(path)
    if _work_item_templates(file_set):
        routing_markers.append("work-item templates")

    workflow_roots = _workflow_roots(file_set)
    if workflow_roots:
        source_labels.append("repo workflow definitions")
        routing_targets.extend(workflow_roots)
        routing_markers.append("repo workflow definitions")
        quality_warnings.append(
            "repo workflow definitions detected; review setup, teardown, "
            "remediation, push, and credential surfaces before agent use."
        )

    inspected_dirs = _dedupe(([active_feature] if active_feature else []) + feature_dirs)
    for feature_dir in inspected_dirs[:20]:
        _append_feature_quality_warnings(root, file_set, feature_dir, quality_warnings)

    return SpecSystemReport(
        source_labels=tuple(_dedupe(source_labels)),
        routing_targets=tuple(_dedupe(routing_targets)),
        workspace_markers=tuple(_dedupe(workspace_markers)),
        routing_markers=tuple(_dedupe(routing_markers)),
        quality_warnings=tuple(_dedupe(quality_warnings)),
    )


def has_spec_system(file_set: set[str]) -> bool:
    return any(file.startswith(".specify/") for file in file_set) or bool(
        _feature_dirs(file_set)
    )


def instruction_routes_to_specs(instruction: str, report: SpecSystemReport) -> bool:
    if not report.source_labels:
        return True
    lower = instruction.lower()
    targets = list(report.routing_targets)
    targets.extend(
        (
            ".specify",
            "specs/",
            "spec.md",
            "plan.md",
            "tasks.md",
            "source-of-truth",
            "source of truth",
            "constitution",
            "work-item",
        )
    )
    return any(target.lower() in lower for target in targets)


def _active_feature_dir(
    root: Path, file_set: set[str], quality_warnings: list[str]
) -> str:
    if ".specify/feature.json" not in file_set:
        return ""
    path = root / ".specify" / "feature.json"
    text = _read_text(path, root)
    if text is None:
        quality_warnings.append(".specify/feature.json is not readable.")
        return ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        quality_warnings.append(".specify/feature.json is not valid JSON.")
        return ""
    if not isinstance(payload, dict):
        quality_warnings.append(".specify/feature.json must be a JSON object.")
        return ""
    feature_directory = payload.get("feature_directory")
    if not isinstance(feature_directory, str) or not feature_directory.strip():
        quality_warnings.append(
            ".specify/feature.json is missing feature_directory."
        )
        return ""
    if is_absolute_path_text(feature_directory):
        quality_warnings.append(
            ".specify/feature.json feature_directory must be repo-relative."
        )
        return ""
    candidate = root / path_from_relative_text(feature_directory)
    if not is_inside_root(candidate, root):
        quality_warnings.append(
            ".specify/feature.json feature_directory escapes the repository."
        )
        return ""
    try:
        return candidate.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        quality_warnings.append(
            ".specify/feature.json feature_directory escapes the repository."
        )
        return ""


def _feature_dirs(file_set: set[str]) -> list[str]:
    dirs: set[str] = set()
    for file in file_set:
        path = Path(file)
        if len(path.parts) >= 3 and path.parts[0] == "specs" and path.name in {
            "spec.md",
            "plan.md",
            "tasks.md",
        }:
            dirs.add("/".join(path.parts[:2]))
    return sorted(dirs)


def _work_item_templates(file_set: set[str]) -> list[str]:
    templates: list[str] = []
    for file in sorted(file_set):
        path = Path(file)
        if path.name != "0000-template.md":
            continue
        if any(part in {"work-items", "work_items", "workitems"} for part in path.parts):
            templates.append(file)
    return templates


def _workflow_roots(file_set: set[str]) -> list[str]:
    roots: set[str] = set()
    for file in file_set:
        path = Path(file)
        if path.suffix.lower() not in {".toml", ".yml", ".yaml"}:
            continue
        if path.parts[:2] == ("aspec", "workflows"):
            roots.add("aspec/workflows/")
        elif path.parts and path.parts[0] == "workflows":
            roots.add("workflows/")
    return sorted(roots)


def _append_feature_quality_warnings(
    root: Path,
    file_set: set[str],
    feature_dir: str,
    quality_warnings: list[str],
) -> None:
    spec_path = f"{feature_dir}/spec.md"
    plan_path = f"{feature_dir}/plan.md"
    tasks_path = f"{feature_dir}/tasks.md"
    if spec_path not in file_set:
        quality_warnings.append(f"{feature_dir} is missing spec.md.")
    else:
        spec_text = _read_text(root / path_from_relative_text(spec_path), root) or ""
        if "[NEEDS CLARIFICATION" in spec_text:
            quality_warnings.append(f"{spec_path} contains NEEDS CLARIFICATION markers.")
        if not re.search(r"\b(?:FR|SC)-\d{3,}\b", spec_text):
            quality_warnings.append(
                f"{spec_path} has weak spec-to-task traceability; no FR-/SC-style IDs found."
            )
    if plan_path not in file_set:
        quality_warnings.append(f"active feature {feature_dir} is missing plan.md.")
    if tasks_path not in file_set:
        quality_warnings.append(f"active feature {feature_dir} is missing tasks.md.")
    else:
        tasks_text = _read_text(root / path_from_relative_text(tasks_path), root) or ""
        if _tasks_have_missing_paths(tasks_text):
            quality_warnings.append(
                f"{tasks_path} has tasks without explicit file paths."
            )
    for checklist in sorted(
        file
        for file in file_set
        if file.startswith(f"{feature_dir}/checklists/")
        and Path(file).suffix.lower() in {".md", ".markdown"}
    ):
        text = _read_text(root / path_from_relative_text(checklist), root) or ""
        if re.search(r"(?m)^\s*-\s+\[\s\]", text):
            quality_warnings.append(
                f"{checklist} has incomplete requirement checklist items."
            )


def _tasks_have_missing_paths(text: str) -> bool:
    for line in text.splitlines():
        if not re.match(r"^\s*-\s+\[[ xX]\]\s+T\d{3}", line):
            continue
        if not re.search(r"\b[\w./-]+\.[A-Za-z0-9]{1,8}\b", line):
            return True
    return False


def _list_files(root: Path, *, max_files: int = 4000) -> list[str]:
    results: list[str] = []

    def walk(current: Path, relative: str) -> None:
        if len(results) >= max_files:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            return
        for entry in entries:
            if len(results) >= max_files:
                return
            if entry.is_symlink():
                continue
            rel = f"{relative}/{entry.name}" if relative else entry.name
            if entry.is_file():
                results.append(rel)
            elif entry.is_dir() and entry.name not in {".git", "node_modules"}:
                walk(entry, rel)

    walk(root, "")
    return results


def _read_text(path: Path, root: Path) -> str | None:
    if not is_inside_root(path, root) or not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
