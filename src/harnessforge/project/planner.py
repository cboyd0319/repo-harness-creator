from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .detect import MISSING_VERIFICATION_COMMAND
from ..core.models import ProjectProfile
from ..core.redact import redact_local_paths

SCHEMA_VERSION = "harnessforge.plan.v1"


@dataclass(frozen=True)
class PlanCheck:
    id: str
    label: str
    command: str
    source: str
    working_directory: str
    required: bool
    status: str
    matched_files: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class DiffPlanReport:
    target: str
    base: str
    changed_files: tuple[str, ...]
    checks: tuple[PlanCheck, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    unmatched_files: tuple[str, ...] = ()

    @property
    def verdict(self) -> str:
        if self.blocked_reasons:
            return "blocked"
        if not self.changed_files:
            return "no_changes"
        return "planned"


def build_diff_plan(
    profile: ProjectProfile,
    *,
    since: str,
    explicit_commands: tuple[str, ...] = (),
) -> DiffPlanReport:
    changed_files, git_error = _changed_files(profile.root, since)
    if git_error:
        return DiffPlanReport(
            target=profile.name,
            base=since,
            changed_files=(),
            checks=(),
            blocked_reasons=(git_error,),
            warnings=(),
        )
    if not changed_files:
        return DiffPlanReport(
            target=profile.name,
            base=since,
            changed_files=(),
            checks=(),
            blocked_reasons=(),
            warnings=(f"No changed files detected since {since}.",),
        )

    source = "explicit" if explicit_commands else "detected"
    commands = explicit_commands or profile.verification_commands
    runnable_commands = tuple(
        command for command in commands if not _is_missing_verification(command)
    )
    if not runnable_commands:
        return DiffPlanReport(
            target=profile.name,
            base=since,
            changed_files=changed_files,
            checks=(
                PlanCheck(
                    id=f"project.{source}.0",
                    label="Missing project verification",
                    command=commands[0] if commands else MISSING_VERIFICATION_COMMAND,
                    source=source,
                    working_directory=".",
                    required=True,
                    status="blocked",
                    matched_files=changed_files,
                    reason="No project verification check detected.",
                ),
            ),
            blocked_reasons=("No project verification check detected.",),
            warnings=(),
        )

    checks, unmatched_files = _select_checks(
        runnable_commands,
        changed_files,
        source=source,
    )
    warnings = (
        (f"No matching checks for changed files: {', '.join(unmatched_files)}.",)
        if unmatched_files
        else ()
    )
    return DiffPlanReport(
        target=profile.name,
        base=since,
        changed_files=changed_files,
        checks=checks,
        blocked_reasons=(),
        warnings=warnings,
        unmatched_files=unmatched_files,
    )


def diff_plan_to_dict(report: DiffPlanReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "target": {
            "name": report.target,
            "root": None,
        },
        "mode": "diff",
        "base": report.base,
        "verdict": report.verdict,
        "execution": {
            "commandsExecuted": False,
        },
        "summary": _summary(report.checks),
        "changedFiles": list(report.changed_files),
        "unmatchedFiles": list(report.unmatched_files),
        "checks": [_check_to_dict(check) for check in report.checks],
        "blockedReasons": list(report.blocked_reasons),
        "warnings": list(report.warnings),
    }


def format_diff_plan(report: DiffPlanReport) -> str:
    lines = [
        f"Verification plan: {report.verdict}",
        f"Base: {report.base}",
        "",
    ]
    _append_section(lines, "Blocked reasons", report.blocked_reasons)
    _append_section(lines, "Warnings", report.warnings)
    _append_section(lines, "Changed files", report.changed_files)
    _append_section(lines, "Unmatched files", report.unmatched_files)
    if report.checks:
        lines.append("Checks:")
        for check in report.checks:
            lines.append(
                f"  - {check.id}: {check.status}, command={check.command}"
            )
            lines.append(f"    reason: {check.reason}")
            if check.matched_files:
                lines.append(f"    files: {', '.join(check.matched_files)}")
    return "\n".join(lines).rstrip()


def _changed_files(root: Path, since: str) -> tuple[tuple[str, ...], str]:
    diff_result = _git_command(
        root,
        "diff",
        "--name-only",
        "--diff-filter=ACMRTUXB",
        since,
        "--",
    )
    if diff_result.returncode != 0:
        return (
            (),
            f"Unable to inspect changed files with git diff: {_git_error(diff_result)}",
        )
    untracked_result = _git_command(
        root,
        "ls-files",
        "--others",
        "--exclude-standard",
    )
    if untracked_result.returncode != 0:
        return (
            (),
            "Unable to inspect changed files with git ls-files: "
            f"{_git_error(untracked_result)}",
        )
    files = tuple(
        line.strip().replace("\\", "/")
        for line in (diff_result.stdout + "\n" + untracked_result.stdout).splitlines()
        if line.strip()
    )
    return tuple(dict.fromkeys(files)), ""


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
        return "git returned a non-zero exit code."
    return redact_local_paths(text.splitlines()[0])


def _select_checks(
    commands: tuple[str, ...],
    changed_files: tuple[str, ...],
    *,
    source: str,
) -> tuple[tuple[PlanCheck, ...], tuple[str, ...]]:
    focused: list[PlanCheck] = []
    matched_files: set[str] = set()
    for index, command in enumerate(commands):
        command_tags = _command_tags(command)
        matched = tuple(
            file for file in changed_files if _file_tags(file) & command_tags
        )
        if not matched:
            continue
        matched_files.update(matched)
        focused.append(
            _plan_check(
                index,
                command,
                source,
                matched,
                reason=(
                    "Changed files match command tags: "
                    f"{', '.join(sorted(command_tags))}."
                ),
            )
        )
    if focused:
        unmatched = tuple(file for file in changed_files if file not in matched_files)
        return tuple(focused), unmatched
    return (
        tuple(
            _plan_check(
                index,
                command,
                source,
                changed_files,
                reason="No file-specific match found; include baseline check.",
            )
            for index, command in enumerate(commands)
        ),
        (),
    )


def _plan_check(
    index: int,
    command: str,
    source: str,
    matched_files: tuple[str, ...],
    *,
    reason: str,
) -> PlanCheck:
    return PlanCheck(
        id=f"project.{source}.{index}",
        label="Project verification",
        command=command,
        source=source,
        working_directory=".",
        required=True,
        status="planned",
        matched_files=matched_files,
        reason=reason,
    )


def _file_tags(file: str) -> set[str]:
    path = Path(file)
    suffix = path.suffix.lower()
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    tags: set[str] = set()
    if suffix == ".py" or name in {"pyproject.toml", "requirements.txt", "uv.lock"}:
        tags.add("python")
    if suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"} or name in {
        "package.json",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lock",
        "bun.lockb",
    }:
        tags.update({"node", "javascript"})
    if suffix in {".ts", ".tsx"} or name.startswith("tsconfig"):
        tags.add("typescript")
    if suffix == ".rs" or name in {"cargo.toml", "cargo.lock"}:
        tags.add("rust")
    if suffix == ".go" or name in {"go.mod", "go.sum", "go.work"}:
        tags.add("go")
    if suffix == ".swift" or name in {"package.swift", "package.resolved"}:
        tags.add("swift")
    if suffix == ".java" or name in {
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
    }:
        tags.add("java")
    if suffix == ".cs" or name.endswith((".csproj", ".fsproj", ".sln", ".slnx")):
        tags.add("dotnet")
    if suffix == ".php" or name == "composer.json":
        tags.add("php")
    if suffix == ".rb" or name == "gemfile":
        tags.add("ruby")
    if suffix == ".tf" or name == "terragrunt.hcl":
        tags.add("terraform")
    if suffix in {".md", ".rst", ".txt"} or "docs" in parts or name == "readme.md":
        tags.add("docs")
    if name in {"agents.md", "claude.md", "gemini.md", "action.yml", "action.yaml"}:
        tags.add("harness")
    if "docs" in parts and "harness" in parts:
        tags.add("harness")
    if file.startswith((".github/workflows/", ".github/actions/")):
        tags.update({"harness", "workflow"})
    if name in {"makefile", "gnumakefile"}:
        tags.add("make")
    if name == "justfile":
        tags.add("just")
    if name in {"dockerfile", "containerfile"} or ".devcontainer" in parts:
        tags.add("container")
    if "test" in parts or name.startswith("test_") or name.endswith("_test.py"):
        tags.add("test")
    return tags or {"generic"}


def _command_tags(command: str) -> set[str]:
    text = command.lower()
    tags: set[str] = set()
    if any(token in text for token in ("python", "pytest", "unittest", "ruff", "mypy")):
        tags.add("python")
    if any(token in text for token in ("npm", "pnpm", "yarn", "bun", "node")):
        tags.update({"node", "javascript"})
    if any(token in text for token in ("tsc", "vite", "next")):
        tags.add("typescript")
    if "cargo" in text or "rust" in text:
        tags.add("rust")
    if text.startswith("go ") or " go test" in text:
        tags.add("go")
    if any(token in text for token in ("mvn", "gradle", "java")):
        tags.add("java")
    if "dotnet" in text:
        tags.add("dotnet")
    if "composer" in text:
        tags.add("php")
    if "bundle" in text or "rake" in text:
        tags.add("ruby")
    if "terraform" in text:
        tags.add("terraform")
    if any(token in text for token in ("docs", "markdown", "mkdocs", "link")):
        tags.add("docs")
    if any(
        token in text
        for token in ("harnessforge", "check_pins", "init.sh", "init.ps1")
    ):
        tags.add("harness")
    if text.startswith("make "):
        tags.add("make")
    if text.startswith("just "):
        tags.add("just")
    if any(token in text for token in ("docker", "container")):
        tags.add("container")
    if any(token in text for token in ("test", "check", "lint")):
        tags.add("test")
    return tags or {"generic"}


def _is_missing_verification(command: str) -> bool:
    return command == MISSING_VERIFICATION_COMMAND or command.startswith(
        "REVIEW REQUIRED:"
    )


def _summary(checks: tuple[PlanCheck, ...]) -> dict[str, int]:
    return {
        "total": len(checks),
        "planned": sum(1 for check in checks if check.status == "planned"),
        "blocked": sum(1 for check in checks if check.status == "blocked"),
    }


def _check_to_dict(check: PlanCheck) -> dict[str, Any]:
    return {
        "id": check.id,
        "label": check.label,
        "command": check.command,
        "source": check.source,
        "workingDirectory": check.working_directory,
        "required": check.required,
        "status": check.status,
        "matchedFiles": list(check.matched_files),
        "reason": check.reason,
    }


def _append_section(lines: list[str], title: str, values: tuple[str, ...]) -> None:
    if not values:
        return
    lines.append(f"{title}:")
    for value in values:
        lines.append(f"  - {value}")
    lines.append("")
