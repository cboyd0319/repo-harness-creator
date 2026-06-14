from __future__ import annotations

from pathlib import Path

from .audit import audit_target
from .generate import create_harness
from .models import AuditResult, ProjectProfile, WriteResult


def plan_or_apply_update(
    target: Path,
    *,
    apply: bool,
    force: bool = False,
    agent_file: str = "AGENTS.md",
    with_ci_workflow: bool = False,
    with_self_heal_workflow: bool = False,
) -> tuple[AuditResult, ProjectProfile | None, tuple[WriteResult, ...]]:
    before = audit_target(target)
    if not apply:
        return before, None, ()
    profile, writes = create_harness(
        target,
        agent_file=agent_file,
        force=force,
        with_ci_workflow=with_ci_workflow,
        with_self_heal_workflow=with_self_heal_workflow,
    )
    return before, profile, writes
