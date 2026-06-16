from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.paths import is_inside_root, path_from_relative_text


WORKFLOW_SUFFIXES = {".toml", ".yaml", ".yml"}
WORK_ITEM_DIR_NAMES = {"work-items", "work_items", "workitems"}


@dataclass(frozen=True)
class WorkflowItem:
    path: str
    kind: str
    format: str
    surfaces: tuple[str, ...]
    review_required: tuple[str, ...]


@dataclass(frozen=True)
class WorkItem:
    path: str
    kind: str
    signals: tuple[str, ...]


@dataclass(frozen=True)
class WorkflowInventoryReport:
    workflows: tuple[WorkflowItem, ...]
    work_items: tuple[WorkItem, ...]
    warnings: tuple[str, ...]
    review_required: tuple[str, ...]


def analyze_workflow_inventory(
    root: Path, files: tuple[str, ...]
) -> WorkflowInventoryReport:
    root = root.resolve()
    workflows = tuple(
        _workflow_item(root, file)
        for file in sorted(files)
        if _is_workflow_file(file)
    )
    workflows = tuple(item for item in workflows if item is not None)
    work_items = tuple(_work_item(file) for file in sorted(files) if _is_work_item(file))

    warnings: list[str] = []
    review_required: list[str] = []
    if workflows:
        warnings.append(
            f"workflow inventory detected {len(workflows)} repo workflow "
            "definition(s); review before agent use."
        )
    if work_items:
        warnings.append(
            f"work-item inventory detected {len(work_items)} work-item "
            "artifact(s); confirm ownership and status."
        )
    for workflow in workflows:
        review_required.extend(workflow.review_required)

    return WorkflowInventoryReport(
        workflows=workflows,
        work_items=work_items,
        warnings=tuple(_dedupe(warnings)),
        review_required=tuple(_dedupe(review_required)),
    )


def workflow_to_dict(item: WorkflowItem) -> dict[str, Any]:
    return {
        "path": item.path,
        "kind": item.kind,
        "format": item.format,
        "surfaces": list(item.surfaces),
        "reviewRequired": list(item.review_required),
    }


def work_item_to_dict(item: WorkItem) -> dict[str, Any]:
    return {
        "path": item.path,
        "kind": item.kind,
        "signals": list(item.signals),
    }


def _workflow_item(root: Path, file: str) -> WorkflowItem | None:
    path = Path(file)
    format_name = "toml" if path.suffix.lower() == ".toml" else "yaml"
    text = _read_text(root, file)
    if text is None:
        return None
    surfaces = _workflow_surfaces(text, format_name)
    review_required = _workflow_review_items(file, surfaces)
    return WorkflowItem(
        path=file,
        kind=_workflow_kind(path),
        format=format_name,
        surfaces=tuple(surfaces),
        review_required=tuple(review_required),
    )


def _workflow_surfaces(text: str, format_name: str) -> list[str]:
    lower = text.lower()
    keys = set(_toml_keys(text)) if format_name == "toml" else set()
    surfaces: list[str] = []
    checks = (
        ("setup", (r"\bsetup\b", r"\binstall\b"), {"setup"}),
        ("teardown", (r"\bteardown\b", r"\bcleanup\b"), {"teardown", "cleanup"}),
        (
            "remediation",
            (r"\bremediat", r"\brepair\b", r"\bfix\b", r"\bself[-_ ]heal\b"),
            {"remediation", "repair", "fix", "self_heal"},
        ),
        ("push", (r"\bpush\b",), {"push"}),
        (
            "pull-request",
            (r"\bpull[_ -]request\b", r"\bpull_request_target\b", r"\bpr\b"),
            {"pull_request", "pull_request_target", "pr"},
        ),
        (
            "ci-polling",
            (r"\bpoll\b", r"\bworkflow_run\b", r"\bcheck_run\b"),
            {"poll", "workflow_run", "check_run"},
        ),
        (
            "credentials",
            (
                r"\bcredential",
                r"\bsecret",
                r"\btoken\b",
                r"\bpassword\b",
                r"\bapi[_-]?key\b",
                r"secrets\.",
            ),
            {"credentials", "credential", "secrets", "token", "password", "api_key"},
        ),
    )
    for surface, patterns, key_names in checks:
        if keys & key_names or any(re.search(pattern, lower) for pattern in patterns):
            surfaces.append(surface)
    return surfaces


def _toml_keys(text: str) -> list[str]:
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return []
    keys: list[str] = []

    def walk(value: object, prefix: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key).lower()
                keys.append(key_text)
                if prefix:
                    keys.append(f"{prefix}.{key_text}")
                walk(child, key_text)
        elif isinstance(value, list):
            for child in value:
                walk(child, prefix)

    walk(payload)
    return keys


def _workflow_review_items(path: str, surfaces: list[str]) -> list[str]:
    items: list[str] = []
    if any(surface in surfaces for surface in ("setup", "teardown", "remediation")):
        items.append(
            f"{path} defines setup, teardown, or remediation surfaces; "
            "review side effects before agent use."
        )
    if any(surface in surfaces for surface in ("push", "pull-request")):
        items.append(
            f"{path} references push or pull-request surfaces; review branch "
            "and PR behavior."
        )
    if "credentials" in surfaces:
        items.append(
            f"{path} references credential or secret surfaces; review scopes before agent use."
        )
    return items


def _is_workflow_file(file: str) -> bool:
    path = Path(file)
    if path.suffix.lower() not in WORKFLOW_SUFFIXES:
        return False
    return (
        path.parts[:2] == ("aspec", "workflows")
        or path.parts[:2] == (".github", "workflows")
        or (bool(path.parts) and path.parts[0] == "workflows")
    )


def _workflow_kind(path: Path) -> str:
    if path.parts[:2] == ("aspec", "workflows"):
        return "aspec-workflow"
    if path.parts[:2] == (".github", "workflows"):
        return "github-action"
    return "repo-workflow"


def _is_work_item(file: str) -> bool:
    path = Path(file)
    return path.suffix.lower() in {".md", ".markdown"} and any(
        part in WORK_ITEM_DIR_NAMES for part in path.parts
    )


def _work_item(file: str) -> WorkItem:
    path = Path(file)
    kind = "template" if path.name == "0000-template.md" else "work-item"
    signals = ["template"] if kind == "template" else ["work-item"]
    return WorkItem(path=file, kind=kind, signals=tuple(signals))


def _read_text(root: Path, file: str) -> str | None:
    try:
        path = root / path_from_relative_text(file)
    except ValueError:
        return None
    if not is_inside_root(path, root) or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
