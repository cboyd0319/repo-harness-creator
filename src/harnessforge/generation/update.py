from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from ..assessment.audit import audit_target
from ..core.models import AuditResult, DriftResult, ProjectProfile, WriteResult
from ..core.paths import is_absolute_path_text, is_inside_root, path_from_relative_text
from .generate import _template_sha256, create_harness


def plan_or_apply_update(
    target: Path,
    *,
    apply: bool,
    force: bool = False,
    enhance_existing: bool = False,
    agent_file: str = "AGENTS.md",
    with_ci_workflow: bool = False,
    platform_contract: str = "cross-platform",
) -> tuple[AuditResult, ProjectProfile | None, tuple[WriteResult, ...]]:
    before = audit_target(target)
    if not apply:
        return before, None, ()
    update_generated_paths = _safe_generated_update_paths(build_drift_report(target))
    profile, writes = create_harness(
        target,
        agent_file=agent_file,
        force=force,
        enhance_existing=enhance_existing,
        with_ci_workflow=with_ci_workflow,
        platform_contract=platform_contract,
        update_generated_paths=update_generated_paths if not force else frozenset(),
    )
    return before, profile, writes


def build_drift_report(target: Path) -> tuple[DriftResult, ...]:
    root = target.resolve()
    manifest_path = root / "docs/harness/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return ()
    generated_files = manifest.get("generatedFiles", {})
    if not isinstance(generated_files, dict):
        return ()

    results: list[DriftResult] = []
    for relative_path, metadata in sorted(generated_files.items()):
        if not isinstance(relative_path, str) or not isinstance(metadata, dict):
            continue
        ownership = str(metadata.get("ownership", "generated"))
        path = root / path_from_relative_text(relative_path)
        if is_absolute_path_text(relative_path) or not is_inside_root(path, root):
            results.append(
                DriftResult(
                    path=relative_path,
                    ownership=ownership,
                    file_status="unsafe-path",
                    template_status="unknown",
                    reason="manifest path points outside target",
                    recommended_action="review-manifest",
                )
            )
            continue
        file_status = _file_status(path, metadata)
        template_status = _template_status(metadata)
        reason = _drift_reason(file_status, template_status)
        action = _drift_recommended_action(ownership, file_status, template_status)
        results.append(
            DriftResult(
                path=relative_path,
                ownership=ownership,
                file_status=file_status,
                template_status=template_status,
                reason=reason,
                recommended_action=action,
            )
        )
    return tuple(results)


def _file_status(path: Path, metadata: dict[str, object]) -> str:
    recorded_hash = metadata.get("contentSha256")
    if not path.exists():
        return "missing"
    if not isinstance(recorded_hash, str):
        return "tracked"
    current_hash = sha256(path.read_bytes()).hexdigest()
    return "unchanged" if current_hash == recorded_hash else "modified"


def _template_status(metadata: dict[str, object]) -> str:
    template_name = metadata.get("template")
    recorded_hash = metadata.get("templateSha256")
    if not isinstance(template_name, str) or not isinstance(recorded_hash, str):
        return "unknown"
    try:
        current_hash = _template_sha256(template_name)
    except FileNotFoundError:
        return "missing"
    return "current" if current_hash == recorded_hash else "changed"


def _drift_reason(file_status: str, template_status: str) -> str:
    reasons = []
    if file_status in {"missing", "modified", "unsafe-path"}:
        reasons.append(f"file {file_status}")
    if template_status in {"changed", "missing"}:
        reasons.append(f"template {template_status}")
    return "; ".join(reasons)


def _drift_recommended_action(
    ownership: str, file_status: str, template_status: str
) -> str:
    if file_status == "unsafe-path":
        return "review-manifest"
    if ownership != "generated":
        if file_status == "missing":
            return "review-project-owned-missing-file"
        if file_status == "modified":
            return "preserve-project-owned-file"
        if template_status in {"changed", "missing"}:
            return "review-project-owned-template-drift"
        return "none"
    if file_status == "missing":
        return "restore-generated-file"
    if file_status == "modified":
        return "review-local-edits-before-overwrite"
    if template_status == "changed":
        return "update-from-current-template"
    if template_status == "missing":
        return "review-missing-template"
    return "none"


def _safe_generated_update_paths(drift: tuple[DriftResult, ...]) -> frozenset[str]:
    return frozenset(
        item.path
        for item in drift
        if item.ownership == "generated"
        and item.file_status == "unchanged"
        and item.template_status == "changed"
    )
