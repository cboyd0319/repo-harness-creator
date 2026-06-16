from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..assessment.audit import audit_target
from ..core.harness_paths import existing_harness_path
from ..core.models import AuditResult
from ..core.redact import redact_local_paths
from .detect import detect_project
from .readiness import ReadinessReport, inspect_readiness

SCHEMA_VERSION = "harnessforge.session.v1"
STATE_FILES = (
    "feature_list.json",
    "current-state.md",
    "docs/plans/active/status.md",
    "docs/plans/index.json",
)
STATE_FILE_HARNESS_KEYS = ("evidence_log",)


@dataclass(frozen=True)
class GitSnapshot:
    available: bool
    status: str
    latest_commit: str
    message: str = ""


@dataclass(frozen=True)
class StateFileSnapshot:
    path: str
    present: bool


@dataclass(frozen=True)
class SessionReport:
    target: str
    stack: str
    git: GitSnapshot
    readiness: ReadinessReport
    audit: AuditResult | None
    state_files: tuple[StateFileSnapshot, ...]


def build_session_report(target: Path) -> SessionReport:
    root = target.resolve()
    profile = detect_project(root)
    readiness = inspect_readiness(profile)
    audit = audit_target(root) if _has_harness_surface(root) else None
    return SessionReport(
        target=profile.name,
        stack=profile.stack,
        git=_git_snapshot(root),
        readiness=readiness,
        audit=audit,
        state_files=_state_file_snapshots(root),
    )


def session_report_to_dict(report: SessionReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "target": {
            "name": report.target,
            "root": None,
        },
        "detectedStack": report.stack,
        "git": {
            "available": report.git.available,
            "status": report.git.status,
            "latestCommit": report.git.latest_commit,
            "message": report.git.message,
        },
        "readiness": {
            "verdict": report.readiness.verdict,
            "warningCount": len(report.readiness.warnings),
            "blockedCount": len(report.readiness.blocked_reasons),
        },
        "harnessAudit": (
            None
            if report.audit is None
            else {
                "overall": report.audit.overall,
                "bottleneck": report.audit.bottleneck,
            }
        ),
        "stateFiles": [
            {"path": item.path, "present": item.present}
            for item in report.state_files
        ],
        "nextActions": list(report.readiness.next_actions),
    }


def format_session_report(report: SessionReport) -> str:
    lines = [
        f"Session snapshot: {report.target}",
        f"Detected stack: {report.stack}",
    ]
    if report.git.available:
        lines.append(f"Git: {report.git.status or 'clean'}")
        if report.git.latest_commit:
            lines.append(f"Latest commit: {report.git.latest_commit}")
    else:
        suffix = f" ({report.git.message})" if report.git.message else ""
        lines.append(f"Git: unavailable{suffix}")
    lines.append(
        "Readiness: "
        f"{report.readiness.verdict} "
        f"({len(report.readiness.warnings)} warnings, "
        f"{len(report.readiness.blocked_reasons)} blocked)"
    )
    if report.audit is None:
        lines.append("Harness audit: not detected")
    else:
        lines.append(
            f"Harness audit: {report.audit.overall}/100 "
            f"(bottleneck: {report.audit.bottleneck})"
        )
    lines.append("")
    lines.append("State files:")
    for item in report.state_files:
        status = "present" if item.present else "missing"
        lines.append(f"  - {item.path}: {status}")
    lines.append("")
    lines.append("Next actions:")
    actions = report.readiness.next_actions or (
        "Run harnessforge quickstart --target <repo> before generating files.",
    )
    for action in actions:
        lines.append(f"  - {action}")
    return "\n".join(lines)


def _has_harness_surface(root: Path) -> bool:
    return any(
        (root / relative).exists()
        for relative in (
            "AGENTS.md",
            "docs/harness/manifest.json",
            "docs/harness/README.md",
        )
    )


def _state_file_snapshots(root: Path) -> tuple[StateFileSnapshot, ...]:
    snapshots = [
        StateFileSnapshot(path=relative, present=(root / relative).exists())
        for relative in STATE_FILES
    ]
    for key in STATE_FILE_HARNESS_KEYS:
        relative = existing_harness_path(root, key)
        snapshots.append(
            StateFileSnapshot(path=relative, present=(root / relative).exists())
        )
    return tuple(snapshots)


def _git_snapshot(root: Path) -> GitSnapshot:
    status = _git_command(root, "status", "--short", "--branch")
    if status.returncode != 0:
        return GitSnapshot(
            available=False,
            status="",
            latest_commit="",
            message=_git_error(status),
        )
    latest = _git_command(root, "log", "-1", "--oneline")
    latest_commit = latest.stdout.strip() if latest.returncode == 0 else ""
    return GitSnapshot(
        available=True,
        status=status.stdout.strip(),
        latest_commit=latest_commit,
    )


def _git_command(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(
            args=["git", "-C", str(root), *args],
            returncode=1,
            stdout="",
            stderr=str(exc),
        )


def _git_error(result: subprocess.CompletedProcess[str]) -> str:
    text = result.stderr.strip() or result.stdout.strip()
    if not text:
        return ""
    first_line = text.splitlines()[0]
    return redact_local_paths(first_line)
