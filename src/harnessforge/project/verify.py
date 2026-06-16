from __future__ import annotations

import os
import platform
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from .detect import MISSING_VERIFICATION_COMMAND
from ..core.models import ProjectProfile
from ..core.redact import redact_local_paths


SCHEMA_VERSION = "harnessforge.verify.v1"
PLAN_MESSAGE = "Plan mode only. Command execution requires explicit run mode."
DEFAULT_TIMEOUT_SECONDS = 300.0
PREVIEW_LIMIT = 4000


@dataclass(frozen=True)
class VerifyCheck:
    id: str
    label: str
    command: str
    source: str
    working_directory: str
    required: bool
    status: str
    exit_code: int | None
    duration_ms: float | None
    message: str
    stdout_preview: str | None
    stderr_preview: str | None


@dataclass(frozen=True)
class VerifyReport:
    target: str
    mode: str
    verdict: str
    checks: tuple[VerifyCheck, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    commands_executed: bool = False
    started_at: str | None = None
    ended_at: str | None = None
    duration_ms: float | None = None


def build_verify_plan(
    profile: ProjectProfile, *, explicit_commands: tuple[str, ...] = ()
) -> VerifyReport:
    commands = explicit_commands or profile.verification_commands
    source = "explicit" if explicit_commands else "detected"
    checks: list[VerifyCheck] = []
    blocked: list[str] = []
    for index, command in enumerate(commands):
        is_missing = command == MISSING_VERIFICATION_COMMAND or command.startswith(
            "REVIEW REQUIRED:"
        )
        status = "blocked" if is_missing else "planned"
        if is_missing:
            blocked.append("No project verification check detected.")
        checks.append(
            VerifyCheck(
                id=f"project.{source}.{index}",
                label=(
                    "Missing project verification"
                    if is_missing
                    else "Project verification"
                ),
                command=command,
                source=source,
                working_directory=".",
                required=True,
                status=status,
                exit_code=None,
                duration_ms=None,
                message=(
                    "Add --command with the smallest reliable project check."
                    if is_missing
                    else PLAN_MESSAGE
                ),
                stdout_preview=None,
                stderr_preview=None,
            )
        )
    verdict = "blocked" if blocked else "planned"
    return VerifyReport(
        target=profile.name,
        mode="plan",
        verdict=verdict,
        checks=tuple(checks),
        blocked_reasons=tuple(_dedupe(blocked)),
        warnings=(),
    )


def run_verify_checks(
    profile: ProjectProfile,
    *,
    explicit_commands: tuple[str, ...] = (),
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> VerifyReport:
    plan = build_verify_plan(profile, explicit_commands=explicit_commands)
    if plan.blocked_reasons:
        return VerifyReport(
            target=plan.target,
            mode="run",
            verdict="blocked",
            checks=plan.checks,
            blocked_reasons=plan.blocked_reasons,
            warnings=plan.warnings,
            commands_executed=False,
        )

    started = _utc_now()
    start_time = monotonic()
    checks = tuple(
        _run_check(check, profile.root, timeout_seconds=timeout_seconds)
        for check in plan.checks
    )
    ended = _utc_now()
    duration_ms = round((monotonic() - start_time) * 1000, 3)
    verdict = "passed"
    if any(check.status in {"failed", "timed_out", "error"} for check in checks):
        verdict = "failed"
    return VerifyReport(
        target=profile.name,
        mode="run",
        verdict=verdict,
        checks=checks,
        blocked_reasons=(),
        warnings=(),
        commands_executed=True,
        started_at=started,
        ended_at=ended,
        duration_ms=duration_ms,
    )


def verify_report_to_dict(report: VerifyReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "target": {
            "name": report.target,
            "root": None,
        },
        "mode": report.mode,
        "verdict": report.verdict,
        "platform": {
            "os": sys.platform,
            "python": platform.python_version(),
            "runner": "local",
        },
        "execution": {
            "commandsExecuted": report.commands_executed,
            "startedAt": report.started_at,
            "endedAt": report.ended_at,
            "durationMs": report.duration_ms,
        },
        "summary": _summary(report.checks),
        "checks": [_check_to_dict(check) for check in report.checks],
        "blockedReasons": list(report.blocked_reasons),
        "warnings": list(report.warnings),
        "artifacts": [],
    }


def format_verify_plan(report: VerifyReport) -> str:
    lines = [f"Verify {report.mode}: {report.verdict}", ""]
    if report.blocked_reasons:
        lines.append("Blocked reasons:")
        lines.extend(f"  - {reason}" for reason in report.blocked_reasons)
        lines.append("")
    lines.append("Checks:")
    for check in report.checks:
        lines.append(
            f"  - {check.id}: {check.status}, source={check.source}, "
            f"exit={check.exit_code}, command={check.command}"
        )
    return "\n".join(lines).rstrip()


def _run_check(
    check: VerifyCheck,
    root: Path,
    *,
    timeout_seconds: float,
) -> VerifyCheck:
    start = monotonic()
    try:
        args = _command_args(check.command)
        completed = subprocess.run(
            args,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except ValueError as exc:
        return _replace_check(
            check,
            status="error",
            duration_ms=_elapsed_ms(start),
            message=redact_local_paths(str(exc)),
        )
    except OSError as exc:
        return _replace_check(
            check,
            status="error",
            duration_ms=_elapsed_ms(start),
            message=f"Command could not start: {redact_local_paths(str(exc))}",
        )
    except subprocess.TimeoutExpired as exc:
        return _replace_check(
            check,
            status="timed_out",
            duration_ms=_elapsed_ms(start),
            message=f"Command timed out after {timeout_seconds:g} seconds.",
            stdout_preview=_preview(exc.stdout),
            stderr_preview=_preview(exc.stderr),
        )

    status = "passed" if completed.returncode == 0 else "failed"
    message = "Command passed." if status == "passed" else "Command failed."
    return _replace_check(
        check,
        status=status,
        exit_code=completed.returncode,
        duration_ms=_elapsed_ms(start),
        message=message,
        stdout_preview=_preview(completed.stdout),
        stderr_preview=_preview(completed.stderr),
    )


def _command_args(command: str) -> list[str]:
    if "\n" in command or "\r" in command:
        raise ValueError("verification command must be one line")
    try:
        args = shlex.split(command, posix=os.name != "nt")
    except ValueError as exc:
        raise ValueError(f"verification command is not parseable: {exc}") from exc
    if not args:
        raise ValueError("verification command is empty")
    if os.name == "nt":
        args = [_strip_wrapping_quotes(arg) for arg in args]
    shell_operators = {"&&", "||", ";", "|", ">", ">>", "<", "2>", "2>>"}
    if any(arg in shell_operators for arg in args):
        raise ValueError(
            "verification command uses shell control syntax; use one command per --command"
        )
    return args


def _strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _replace_check(
    check: VerifyCheck,
    *,
    status: str,
    duration_ms: float,
    message: str,
    exit_code: int | None = None,
    stdout_preview: str | None = None,
    stderr_preview: str | None = None,
) -> VerifyCheck:
    return VerifyCheck(
        id=check.id,
        label=check.label,
        command=check.command,
        source=check.source,
        working_directory=check.working_directory,
        required=check.required,
        status=status,
        exit_code=exit_code,
        duration_ms=duration_ms,
        message=message,
        stdout_preview=stdout_preview,
        stderr_preview=stderr_preview,
    )


def _preview(value: str | bytes | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = value
    text = redact_local_paths(text)
    if not text:
        return None
    if len(text) <= PREVIEW_LIMIT:
        return text
    return f"{text[:PREVIEW_LIMIT]}\n[truncated]"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _elapsed_ms(start: float) -> float:
    return round((monotonic() - start) * 1000, 3)


def _summary(checks: tuple[VerifyCheck, ...]) -> dict[str, int]:
    counts = {
        "total": len(checks),
        "planned": 0,
        "skipped": 0,
        "blocked": 0,
        "passed": 0,
        "failed": 0,
        "timedOut": 0,
        "errors": 0,
    }
    for check in checks:
        if check.status == "timed_out":
            counts["timedOut"] += 1
        elif check.status == "error":
            counts["errors"] += 1
        elif check.status in counts:
            counts[check.status] += 1
    return counts


def _check_to_dict(check: VerifyCheck) -> dict[str, Any]:
    return {
        "id": check.id,
        "label": check.label,
        "command": check.command,
        "source": check.source,
        "workingDirectory": check.working_directory,
        "required": check.required,
        "status": check.status,
        "exitCode": check.exit_code,
        "durationMs": check.duration_ms,
        "message": check.message,
        "stdoutPreview": check.stdout_preview,
        "stderrPreview": check.stderr_preview,
    }


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
