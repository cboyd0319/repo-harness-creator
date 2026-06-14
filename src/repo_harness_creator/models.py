from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectProfile:
    root: Path
    name: str
    stack: str
    languages: tuple[str, ...]
    package_managers: tuple[str, ...]
    runtime_files: tuple[str, ...]
    verification_commands: tuple[str, ...]
    components: tuple[str, ...]
    files: tuple[str, ...] = field(repr=False)
    workspace_markers: tuple[str, ...] = ()
    routing_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class WriteResult:
    path: Path
    status: str
    reason: str = ""


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    message: str
    detail: str = ""


@dataclass(frozen=True)
class DomainScore:
    name: str
    score: int
    passed: int
    total: int
    checks: tuple[CheckResult, ...]


@dataclass(frozen=True)
class AuditResult:
    target_name: str
    overall: int
    bottleneck: str
    domains: tuple[DomainScore, ...]
    recommendations: tuple[str, ...]
    manifest_failures: tuple[str, ...] = ()
