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
    config_precedence: tuple[str, ...] = ()
    file_scan_limit: int = 4000
    file_scan_truncated: bool = False
    component_scan_limit: int = 80
    component_scan_truncated: bool = False


@dataclass(frozen=True)
class WriteResult:
    path: Path
    status: str
    reason: str = ""


@dataclass(frozen=True)
class DriftResult:
    path: str
    ownership: str
    file_status: str
    template_status: str
    reason: str = ""
    recommended_action: str = "none"


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
