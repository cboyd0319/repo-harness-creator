from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

from .detect import detect_project
from .models import ProjectProfile, WriteResult
from .paths import is_inside_root
from .redact import redact_local_paths

TEMPLATE_ROOT = files("repo_harness_creator").joinpath("templates")


def create_harness(
    target: Path,
    *,
    agent_file: str = "AGENTS.md",
    force: bool = False,
    dry_run: bool = False,
    package_manager: str | None = None,
    commands: tuple[str, ...] = (),
    project_name: str | None = None,
) -> tuple[ProjectProfile, tuple[WriteResult, ...]]:
    agent_file = _validate_agent_file(agent_file)
    profile = detect_project(
        target,
        explicit_package_manager=package_manager,
        explicit_commands=commands,
    )
    context = _template_context(profile, agent_file=agent_file, project_name=project_name)
    specs = _template_specs(agent_file)
    _validate_destinations(profile.root, tuple(spec[1] for spec in specs))
    results: list[WriteResult] = []
    for template_name, relative_path, executable in specs:
        destination = profile.root / relative_path
        if template_name == "manifest.json.tmpl":
            content = _manifest_content(profile, agent_file)
        elif template_name == "feature-list.schema.json.tmpl":
            content = _feature_list_schema()
        else:
            content = _render_template(template_name, context)
        content = redact_local_paths(content)
        results.append(
            _write_file(
                profile.root,
                destination,
                content,
                executable=executable,
                force=force,
                dry_run=dry_run,
            )
        )
    return profile, tuple(results)


def _template_specs(agent_file: str) -> tuple[tuple[str, str, bool], ...]:
    return (
        ("agents.md.tmpl", agent_file, False),
        ("feature-list.json.tmpl", "feature_list.json", False),
        ("feature-list.schema.json.tmpl", "docs/harness/feature-list.schema.json", False),
        ("progress.md.tmpl", "progress.md", False),
        ("session-handoff.md.tmpl", "session-handoff.md", False),
        ("init.sh.tmpl", "init.sh", True),
        ("init.ps1.tmpl", "init.ps1", False),
        ("harness-readme.md.tmpl", "docs/harness/README.md", False),
        ("change-contract.md.tmpl", "docs/harness/change-contract.md", False),
        ("verification-matrix.md.tmpl", "docs/harness/verification-matrix.md", False),
        ("component-inventory.md.tmpl", "docs/harness/component-inventory.md", False),
        ("dependency-change-policy.md.tmpl", "docs/harness/dependency-change-policy.md", False),
        ("security-boundary-map.md.tmpl", "docs/harness/security-boundary-map.md", False),
        ("feature-privacy-labels.json.tmpl", "docs/harness/feature-privacy-labels.json", False),
        ("evidence-log.md.tmpl", "docs/harness/evidence-log.md", False),
        ("clean-state-checklist.md.tmpl", "docs/harness/clean-state-checklist.md", False),
        ("evaluator-rubric.md.tmpl", "docs/harness/evaluator-rubric.md", False),
        ("quality-document.md.tmpl", "docs/harness/quality-document.md", False),
        ("self-healing.md.tmpl", "docs/harness/self-healing.md", False),
        ("research-sources.json.tmpl", "docs/harness/research-sources.json", False),
        ("research-inbox.md.tmpl", "docs/harness/research-inbox.md", False),
        ("agent-operating-model.md.tmpl", "docs/harness/agent-operating-model.md", False),
        ("multi-agent-orchestration.md.tmpl", "docs/harness/multi-agent-orchestration.md", False),
        ("entropy-control.md.tmpl", "docs/harness/entropy-control.md", False),
        ("sources.md.tmpl", "docs/harness/sources.md", False),
        ("manifest.json.tmpl", "docs/harness/manifest.json", False),
    )


def _validate_agent_file(agent_file: str) -> str:
    name = agent_file.strip()
    path = Path(name)
    if (
        not name
        or path.is_absolute()
        or path.name != name
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or not name.endswith(".md")
    ):
        raise ValueError(
            "--agent-file must be a Markdown filename in the target repository root"
        )
    return name


def _template_context(
    profile: ProjectProfile, *, agent_file: str, project_name: str | None
) -> dict[str, str]:
    now = datetime.now(UTC).date().isoformat()
    commands = profile.verification_commands
    return {
        "agent_file": agent_file,
        "project_name": project_name or profile.name,
        "detected_stack": profile.stack,
        "languages": ", ".join(profile.languages),
        "package_managers": ", ".join(profile.package_managers) or "none detected",
        "runtime_files": ", ".join(profile.runtime_files) or "none detected",
        "components_markdown": _components_markdown(profile.components),
        "workspace_markers_markdown": _workspace_markers_markdown(
            profile.workspace_markers
        ),
        "routing_markers_markdown": _routing_markers_markdown(
            profile.routing_markers
        ),
        "generated_date": now,
        "commands_markdown": "\n".join(f"- `{command}`" for command in commands),
        "commands_shell": "\n\n".join(_shell_command_block(command) for command in commands),
        "commands_powershell": "\n\n".join(
            _powershell_command_block(command) for command in commands
        ),
    }


def _render_template(template_name: str, context: dict[str, str]) -> str:
    template = TEMPLATE_ROOT.joinpath(template_name).read_text(encoding="utf-8")
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _write_file(
    root: Path,
    path: Path,
    content: str,
    *,
    executable: bool,
    force: bool,
    dry_run: bool,
) -> WriteResult:
    if not is_inside_root(path, root):
        raise ValueError(f"refusing to write outside target repository: {path}")
    if path.exists() and not force:
        return WriteResult(path=path, status="skipped", reason="exists")
    if dry_run:
        return WriteResult(path=path, status="would_write")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    if executable and os.name != "nt":
        current = path.stat().st_mode
        path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return WriteResult(path=path, status="written")


def _validate_destinations(root: Path, relative_paths: tuple[str, ...]) -> None:
    for relative_path in relative_paths:
        destination = root / relative_path
        if not is_inside_root(destination, root):
            raise ValueError(f"refusing to write outside target repository: {destination}")


def _shell_command_block(command: str) -> str:
    display = command.replace(chr(34), chr(92) + chr(34))
    runnable = _portable_shell_command(command)
    return f'echo "== {display} =="\n{runnable}'


def _powershell_command_block(command: str) -> str:
    escaped = command.replace("'", "''")
    runnable = _portable_powershell_command(command)
    return f"Write-Host '== {escaped} =='\n{runnable}"


def _portable_shell_command(command: str) -> str:
    python_args = _python_command_args(command)
    if python_args is not None:
        return f'"${{PYTHON_BIN}}" {python_args}'.rstrip()
    return command


def _portable_powershell_command(command: str) -> str:
    python_args = _python_command_args(command)
    if python_args is not None:
        return f"& $PythonBin {python_args}".rstrip()
    if command == "./gradlew" or command.startswith("./gradlew "):
        args = command.removeprefix("./gradlew").strip()
        suffix = f" {args}" if args else ""
        return (
            "if (Test-Path '.\\gradlew.bat') { "
            f"& '.\\gradlew.bat'{suffix} "
            "} elseif (Test-Path '.\\gradlew') { "
            f"& '.\\gradlew'{suffix} "
            "} else { throw 'Gradle wrapper not found' }"
        )
    return command


def _python_command_args(command: str) -> str | None:
    for executable in ("python", "python3"):
        if command == executable:
            return ""
        prefix = f"{executable} "
        if command.startswith(prefix):
            return command.removeprefix(prefix).strip()
    return None


def _manifest_content(profile: ProjectProfile, agent_file: str) -> str:
    manifest = {
        "version": 1,
        "generatedBy": "repo-harness-creator",
        "generatedFor": profile.name,
        "detectedStack": profile.stack,
        "supportedPlatforms": {
            "python": "3.13+",
            "macOS": "15+",
            "windows": "11+",
            "linux": "Ubuntu 22.04+ floor; other modern distributions are best effort",
        },
        "requiredFiles": [
            agent_file,
            "feature_list.json",
            "progress.md",
            "session-handoff.md",
            "init.sh",
            "init.ps1",
            "docs/harness/README.md",
            "docs/harness/change-contract.md",
            "docs/harness/verification-matrix.md",
            "docs/harness/component-inventory.md",
            "docs/harness/dependency-change-policy.md",
            "docs/harness/security-boundary-map.md",
            "docs/harness/feature-privacy-labels.json",
            "docs/harness/evidence-log.md",
            "docs/harness/clean-state-checklist.md",
            "docs/harness/evaluator-rubric.md",
            "docs/harness/quality-document.md",
            "docs/harness/self-healing.md",
            "docs/harness/research-sources.json",
            "docs/harness/research-inbox.md",
            "docs/harness/manifest.json",
            "docs/harness/sources.md",
            "docs/harness/entropy-control.md",
            "docs/harness/agent-operating-model.md",
            "docs/harness/multi-agent-orchestration.md",
            "docs/harness/feature-list.schema.json",
        ],
        "requiredHarnessSnippets": {
            agent_file: [
                "Startup",
                "Verification",
                "Definition Of Done",
                "feature_list.json",
                "progress.md",
            ],
            "docs/harness/README.md": [
                "Operating Loop",
                "When To Add Harness",
                "Assessment And Updates",
            ],
            "docs/harness/change-contract.md": [
                "Problem",
                "Acceptance Criteria",
                "Verification",
                "Rollback",
            ],
            "docs/harness/verification-matrix.md": [
                "Change Type",
                "Required Checks",
                "When Checks Cannot Run",
            ],
            "docs/harness/component-inventory.md": [
                "Component Inventory",
                "Detected Workspace Markers",
                "Detected Routing Markers",
                "Detected Components",
                "Routing Rules",
            ],
            "docs/harness/dependency-change-policy.md": [
                "latest stable",
                "exact pins",
                "GitHub Actions",
            ],
            "docs/harness/security-boundary-map.md": [
                "Access Boundaries",
                "Data Boundaries",
                "Required Checks",
                "security wins",
            ],
            "docs/harness/feature-privacy-labels.json": [
                "External AI optional",
                "Sensitive",
                "Public-data only",
            ],
            "docs/harness/evidence-log.md": [
                "Date",
                "Scope",
                "Command Or Review",
            ],
            "docs/harness/clean-state-checklist.md": [
                "Startup path",
                "Verification path",
                "Next Session",
            ],
            "docs/harness/evaluator-rubric.md": [
                "Correctness",
                "Verification",
                "Handoff Readiness",
            ],
            "docs/harness/quality-document.md": [
                "Quality Document",
                "Domain Grades",
                "Harness Simplification",
            ],
            "docs/harness/self-healing.md": [
                "Self-healing must be reviewable",
                "Safe Loop",
                "Promotion Rule",
            ],
            "docs/harness/research-sources.json": [
                "openai-harness-engineering",
                "walkinglabs-course",
                "github-actions-secure-use",
                "pnpm-workspaces",
                "github-actions-workflow-syntax",
                "terraform-standard-module-structure",
            ],
            "docs/harness/research-inbox.md": [
                "Research Inbox",
                "Promotion checklist",
            ],
        },
        "verificationCommands": list(profile.verification_commands),
        "detectedComponents": list(profile.components),
        "detectedWorkspaceMarkers": list(profile.workspace_markers),
        "detectedRoutingMarkers": list(profile.routing_markers),
    }
    return f"{json.dumps(manifest, indent=2)}\n"


def _components_markdown(components: tuple[str, ...]) -> str:
    if not components:
        return "- No package or runtime component manifests detected."
    return "\n".join(f"- `{component}`" for component in components)


def _workspace_markers_markdown(markers: tuple[str, ...]) -> str:
    if not markers:
        return "- No workspace or monorepo orchestration markers detected."
    return "\n".join(f"- `{marker}`" for marker in markers)


def _routing_markers_markdown(markers: tuple[str, ...]) -> str:
    if not markers:
        return "- No CI, devcontainer, harness, or agent routing markers detected."
    return "\n".join(f"- `{marker}`" for marker in markers)


def _feature_list_schema() -> str:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Repo Harness Feature List",
        "type": "object",
        "required": ["features"],
        "properties": {
            "$schema": {"type": "string"},
            "project": {"type": "string"},
            "last_updated": {"type": "string"},
            "rules": {"type": "object"},
            "status_legend": {"type": "object"},
            "features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "priority",
                        "area",
                        "title",
                        "user_visible_behavior",
                        "status",
                        "verification",
                        "evidence",
                    ],
                    "properties": {
                        "id": {"type": "string"},
                        "priority": {"type": "integer"},
                        "area": {"type": "string"},
                        "title": {"type": "string"},
                        "user_visible_behavior": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "active", "blocked", "passing"],
                        },
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "verification": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "evidence": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "notes": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    }
    return f"{json.dumps(schema, indent=2)}\n"
