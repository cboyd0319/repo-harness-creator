from __future__ import annotations

import json
import os
import shlex
import stat
from datetime import UTC, datetime
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

from . import __version__
from .detect import detect_project
from .models import ProjectProfile, WriteResult
from .paths import is_inside_root
from .redact import redact_local_paths

TEMPLATE_ROOT = files("harnessforge").joinpath("templates")
PLATFORM_CONTRACTS = ("cross-platform", "macos-only", "windows-only", "linux-only")
REVIEW_REQUIRED_FILES = (
    "docs/harness/change-contract.md",
    "docs/harness/feature-privacy-labels.json",
    "docs/harness/evidence-log.md",
    "docs/harness/quality-document.md",
    "docs/harness/release-controls.md",
)


def create_harness(
    target: Path,
    *,
    agent_file: str = "AGENTS.md",
    force: bool = False,
    dry_run: bool = False,
    package_manager: str | None = None,
    commands: tuple[str, ...] = (),
    project_name: str | None = None,
    with_ci_workflow: bool = False,
    with_self_heal_workflow: bool = False,
    platform_contract: str = "cross-platform",
) -> tuple[ProjectProfile, tuple[WriteResult, ...]]:
    agent_file = _validate_agent_file(agent_file)
    platform_contract = _validate_platform_contract(platform_contract)
    profile = detect_project(
        target,
        explicit_package_manager=package_manager,
        explicit_commands=commands,
    )
    context = _template_context(
        profile,
        agent_file=agent_file,
        project_name=project_name,
        platform_contract=platform_contract,
    )
    specs = _template_specs(
        agent_file,
        with_ci_workflow=with_ci_workflow,
        with_self_heal_workflow=with_self_heal_workflow,
        platform_contract=platform_contract,
    )
    _validate_destinations(profile.root, tuple(spec[1] for spec in specs))
    rendered = _render_harness_files(specs, context)
    generated_files = _generated_file_metadata(specs, rendered)
    results: list[WriteResult] = []
    for template_name, relative_path, executable in specs:
        destination = profile.root / relative_path
        if template_name == "manifest.json.tmpl":
            content = _manifest_content(
                profile,
                agent_file,
                with_ci_workflow=with_ci_workflow,
                with_self_heal_workflow=with_self_heal_workflow,
                platform_contract=platform_contract,
                generated_files=generated_files,
            )
        else:
            content = rendered[relative_path]
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


def _template_specs(
    agent_file: str,
    *,
    with_ci_workflow: bool = False,
    with_self_heal_workflow: bool = False,
    platform_contract: str = "cross-platform",
) -> tuple[tuple[str, str, bool], ...]:
    platform = _platform_contract_data(platform_contract)
    specs = [
        ("agents.md.tmpl", agent_file, False),
    ]
    if agent_file != "CLAUDE.md":
        specs.append(("claude.md.tmpl", "CLAUDE.md", False))
    if agent_file != "GEMINI.md":
        specs.append(("gemini.md.tmpl", "GEMINI.md", False))
    specs.extend(
        [
            (
                "copilot-instructions.md.tmpl",
                ".github/copilot-instructions.md",
                False,
            ),
            ("feature-list.json.tmpl", "feature_list.json", False),
            (
                "feature-list.schema.json.tmpl",
                "docs/harness/feature-list.schema.json",
                False,
            ),
            ("progress.md.tmpl", "progress.md", False),
            ("session-handoff.md.tmpl", "session-handoff.md", False),
            ("check-pins.py.tmpl", "scripts/check_pins.py", True),
            ("harness-readme.md.tmpl", "docs/harness/README.md", False),
            ("change-contract.md.tmpl", "docs/harness/change-contract.md", False),
            ("verification-matrix.md.tmpl", "docs/harness/verification-matrix.md", False),
            ("component-inventory.md.tmpl", "docs/harness/component-inventory.md", False),
            (
                "dependency-change-policy.md.tmpl",
                "docs/harness/dependency-change-policy.md",
                False,
            ),
            (
                "security-boundary-map.md.tmpl",
                "docs/harness/security-boundary-map.md",
                False,
            ),
            (
                "feature-privacy-labels.json.tmpl",
                "docs/harness/feature-privacy-labels.json",
                False,
            ),
            ("evidence-log.md.tmpl", "docs/harness/evidence-log.md", False),
            (
                "clean-state-checklist.md.tmpl",
                "docs/harness/clean-state-checklist.md",
                False,
            ),
            ("evaluator-rubric.md.tmpl", "docs/harness/evaluator-rubric.md", False),
            ("quality-document.md.tmpl", "docs/harness/quality-document.md", False),
            ("release-controls.md.tmpl", "docs/harness/release-controls.md", False),
            ("self-healing.md.tmpl", "docs/harness/self-healing.md", False),
            ("research-sources.json.tmpl", "docs/harness/research-sources.json", False),
            ("research-inbox.md.tmpl", "docs/harness/research-inbox.md", False),
            (
                "agent-operating-model.md.tmpl",
                "docs/harness/agent-operating-model.md",
                False,
            ),
            (
                "multi-agent-orchestration.md.tmpl",
                "docs/harness/multi-agent-orchestration.md",
                False,
            ),
            ("entropy-control.md.tmpl", "docs/harness/entropy-control.md", False),
            ("sources.md.tmpl", "docs/harness/sources.md", False),
            ("manifest.json.tmpl", "docs/harness/manifest.json", False),
        ]
    )
    insert_at = next(
        index
        for index, spec in enumerate(specs)
        if spec[1] == "docs/harness/README.md"
    )
    entrypoint_specs: list[tuple[str, str, bool]] = []
    if platform["requires_posix"]:
        entrypoint_specs.append(("init.sh.tmpl", "init.sh", True))
    if platform["requires_powershell"]:
        entrypoint_specs.append(("init.ps1.tmpl", "init.ps1", False))
    specs[insert_at:insert_at] = entrypoint_specs
    if with_ci_workflow:
        specs.append(("ci-workflow.yml.tmpl", ".github/workflows/harnessforge.yml", False))
    if with_self_heal_workflow:
        specs.append(
            (
                "self-heal-workflow.yml.tmpl",
                ".github/workflows/harness-self-heal.yml",
                False,
            )
        )
    return tuple(specs)


def _self_heal_git_add_paths(agent_file: str, platform_contract: str) -> str:
    platform = _platform_contract_data(platform_contract)
    paths = [agent_file]
    if agent_file != "CLAUDE.md":
        paths.append("CLAUDE.md")
    if agent_file != "GEMINI.md":
        paths.append("GEMINI.md")
    paths.extend(
        [
            ".github/copilot-instructions.md",
            "feature_list.json",
            "progress.md",
            "session-handoff.md",
            "scripts/check_pins.py",
            "docs/harness",
            ".github/workflows/harness-self-heal.yml",
        ]
    )
    if platform["requires_posix"]:
        paths.insert(-3, "init.sh")
    if platform["requires_powershell"]:
        paths.insert(-3, "init.ps1")
    return " \\\n            ".join(shlex.quote(path) for path in paths)


def _validate_platform_contract(platform_contract: str) -> str:
    value = platform_contract.strip().lower()
    if value not in PLATFORM_CONTRACTS:
        allowed = ", ".join(PLATFORM_CONTRACTS)
        raise ValueError(f"--platform-contract must be one of: {allowed}")
    return value


def _platform_contract_data(platform_contract: str) -> dict[str, object]:
    if platform_contract == "macos-only":
        return {
            "requires_posix": True,
            "requires_powershell": False,
            "summary": "macOS 15+ only with Python 3.13+.",
            "supported": {
                "macosOnly": {
                    "python": "3.13+",
                    "macOS": "15+",
                    "note": "Windows and Linux are not supported by this harness contract.",
                }
            },
        }
    if platform_contract == "windows-only":
        return {
            "requires_posix": False,
            "requires_powershell": True,
            "summary": "Windows 11+ only with Python 3.13+.",
            "supported": {
                "windowsOnly": {
                    "python": "3.13+",
                    "windows": "11+",
                    "note": "macOS and Linux are not supported by this harness contract.",
                }
            },
        }
    if platform_contract == "linux-only":
        return {
            "requires_posix": True,
            "requires_powershell": False,
            "summary": "Ubuntu 22.04+ Linux floor with Python 3.13+.",
            "supported": {
                "linuxOnly": {
                    "python": "3.13+",
                    "linux": "Ubuntu 22.04+ floor",
                    "note": "macOS and Windows are not supported by this harness contract.",
                }
            },
        }
    return {
        "requires_posix": True,
        "requires_powershell": True,
        "summary": (
            "Python 3.13+, macOS 15+, Windows 11+, Ubuntu 22.04+, and "
            "best-effort support for other modern Linux distributions with "
            "Python 3.13+."
        ),
        "supported": {
            "python": "3.13+",
            "macOS": "15+",
            "windows": "11+",
            "linux": "Ubuntu 22.04+ floor; other modern distributions are best effort",
        },
    }


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
    profile: ProjectProfile,
    *,
    agent_file: str,
    project_name: str | None,
    platform_contract: str,
) -> dict[str, str]:
    now = datetime.now(UTC).date().isoformat()
    commands = profile.verification_commands
    platform = _platform_contract_data(platform_contract)
    return {
        "agent_file": agent_file,
        "agent_file_yaml": json.dumps(agent_file),
        "platform_contract": platform_contract,
        "platform_contract_summary": str(platform["summary"]),
        "project_name": project_name or profile.name,
        "detected_stack": profile.stack,
        "languages": ", ".join(profile.languages),
        "package_managers": ", ".join(profile.package_managers) or "none detected",
        "runtime_files": ", ".join(profile.runtime_files) or "none detected",
        "self_heal_git_add_paths": _self_heal_git_add_paths(
            agent_file, platform_contract
        ),
        "self_heal_verify_command": _self_heal_verify_command(platform_contract),
        "components_markdown": _components_markdown(profile.components),
        "workspace_markers_markdown": _workspace_markers_markdown(
            profile.workspace_markers
        ),
        "routing_markers_markdown": _routing_markers_markdown(
            profile.routing_markers
        ),
        "generated_date": now,
        "commands_markdown": "\n".join(f"- `{command}`" for command in commands),
        "verification_entrypoints_markdown": _verification_entrypoints_markdown(
            platform_contract
        ),
        "commands_shell": "\n\n".join(_shell_command_block(command) for command in commands),
        "commands_powershell": "\n\n".join(
            _powershell_command_block(command) for command in commands
        ),
    }


def _verification_entrypoints_markdown(platform_contract: str) -> str:
    platform = _platform_contract_data(platform_contract)
    blocks: list[str] = []
    if platform["requires_posix"]:
        blocks.append(
            "Full local verification on macOS or Linux:\n\n"
            "```bash\n"
            "./init.sh\n"
            "```"
        )
    if platform["requires_powershell"]:
        blocks.append(
            "Full local verification on Windows:\n\n"
            "```powershell\n"
            ".\\init.ps1\n"
            "```"
        )
    return "\n\n".join(blocks)


def _self_heal_verify_command(platform_contract: str) -> str:
    platform = _platform_contract_data(platform_contract)
    if platform["requires_posix"]:
        return "./init.sh"
    return "pwsh -NoProfile -File ./init.ps1"


def _render_harness_files(
    specs: tuple[tuple[str, str, bool], ...], context: dict[str, str]
) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for template_name, relative_path, _ in specs:
        if template_name == "manifest.json.tmpl":
            continue
        if template_name == "feature-list.schema.json.tmpl":
            content = _feature_list_schema()
        else:
            content = _render_template(template_name, context)
        rendered[relative_path] = redact_local_paths(content)
    return rendered


def _generated_file_metadata(
    specs: tuple[tuple[str, str, bool], ...], rendered: dict[str, str]
) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    for template_name, relative_path, executable in specs:
        entry: dict[str, object] = {
            "ownership": "generated",
            "template": template_name,
            "templateSha256": _template_sha256(template_name),
            "executable": executable,
            "reviewRequired": relative_path in REVIEW_REQUIRED_FILES,
        }
        if relative_path in rendered:
            entry["contentSha256"] = _sha256_text(rendered[relative_path])
        metadata[relative_path] = entry
    return metadata


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _template_sha256(template_name: str) -> str:
    if template_name == "feature-list.schema.json.tmpl":
        return _sha256_text(_feature_list_schema())
    if template_name == "manifest.json.tmpl":
        return _sha256_text("harnessforge dynamic manifest v1")
    return sha256(
        TEMPLATE_ROOT.joinpath(template_name).read_bytes()
    ).hexdigest()


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
        return f"Invoke-Native $PythonBin {python_args}".rstrip()
    if command == "./gradlew" or command.startswith("./gradlew "):
        args = command.removeprefix("./gradlew").strip()
        suffix = f" {args}" if args else ""
        return (
            "if (Test-Path '.\\gradlew.bat') { "
            f"Invoke-Native '.\\gradlew.bat'{suffix} "
            "} elseif (Test-Path '.\\gradlew') { "
            f"Invoke-Native '.\\gradlew'{suffix} "
            "} else { throw 'Gradle wrapper not found' }"
        )
    simple = _simple_powershell_command(command)
    if simple is not None:
        return simple
    return command


def _python_command_args(command: str) -> str | None:
    for executable in ("python", "python3"):
        if command == executable:
            return ""
        prefix = f"{executable} "
        if command.startswith(prefix):
            return command.removeprefix(prefix).strip()
    return None


def _simple_powershell_command(command: str) -> str | None:
    if any(character in command for character in "\n\r|&;<>(){}[]`$"):
        return None
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    if not parts:
        return None
    quoted = " ".join(_powershell_single_quote(part) for part in parts)
    return f"Invoke-Native {quoted}"


def _powershell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _manifest_content(
    profile: ProjectProfile,
    agent_file: str,
    *,
    with_ci_workflow: bool = False,
    with_self_heal_workflow: bool = False,
    platform_contract: str = "cross-platform",
    generated_files: dict[str, dict[str, object]] | None = None,
) -> str:
    platform = _platform_contract_data(platform_contract)
    required_files = [
        agent_file,
        *([] if agent_file == "CLAUDE.md" else ["CLAUDE.md"]),
        *([] if agent_file == "GEMINI.md" else ["GEMINI.md"]),
        ".github/copilot-instructions.md",
        "feature_list.json",
        "progress.md",
        "session-handoff.md",
        "scripts/check_pins.py",
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
        "docs/harness/release-controls.md",
        "docs/harness/self-healing.md",
        "docs/harness/research-sources.json",
        "docs/harness/research-inbox.md",
        "docs/harness/manifest.json",
        "docs/harness/sources.md",
        "docs/harness/entropy-control.md",
        "docs/harness/agent-operating-model.md",
        "docs/harness/multi-agent-orchestration.md",
        "docs/harness/feature-list.schema.json",
    ]
    if platform["requires_posix"]:
        required_files.insert(required_files.index("docs/harness/README.md"), "init.sh")
    if platform["requires_powershell"]:
        required_files.insert(required_files.index("docs/harness/README.md"), "init.ps1")
    required_snippets: dict[str, list[str]] = {
        agent_file: [
            "Startup",
            "Build and test commands",
            "Definition Of Done",
            "feature_list.json",
            "progress.md",
            "remote CI",
            "stubbed",
        ],
        ".github/copilot-instructions.md": [
            "source of truth",
            agent_file,
            "Security boundary map",
        ],
        "docs/harness/README.md": [
            "Operating Loop",
            "When To Add Harness",
            "Assessment And Updates",
            "project-owned generated files",
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
            "Remote CI",
            "AI/RAG/agent",
            "Agent-generated tests",
            "stubbed",
            "intentionally vulnerable",
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
            "pins.toml",
            "GitHub Actions",
        ],
        "docs/harness/security-boundary-map.md": [
            "Harness Surface Boundaries",
            "Access Boundaries",
            "Data Boundaries",
            "Required Checks",
            "security wins",
            "GitHub Action",
            "machine-local absolute paths",
            "fixed allowlist",
            "prompt injection",
            "data poisoning",
            "Workflow surfaces",
            "least privilege",
            "human approval",
            "cost-incurring",
            "Verification commands",
            "intentionally vulnerable",
            "Threat model",
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
            "high-signal defects",
            "test integrity",
        ],
        "docs/harness/quality-document.md": [
            "Quality Document",
            "Domain Grades",
            "Harness Simplification",
        ],
        "docs/harness/release-controls.md": [
            "Release Controls",
            "Manual platform",
            "SBOM",
            "provenance",
            "isolated directory",
            "Rollback",
        ],
        "docs/harness/self-healing.md": [
            "Self-healing must be reviewable",
            "fixed allowlist",
            "prompt injection",
            "invisible Unicode",
            "Workflow Boundary",
            "HarnessForge Action",
            "Safe Loop",
            "Promotion Rule",
        ],
        "docs/harness/research-sources.json": [
            "openai-harness-engineering",
            "walkinglabs-course",
            "github-actions-secure-use",
            "owasp-ai-agent-security-cheat-sheet",
            "owasp-mcp-security-cheat-sheet",
            "owasp-security-shepherd",
            "owasp-pytm",
            "owasp-samm",
            "owasp-rag-security-cheat-sheet",
            "owasp-secure-coding-with-ai-cheat-sheet",
            "owasp-llm-top-10",
            "owasp-agentic-applications-top-10",
            "owasp-agentic-skills-top-10",
            "openai-ai-native-engineering",
            "microsoft-agt-prompt-injection-benchmark",
            "pnpm-workspaces",
            "github-actions-workflow-syntax",
            "terraform-standard-module-structure",
        ],
        "docs/harness/agent-operating-model.md": [
            "Delegate",
            "Review",
            "Own",
            "GitHub Action behavior",
            "least privilege",
            "human approval",
            "verification commands",
            "project checkpoints",
            "push",
            "intentionally vulnerable",
        ],
        "docs/harness/research-inbox.md": [
            "Research Inbox",
            "review signals",
            "Promotion checklist",
        ],
        "docs/harness/entropy-control.md": [
            "Promotion Rules",
            "Evidence Rules",
            "Stop Conditions",
        ],
        "scripts/check_pins.py": [
            "40-char SHA",
            "--strict",
            "pins.toml",
            "tomllib",
            "unexpected build hook",
            "container base image",
            "Python requirement",
            "package-lock entry",
            "profile image",
        ],
    }
    if agent_file != "CLAUDE.md":
        required_snippets["CLAUDE.md"] = [
            f"@{agent_file}",
            "Claude Code",
            "Shared repo guidance",
        ]
    if agent_file != "GEMINI.md":
        required_snippets["GEMINI.md"] = [
            f"@{agent_file}",
            "Gemini",
            "Shared repo guidance",
        ]
    if with_ci_workflow:
        required_files.append(".github/workflows/harnessforge.yml")
        required_snippets[".github/workflows/harnessforge.yml"] = [
            "workflow_dispatch",
            "cancel-in-progress: true",
            "persist-credentials: false",
            "harnessforge@<reviewed-commit-sha>",
        ]
    if with_self_heal_workflow:
        required_files.append(".github/workflows/harness-self-heal.yml")
        required_snippets[".github/workflows/harness-self-heal.yml"] = [
            "workflow_dispatch",
            "contents: write",
            "pull-requests: write",
            "apply",
            "agent-file:",
            agent_file,
            "git add --",
            ".github/copilot-instructions.md",
            "gh pr create",
        ]
    manifest = {
        "version": 1,
        "generatedBy": "harnessforge",
        "generator": {
            "name": "harnessforge",
            "version": __version__,
        },
        "generatedFor": profile.name,
        "detectedStack": profile.stack,
        "platformContract": platform_contract,
        "supportedPlatforms": platform["supported"],
        "requiredFiles": required_files,
        "requiredHarnessSnippets": required_snippets,
        "generatedFiles": generated_files or {},
        "reviewRequired": list(REVIEW_REQUIRED_FILES),
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
        "title": "HarnessForge Feature List",
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
