from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.models import WriteResult
from ..core.paths import is_inside_root, path_from_relative_text

SCHEMA_VERSION = "harnessforge.stateMigration.v1"
LEGACY_STATE_FILES = ("progress.md", "session-handoff.md")
CURRENT_STATE_PATH = "current-state.md"
SECTION_START = "<!-- harnessforge-state-migration:start -->"
SECTION_END = "<!-- harnessforge-state-migration:end -->"
MAX_INCLUDED_LINES = 80
MAX_INCLUDED_CHARS = 8000


@dataclass(frozen=True)
class LegacyStateSource:
    path: str
    exists: bool
    status: str
    line_count: int = 0
    char_count: int = 0
    included_lines: int = 0
    included_chars: int = 0
    truncated: bool = False
    excerpt: str = ""
    error: str = ""


@dataclass(frozen=True)
class StateMigrationPlan:
    payload: dict[str, Any]
    writes: tuple[WriteResult, ...]
    changed_files: int


def build_state_migration_plan(target: Path, *, apply: bool) -> StateMigrationPlan:
    root = target.resolve()
    sources = tuple(_legacy_source(root, relative) for relative in LEGACY_STATE_FILES)
    preview = _preview_current_state(root, sources)
    planned = _planned_writes(root, preview)
    applied: tuple[WriteResult, ...] = ()
    if apply:
        applied = _apply_preview(root, preview)
    changed_files = sum(1 for write in applied if write.status in {"written", "updated"})
    active_writes = applied if apply else planned
    warnings = _warnings(sources, preview)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "apply" if apply else "dry_run",
        "target": {
            "name": root.name,
            "root": None,
        },
        "execution": {
            "commandsExecuted": False,
            "writesPerformed": bool(apply and changed_files),
        },
        "legacyFiles": [_source_to_dict(source) for source in sources],
        "currentState": _current_state_to_dict(root, preview, active_writes),
        "plannedWrites": [_write_to_dict(root, write) for write in planned],
        "appliedWrites": [_write_to_dict(root, write) for write in applied],
        "changedFiles": changed_files,
        "warnings": warnings,
        "nextActions": _next_actions(sources, preview),
    }
    return StateMigrationPlan(
        payload=payload,
        writes=active_writes,
        changed_files=changed_files,
    )


def format_state_migration_plan(payload: dict[str, Any]) -> str:
    lines = [
        "HarnessForge State Migration",
        f"Mode: {payload['mode']}",
        f"Target: {payload['target']['name']}",
        f"Writes performed: {str(payload['execution']['writesPerformed']).lower()}",
        f"Changed files: {payload['changedFiles']}",
        "",
        "Legacy files:",
    ]
    for item in payload["legacyFiles"]:
        if not item["exists"]:
            lines.append(f"  - {item['path']}: missing")
            continue
        suffix = " truncated" if item["truncated"] else ""
        lines.append(
            f"  - {item['path']}: {item['status']}, "
            f"{item['lineCount']} lines, {item['charCount']} chars{suffix}"
        )
    lines.extend(["", "Planned writes:"])
    planned = payload["plannedWrites"]
    if planned:
        for write in planned:
            lines.append(
                f"  - {write['status'].upper()} {write['path']} ({write['reason']})"
            )
    else:
        lines.append("  - none")
    applied = payload["appliedWrites"]
    if applied:
        lines.extend(["", "Applied writes:"])
        for write in applied:
            lines.append(
                f"  - {write['status'].upper()} {write['path']} ({write['reason']})"
            )
    if payload["warnings"]:
        lines.extend(["", "Warnings:"])
        lines.extend(f"  - {warning}" for warning in payload["warnings"])
    if payload["nextActions"]:
        lines.extend(["", "Next actions:"])
        lines.extend(f"  - {action}" for action in payload["nextActions"])
    return "\n".join(lines).rstrip() + "\n"


def _legacy_source(root: Path, relative_path: str) -> LegacyStateSource:
    path = _target_path(root, relative_path)
    if not path.exists():
        return LegacyStateSource(
            path=relative_path,
            exists=False,
            status="missing",
        )
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return LegacyStateSource(
            path=relative_path,
            exists=True,
            status="unreadable",
            error=str(exc),
        )
    lines = text.splitlines()
    excerpt_lines: list[str] = []
    included_chars = 0
    truncated = False
    for line in lines:
        next_chars = included_chars + len(line) + 1
        if len(excerpt_lines) >= MAX_INCLUDED_LINES or next_chars > MAX_INCLUDED_CHARS:
            truncated = True
            break
        excerpt_lines.append(line)
        included_chars = next_chars
    excerpt = "\n".join(excerpt_lines).rstrip()
    if excerpt:
        excerpt += "\n"
    return LegacyStateSource(
        path=relative_path,
        exists=True,
        status="source_preserved",
        line_count=len(lines),
        char_count=len(text),
        included_lines=len(excerpt_lines),
        included_chars=len(excerpt),
        truncated=truncated or len(excerpt_lines) < len(lines),
        excerpt=excerpt,
    )


def _preview_current_state(
    root: Path,
    sources: tuple[LegacyStateSource, ...],
) -> dict[str, str]:
    existing_sources = tuple(source for source in sources if source.exists)
    if not existing_sources:
        return {}
    path = _target_path(root, CURRENT_STATE_PATH)
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        current = _new_current_state_text()
    section = _migration_section(existing_sources)
    return {CURRENT_STATE_PATH: _replace_or_append_section(current, section)}


def _new_current_state_text() -> str:
    return "\n".join(
        [
            "# Current State",
            "",
            "Last Updated: REVIEW REQUIRED",
            "",
            "## Current Objective",
            "",
            "Review migrated legacy state and keep only current facts.",
            "",
            "## State Contract",
            "",
            "- `current-state.md`: current objective, blockers, trusted verification,",
            "  touched surfaces, and next step.",
            "- `feature_list.json`: machine-readable feature state.",
            "- `docs/harness/evidence/evidence-log.md`: meaningful verification evidence.",
            "- Do not recreate root `progress.md` or `session-handoff.md`.",
            "",
            "## Trusted Verification",
            "",
            "- Pending review after migration.",
            "",
            "## Touched Surfaces",
            "",
            "- `current-state.md`",
            "",
            "## Blockers",
            "",
            "- None recorded.",
            "",
            "## Next Step",
            "",
            "Review migrated excerpts and move durable facts to the owning section.",
            "",
        ]
    )


def _migration_section(sources: tuple[LegacyStateSource, ...]) -> str:
    lines = [
        SECTION_START,
        "## Migrated Legacy State",
        "",
        "Legacy state sources are preserved in place. This section is a bounded",
        "review aid for consolidating current facts into the regular sections above.",
        "",
        "| Source | Status | Lines | Chars | Included |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for source in sources:
        lines.append(
            f"| `{source.path}` | {source.status} | {source.line_count} | "
            f"{source.char_count} | {source.included_lines} lines |"
        )
    for source in sources:
        lines.extend(["", f"### {source.path}", ""])
        if source.status == "unreadable":
            lines.append(f"Unreadable as UTF-8: {source.error}")
            continue
        if not source.excerpt:
            lines.append("_No text captured._")
            continue
        lines.extend(["```markdown", source.excerpt.rstrip(), "```"])
        if source.truncated:
            lines.append("")
            lines.append(
                "Excerpt truncated. Review the source file directly before deleting it."
            )
    lines.extend(["", SECTION_END, ""])
    return "\n".join(lines)


def _replace_or_append_section(current: str, section: str) -> str:
    text = current.rstrip() + "\n"
    if SECTION_START in text and SECTION_END in text:
        prefix, rest = text.split(SECTION_START, 1)
        _, suffix = rest.split(SECTION_END, 1)
        return prefix.rstrip() + "\n\n" + section + suffix.lstrip()
    return text + "\n" + section


def _planned_writes(root: Path, preview: dict[str, str]) -> tuple[WriteResult, ...]:
    writes: list[WriteResult] = []
    for relative_path in sorted(preview):
        path = _target_path(root, relative_path)
        before = path.read_text(encoding="utf-8") if path.exists() else None
        after = preview[relative_path]
        if before == after:
            status = "unchanged"
        elif before is None:
            status = "would_write"
        else:
            status = "would_update"
        writes.append(WriteResult(path=path, status=status, reason="state-migration"))
    return tuple(writes)


def _apply_preview(root: Path, preview: dict[str, str]) -> tuple[WriteResult, ...]:
    writes: list[WriteResult] = []
    for relative_path in sorted(preview):
        path = _target_path(root, relative_path)
        before = path.read_text(encoding="utf-8") if path.exists() else None
        after = preview[relative_path]
        if before == after:
            writes.append(WriteResult(path=path, status="unchanged", reason="state-migration"))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(after, encoding="utf-8")
        writes.append(
            WriteResult(
                path=path,
                status="updated" if before is not None else "written",
                reason="state-migration",
            )
        )
    return tuple(writes)


def _target_path(root: Path, relative_path: str) -> Path:
    path = root / path_from_relative_text(relative_path)
    if not is_inside_root(path, root):
        raise ValueError(f"state migration path escapes target: {relative_path}")
    return path


def _current_state_to_dict(
    root: Path,
    preview: dict[str, str],
    writes: tuple[WriteResult, ...],
) -> dict[str, Any]:
    path = _target_path(root, CURRENT_STATE_PATH)
    status = "not_required"
    if writes:
        status = writes[0].status
    elif preview:
        status = "unchanged"
    return {
        "path": CURRENT_STATE_PATH,
        "exists": path.exists(),
        "plannedStatus": status,
    }


def _warnings(
    sources: tuple[LegacyStateSource, ...],
    preview: dict[str, str],
) -> list[str]:
    warnings = []
    if not preview:
        warnings.append(
            "No legacy progress.md or session-handoff.md files were found; "
            "current-state.md was not changed."
        )
    for source in sources:
        if source.status == "unreadable":
            warnings.append(f"{source.path} could not be read as UTF-8.")
        elif source.truncated:
            warnings.append(
                f"{source.path} excerpt was truncated; review the source before cleanup."
            )
    return warnings


def _next_actions(
    sources: tuple[LegacyStateSource, ...],
    preview: dict[str, str],
) -> list[str]:
    if not preview:
        return ["Keep using current-state.md as the single active restart file."]
    existing = [source.path for source in sources if source.exists]
    return [
        "Review current-state.md and move only still-current facts into its normal sections.",
        "Preserve or delete legacy state files through a separate reviewed repo decision.",
        "Do not recreate split progress/session-handoff state after migration.",
        f"Legacy sources preserved: {', '.join(existing)}.",
    ]


def _source_to_dict(source: LegacyStateSource) -> dict[str, Any]:
    return {
        "path": source.path,
        "exists": source.exists,
        "status": source.status,
        "lineCount": source.line_count,
        "charCount": source.char_count,
        "includedLines": source.included_lines,
        "includedChars": source.included_chars,
        "truncated": source.truncated,
        "error": source.error,
    }


def _write_to_dict(root: Path, write: WriteResult) -> dict[str, str]:
    return {
        "path": write.path.resolve().relative_to(root.resolve()).as_posix(),
        "status": write.status,
        "reason": write.reason,
    }
