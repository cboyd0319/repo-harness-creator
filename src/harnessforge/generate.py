from __future__ import annotations

import json
import os
import shlex
import stat
from datetime import UTC, datetime
from hashlib import sha256
from html import escape as html_escape
from importlib.resources import files
from pathlib import Path

from . import __version__
from .detect import MISSING_VERIFICATION_COMMAND, detect_project
from .models import ProjectProfile, WriteResult
from .paths import is_inside_root
from .redact import redact_local_paths

TEMPLATE_ROOT = files("harnessforge").joinpath("templates")
PLATFORM_CONTRACTS = ("cross-platform", "macos-only", "windows-only", "linux-only")
REVIEW_REQUIRED_FILES = (
    "docs/harness/change-contract.md",
    "docs/harness/feature-privacy-labels.json",
    "docs/harness/evidence-log.md",
    "docs/harness/first-agent-task.md",
    "docs/harness/quality-document.md",
    "docs/harness/release-controls.md",
    "docs/harness/roadmap.md",
    "docs/harness/sensor-registry.md",
    "docs/harness/source-record-example.json",
)
PLATFORM_SOURCE_REVIEW_DATE = "2026-06-15"
PLATFORM_SOURCE_REVIEW = (
    {
        "id": "python-devguide-versions",
        "url": "https://devguide.python.org/versions/",
        "evidence": "Python 3.13 and 3.14 are supported bugfix branches.",
    },
    {
        "id": "github-actions-hosted-runners",
        "url": "https://docs.github.com/en/actions/reference/runners/github-hosted-runners",
        "evidence": (
            "GitHub documents ubuntu-22.04, macos-15, windows-2025, "
            "and windows-2025-vs2026 hosted-runner labels."
        ),
    },
    {
        "id": "github-runner-images-windows-vs2026",
        "url": "https://github.com/actions/runner-images/issues/14017",
        "evidence": (
            "GitHub announced the June 8-15, 2026 migration of "
            "windows-2025 to the Visual Studio 2026 image."
        ),
    },
)


def create_harness(
    target: Path,
    *,
    agent_file: str = "AGENTS.md",
    force: bool = False,
    enhance_existing: bool = False,
    dry_run: bool = False,
    package_manager: str | None = None,
    commands: tuple[str, ...] = (),
    project_name: str | None = None,
    with_ci_workflow: bool = False,
    with_self_heal_workflow: bool = False,
    platform_contract: str = "cross-platform",
    update_generated_paths: frozenset[str] = frozenset(),
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
    generated_files = _generated_file_metadata(
        profile.root,
        specs,
        rendered,
        force=force,
        enhance_existing=enhance_existing,
        update_generated_paths=update_generated_paths,
        agent_file=agent_file,
        project_context_markdown=context["project_context_markdown"],
    )
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
                relative_path=relative_path,
                agent_file=agent_file,
                project_context_markdown=context["project_context_markdown"],
                executable=executable,
                force=force,
                enhance_existing=enhance_existing,
                update_generated=relative_path in update_generated_paths,
                dry_run=dry_run,
            )
        )
    if enhance_existing:
        spec_paths = {relative_path for _, relative_path, _ in specs}
        results.extend(
            _enhance_existing_instruction_files(
                profile.root,
                agent_file=agent_file,
                skip_paths=spec_paths,
                project_context_markdown=context["project_context_markdown"],
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
            ("first-agent-task.md.tmpl", "docs/harness/first-agent-task.md", False),
            ("roadmap.md.tmpl", "docs/harness/roadmap.md", False),
            ("change-contract.md.tmpl", "docs/harness/change-contract.md", False),
            ("verification-matrix.md.tmpl", "docs/harness/verification-matrix.md", False),
            ("sensor-registry.md.tmpl", "docs/harness/sensor-registry.md", False),
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
            (
                "source-record.schema.json.tmpl",
                "docs/harness/source-record.schema.json",
                False,
            ),
            (
                "source-record-example.json.tmpl",
                "docs/harness/source-record-example.json",
                False,
            ),
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
        "agent_file_usage_note": _agent_file_usage_note(agent_file),
        "agent_file_yaml": json.dumps(agent_file),
        "platform_contract": platform_contract,
        "platform_contract_summary": str(platform["summary"]),
        "platform_source_review_markdown": _platform_source_review_markdown(),
        "project_name": project_name or profile.name,
        "detected_stack": profile.stack,
        "languages": ", ".join(profile.languages),
        "package_managers": ", ".join(profile.package_managers) or "none detected",
        "runtime_files": ", ".join(profile.runtime_files) or "none detected",
        "project_context_markdown": _project_context_markdown(profile),
        "self_heal_git_add_paths": _self_heal_git_add_paths(
            agent_file, platform_contract
        ),
        "self_heal_verify_command": _self_heal_verify_command(platform_contract),
        "components_markdown": _components_markdown(profile),
        "workspace_markers_markdown": _workspace_markers_markdown(
            profile.workspace_markers
        ),
        "routing_markers_markdown": _routing_markers_markdown(
            profile.routing_markers
        ),
        "generated_date": now,
        "commands_markdown": "\n".join(f"- `{command}`" for command in commands),
        "sensor_rows_markdown": _sensor_rows_markdown(commands),
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


def _platform_source_review_markdown() -> str:
    source_ids = ", ".join(source["id"] for source in PLATFORM_SOURCE_REVIEW)
    return (
        f"- Last HarnessForge platform source review: {PLATFORM_SOURCE_REVIEW_DATE}.\n"
        "- Before changing platform floors, interpreter versions, runner labels, "
        "or CI image assumptions, record current primary-source evidence and "
        "the review date in `docs/harness/evidence-log.md`.\n"
        f"- Recheck source IDs: {source_ids}."
    )


def _self_heal_verify_command(platform_contract: str) -> str:
    platform = _platform_contract_data(platform_contract)
    if platform["requires_posix"]:
        return "./init.sh"
    return "pwsh -NoProfile -File ./init.ps1"


def _agent_file_usage_note(agent_file: str) -> str:
    if agent_file == "AGENTS.md":
        return ""
    return (
        "\nThis file is a side-by-side HarnessForge entrypoint, not the default "
        "`AGENTS.md`. Configure your coding agent to load this file directly, or "
        "add a reviewed router from the existing canonical instruction file "
        "before relying on it.\n"
    )


def _project_context_markdown(profile: ProjectProfile) -> str:
    signals: list[str] = []
    component_paths = {
        component.split(" (", 1)[0]
        for component in profile.components
        if " (" in component
    }
    component_text = "\n".join(profile.components)
    languages = set(profile.languages)
    package_managers = set(profile.package_managers)
    runtime_files = set(profile.runtime_files)
    routing_markers = set(profile.routing_markers)
    workspace_markers = set(profile.workspace_markers)
    command_text = "\n".join(profile.verification_commands).lower()
    if profile.component_scan_truncated:
        signals.append(
            "- Component inventory reached the generated "
            f"{profile.component_scan_limit}-component limit. Run "
            "`harnessforge index --target . --max-files <N>` and add important\n"
            "  omitted boundaries to `docs/harness/component-inventory.md` "
            "before broad changes."
        )
    if profile.stack == "rust" or "rust" in profile.languages:
        signals.append(
            "- Rust workspace or crate detected. Treat `Cargo.toml`, "
            "`Cargo.lock`, and `rust-toolchain.toml` as primary build and\n"
            "  reproducibility inputs when present."
        )
    if profile.stack == "swift" or "swift" in languages:
        signals.append(
            "- Swift Package Manager surface detected. Treat `Package.swift`, "
            "`Package.resolved`, Xcode toolchain selection, and Apple platform\n"
            "  availability as build-contract inputs."
        )
    if profile.stack == "python" or "python" in languages:
        signals.append(
            "- Python surface detected. Inspect `pyproject.toml`, lockfiles, "
            "test configuration, and the nearest package boundary before\n"
            "  choosing Python checks."
        )
    if profile.stack == "bazel" or "bazel" in profile.languages:
        signals.append(
            "- Bazel markers detected. Inspect `MODULE.bazel`, `WORKSPACE`, "
            "`BUILD.bazel`, and related `tools/` rules before changing Bazel\n"
            "  routing or build-system behavior."
        )
    if profile.stack == "bazel" and {"java", "cpp", "starlark"} & set(
        profile.languages
    ):
        signals.append(
            "- Mixed Bazel implementation surfaces detected. Identify whether "
            "the change is Java, C/C++, Starlark, tests, tooling, or docs\n"
            "  before choosing verification."
        )
    if {".bazelrc", ".bazelversion"} & routing_markers:
        signals.append(
            "- Bazel runtime routing files detected. Treat `.bazelrc` and "
            "`.bazelversion` changes as shared build-contract changes."
        )
    if "structured project specs" in workspace_markers | routing_markers:
        signals.append(
            "- Structured project specs detected. Treat architecture, security, "
            "operations, UX, and work-item docs as planning or source-of-truth\n"
            "  surfaces when the target repo already uses them."
        )
    if "Spec Kit SDD" in workspace_markers | routing_markers:
        signals.append(
            "- Spec Kit-style SDD surfaces detected. Treat `.specify/`, "
            "`.specify/memory/constitution.md`, `.specify/feature.json`, and\n"
            "  `specs/` feature artifacts as existing repo-owned source-of-truth "
            "systems."
        )
    if any(path.startswith("third_party") for path in component_paths):
        signals.append(
            "- `third_party/` or vendored components detected. Treat them as "
            "dependency, fixture, or external-input boundaries unless the\n"
            "  task explicitly targets them."
        )
    if any(path.startswith("scripts/release") for path in component_paths) or any(
        path.startswith("scripts/packages") for path in component_paths
    ):
        signals.append(
            "- Release or package scripts detected. Treat release automation, "
            "publishing, signing, and packaging behavior as review-sensitive."
        )
    if any(path.startswith(("docs", "site", "scripts/docs")) for path in component_paths):
        signals.append(
            "- Documentation or site-generation surfaces detected. Inspect the "
            "nearest docs build targets before changing generated docs or\n"
            "  published site content."
        )
    elif profile.stack == "docs" or "docs" in languages:
        signals.append(
            "- Documentation or catalog repository detected. Treat README files, "
            "contribution rules, figures, tables, and external links as the\n"
            "  main product surface; use a repo-owned link or format check when "
            "one exists."
        )
    if "terraform" in languages:
        signals.append(
            "- Terraform or infrastructure files detected. Treat provider, "
            "state, secret, cost, and environment changes as review-sensitive."
        )
    if "cpp" in languages and not (
        profile.stack == "bazel" and {"java", "cpp", "starlark"} & languages
    ):
        signals.append(
            "- C/C++ or native-code files detected. Inspect compiler, linker, "
            "platform, packaging, and fixture boundaries before choosing\n"
            "  validation."
        )
    if "dotnet" in languages:
        signals.append(
            "- .NET solution or project files detected. Treat `.sln`, `.slnx`, "
            "`.csproj`, `.fsproj`, and `global.json` as build-contract inputs."
        )
    if "php" in languages:
        signals.append(
            "- PHP or Composer surface detected. Inspect `composer.json`, "
            "`composer.lock`, framework config, and test scripts before\n"
            "  changing runtime behavior."
        )
    if "ruby" in languages:
        signals.append(
            "- Ruby or Bundler surface detected. Inspect `Gemfile`, lockfiles, "
            "Rake tasks, and framework config before changing runtime behavior."
        )
    if "shell" in languages:
        signals.append(
            "- Shell entrypoints detected. Quote paths, preserve spaces, use "
            "strict error handling, and run syntax or harness checks before\n"
            "  claiming shell behavior is safe."
        )
    if "Dockerfile" in component_text or "Containerfile" in component_text or {
        "Dockerfile",
        "Containerfile",
    } & runtime_files:
        signals.append(
            "- Container image definitions detected. Treat base images, build "
            "context, network access, mounted secrets, and published tags as\n"
            "  security-sensitive."
        )
    if any(path == "src-tauri" or path.startswith("src-tauri/") for path in component_paths):
        signals.append(
            "- Tauri desktop surface detected. Coordinate frontend, Rust, "
            "packaging, platform permissions, and updater behavior together."
        )
    if "Cargo.toml [workspace]" in profile.workspace_markers:
        signals.append(
            "- Cargo workspace members are component boundaries. Prefer scoped "
            "crate checks first,\n"
            "  then workspace checks for shared behavior."
        )
    if "just" in package_managers or "justfile" in routing_markers | runtime_files:
        signals.append(
            "- Repository task runner detected. Inspect `justfile` targets and "
            "prefer the project-provided aggregate check when it exists."
        )
    if {"npm", "pnpm", "yarn", "bun"} & package_managers:
        signals.append(
            "- JavaScript or TypeScript subprojects are present. Inspect the "
            "nearest `package.json`\n"
            "  scripts before choosing Node-based checks."
        )
    elif {"javascript", "typescript"} & languages:
        signals.append(
            "- JavaScript or TypeScript files detected without a package manager "
            "marker. Treat them as templates, examples, docs assets, or\n"
            "  secondary scripts until a package boundary is confirmed."
        )
    if {"maven", "gradle"} & package_managers:
        signals.append(
            "- JVM build surfaces are present. Inspect the nearest `pom.xml`, "
            "`build.gradle`, or\n"
            "  `build.gradle.kts` before changing Java or plugin behavior."
        )
    if "go" in package_managers:
        signals.append(
            "- Go module surfaces are present. Treat nested `go.mod` files as "
            "separate module\n"
            "  boundaries."
        )
    if "agent skills" in routing_markers:
        signals.append(
            "- Agent skill surfaces detected. Treat `SKILL.md` frontmatter, "
            "trigger descriptions, bundled scripts, assets, and examples as\n"
            "  agent-control surfaces; review tool assumptions before changing "
            "or distributing them."
        )
    if {".claude-plugin", ".codex-plugin"} & routing_markers:
        signals.append(
            "- Agent plugin manifests detected. Review marketplace metadata, "
            "packaged skills, install commands, and distribution scope before\n"
            "  changing plugin behavior."
        )
    if (
        "gen-docs" in command_text
        or "docs-check" in command_text
        or "docgen" in component_text.lower()
    ):
        signals.append(
            "- Generated documentation checks detected. Treat generated docs as "
            "code-owned artifacts and run the documented drift check after\n"
            "  changing schemas, tool definitions, CLIs, or docs generators."
        )
    if "action.yml" in routing_markers or "action.yaml" in routing_markers:
        signals.append(
            "- GitHub Action surface detected. Changes to `action.yml` or "
            "workflow behavior are\n"
            "  release and security-sensitive."
        )
    if ".github/workflows" in routing_markers:
        workflow_details = []
        if ".github/workflows path filters" in routing_markers:
            workflow_details.append("path filters")
        if ".github/workflows working-directory" in routing_markers:
            workflow_details.append("`working-directory` routing")
        if ".github/actions" in routing_markers:
            workflow_details.append("local Actions")
        detail = (
            f" Existing workflow metadata includes {', '.join(workflow_details)}."
            if workflow_details
            else ""
        )
        signals.append(
            "- Existing GitHub workflow surfaces detected. Review triggers, "
            "permissions, matrix coverage, environment use, and generated\n"
            f"  workflow boundaries before changing CI.{detail}"
        )
    if ".devcontainer" in routing_markers:
        signals.append(
            "- Devcontainer configuration detected. Treat container images, "
            "features, mounts, secrets, and setup commands as environment\n"
            "  contract inputs."
        )
    root_agent_markers = tuple(
        marker
        for marker in (
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            ".github/copilot-instructions.md",
        )
        if marker in routing_markers
    )
    if root_agent_markers:
        signals.append(
            "- Existing root agent instruction files detected: "
            f"{', '.join(f'`{marker}`' for marker in root_agent_markers)}. "
            "Preserve project-owned text and keep durable rules in\n"
            "  the canonical instruction surface after review."
        )
    hidden_agent_markers = tuple(
        marker
        for marker in profile.routing_markers
        if marker.startswith((".claude/", ".gemini/"))
    )
    if hidden_agent_markers:
        signals.append(
            "- Existing hidden agent instruction files detected: "
            f"{', '.join(f'`{marker}`' for marker in hidden_agent_markers)}. "
            "Keep them as\n"
            "  short routers or project overlays after reviewing "
            "the canonical root instructions."
        )
    if not signals:
        return "- No stack-specific context beyond the detected files."
    return "\n".join(signals)


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
    root: Path,
    specs: tuple[tuple[str, str, bool], ...],
    rendered: dict[str, str],
    *,
    force: bool,
    enhance_existing: bool,
    update_generated_paths: frozenset[str],
    agent_file: str,
    project_context_markdown: str,
) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    for template_name, relative_path, executable in specs:
        destination = root / relative_path
        update_generated = relative_path in update_generated_paths
        existing_project_file = destination.exists() and not force and not update_generated
        enhanced_content = None
        if existing_project_file and enhance_existing:
            enhanced_content = _enhanced_instruction_content(
                root,
                destination,
                relative_path=relative_path,
                agent_file=agent_file,
                project_context_markdown=project_context_markdown,
            )
        enhanced = enhanced_content is not None
        entry: dict[str, object] = {
            "ownership": (
                "project-enhanced"
                if enhanced
                else "project"
                if existing_project_file
                else "generated"
            ),
            "template": template_name,
            "templateSha256": _template_sha256(template_name),
            "executable": executable,
            "reviewRequired": relative_path in REVIEW_REQUIRED_FILES,
            "writeStatus": _generated_write_status(
                update_generated=update_generated,
                enhanced=enhanced,
                existing_project_file=existing_project_file,
            ),
        }
        if enhanced_content is not None:
            entry["contentSha256"] = _sha256_text(enhanced_content)
        elif existing_project_file:
            entry["contentSha256"] = sha256(destination.read_bytes()).hexdigest()
        elif relative_path in rendered:
            entry["contentSha256"] = _sha256_text(rendered[relative_path])
        metadata[relative_path] = entry
    return metadata


def _generated_write_status(
    *,
    update_generated: bool,
    enhanced: bool,
    existing_project_file: bool,
) -> str:
    if update_generated:
        return "updated"
    if enhanced:
        return "enhanced"
    if existing_project_file:
        return "skipped-existing"
    return "generated"


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
    relative_path: str,
    agent_file: str,
    project_context_markdown: str,
    executable: bool,
    force: bool,
    enhance_existing: bool,
    update_generated: bool,
    dry_run: bool,
) -> WriteResult:
    if not is_inside_root(path, root):
        raise ValueError(f"refusing to write outside target repository: {path}")
    if path.exists() and update_generated and not force:
        if dry_run:
            return WriteResult(
                path=path,
                status="would_update",
                reason="generated-owned template changed and file unchanged",
            )
        path.write_text(content, encoding="utf-8", newline="\n")
        if executable and os.name != "nt":
            current = path.stat().st_mode
            path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return WriteResult(
            path=path,
            status="updated",
            reason="generated-owned template changed and file unchanged",
        )
    if path.exists() and not force:
        if enhance_existing:
            enhanced = _enhanced_instruction_content(
                root,
                path,
                relative_path=relative_path,
                agent_file=agent_file,
                project_context_markdown=project_context_markdown,
            )
            if enhanced is not None:
                if dry_run:
                    return WriteResult(path=path, status="would_enhance")
                path.write_text(enhanced, encoding="utf-8", newline="\n")
                return WriteResult(path=path, status="enhanced")
        return WriteResult(path=path, status="skipped", reason="exists")
    if dry_run:
        return WriteResult(path=path, status="would_write")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    if executable and os.name != "nt":
        current = path.stat().st_mode
        path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return WriteResult(path=path, status="written")


def _enhanced_instruction_content(
    root: Path,
    path: Path,
    *,
    relative_path: str,
    agent_file: str,
    project_context_markdown: str,
) -> str | None:
    if relative_path not in _enhanceable_instruction_paths(agent_file):
        return None
    if not is_inside_root(path, root):
        return None
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    addendum = _instruction_addendum(
        relative_path,
        agent_file,
        project_context_markdown=project_context_markdown,
    )
    if not addendum or "HarnessForge Quality Addendum" in original:
        return None
    stripped = original.rstrip()
    return f"{stripped}\n\n{addendum}\n"


def _enhanceable_instruction_paths(agent_file: str) -> set[str]:
    return {
        agent_file,
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        ".claude/AGENTS.md",
        ".claude/CLAUDE.md",
        ".gemini/GEMINI.md",
        ".github/copilot-instructions.md",
    }


def _instruction_addendum(
    relative_path: str,
    agent_file: str,
    *,
    project_context_markdown: str,
) -> str:
    if relative_path == ".claude/AGENTS.md":
        canonical = f"../{agent_file}"
        return f"""<!-- HarnessForge Quality Addendum: start -->
## HarnessForge Quality Addendum

Use `{canonical}` as the canonical repo instruction file after review. Keep this
hidden Claude-specific file as a short router or local overlay.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path == ".claude/CLAUDE.md":
        canonical = f"../{agent_file}"
        return f"""<!-- HarnessForge Quality Addendum: start -->
@{canonical}

## HarnessForge Quality Addendum

Claude Code should use `{canonical}` for Shared repo guidance. Keep this hidden
file short and route durable policy to the canonical instruction file.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path == ".gemini/GEMINI.md":
        canonical = f"../{agent_file}"
        return f"""<!-- HarnessForge Quality Addendum: start -->
@{canonical}

## HarnessForge Quality Addendum

Gemini should use `{canonical}` for Shared repo guidance. Keep this hidden file
short and route durable policy to the canonical instruction file.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path in {agent_file, "AGENTS.md"}:
        return f"""<!-- HarnessForge Quality Addendum: start -->
## HarnessForge Quality Addendum

Startup path:

1. Confirm the working directory.
2. Read `{agent_file}` and `docs/harness/README.md`.
3. Read `feature_list.json`, `progress.md`, and `session-handoff.md`.
4. Check `docs/harness/roadmap.md` before selecting, deferring, or reshaping
   backlog, release-prep, or product-scope work.
5. Check `docs/harness/component-inventory.md` before changing component
   boundaries or verification routing.

Build and test commands:

- Use the smallest reliable command listed in this file,
  `docs/harness/verification-matrix.md`, or the generated init entrypoint.
- Prefer local checks before remote CI. Push or open remote CI only at an
  explicit checkpoint, release point, or user request.

Implementation discipline:

- State assumptions and tradeoffs before coding when the request is ambiguous.
- Do not build speculative features, abstractions, workflows, or dependencies.
- Prefer no change, deletion, documentation, configuration, standard library,
  native platform features, or existing dependencies before new code.
- Keep every changed line traceable to the current objective.
- Record the ceiling and upgrade path for intentional simplifications.

Definition Of Done: behavior is implemented, relevant checks ran, skipped checks
have a reason and risk, and durable state is updated.

Testing instructions: reject stubbed, assertion-free, or shortcut tests that do
not prove the changed behavior.

Detected project context:

{project_context_markdown}

End of Session: update `progress.md` and `session-handoff.md` with current
state, verification evidence, blockers, and the recommended next step.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path == "CLAUDE.md":
        return f"""<!-- HarnessForge Quality Addendum: start -->
@{agent_file}

## HarnessForge Quality Addendum

Claude Code should use `{agent_file}` for Shared repo guidance. Keep this file
short and route durable policy to the canonical instruction file.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path == "GEMINI.md":
        return f"""<!-- HarnessForge Quality Addendum: start -->
@{agent_file}

## HarnessForge Quality Addendum

Gemini should use `{agent_file}` for Shared repo guidance. Keep this file short
and route durable policy to the canonical instruction file.
<!-- HarnessForge Quality Addendum: end -->"""
    if relative_path == ".github/copilot-instructions.md":
        return f"""<!-- HarnessForge Quality Addendum: start -->
## HarnessForge Quality Addendum

Use `{agent_file}` as the source of truth for repo guidance. Read the Security
boundary map at `docs/harness/security-boundary-map.md` before
security-sensitive work.
<!-- HarnessForge Quality Addendum: end -->"""
    return ""


def _enhance_existing_instruction_files(
    root: Path,
    *,
    agent_file: str,
    skip_paths: set[str],
    project_context_markdown: str,
    dry_run: bool,
) -> list[WriteResult]:
    results: list[WriteResult] = []
    for relative_path in sorted(_enhanceable_instruction_paths(agent_file) - skip_paths):
        path = root / relative_path
        if not path.exists():
            continue
        enhanced = _enhanced_instruction_content(
            root,
            path,
            relative_path=relative_path,
            agent_file=agent_file,
            project_context_markdown=project_context_markdown,
        )
        if enhanced is None:
            continue
        if dry_run:
            results.append(WriteResult(path=path, status="would_enhance"))
            continue
        path.write_text(enhanced, encoding="utf-8", newline="\n")
        results.append(WriteResult(path=path, status="enhanced"))
    return results


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
    if _is_missing_verification_command(command):
        return (
            "echo \"REVIEW REQUIRED: No project verification check detected. "
            "Replace this placeholder with the smallest reliable project check.\" >&2\n"
            "exit 1"
        )
    python_args = _python_command_args(command)
    if python_args is not None:
        return f'"${{PYTHON_BIN}}" {python_args}'.rstrip()
    return command


def _portable_powershell_command(command: str) -> str:
    if _is_missing_verification_command(command):
        return (
            "Write-Error 'REVIEW REQUIRED: No project verification check detected. "
            "Replace this placeholder with the smallest reliable project check.'\n"
            "exit 1"
        )
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


def _is_missing_verification_command(command: str) -> bool:
    return command == MISSING_VERIFICATION_COMMAND


def _sensor_rows_markdown(commands: tuple[str, ...]) -> str:
    rows = [
        "| Sensor | Source | Purpose | Owner | Retire When | Review Cadence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for command in commands:
        if _is_missing_verification_command(command):
            source = "HarnessForge placeholder"
            purpose = "Pending replacement with the smallest reliable project check."
        else:
            source = "Detected or explicitly supplied project command"
            purpose = "Pending project-specific decision."
        rows.append(
            "| "
            f"{_markdown_code_cell(command)} | "
            f"{source} | "
            f"{purpose} | "
            "Pending owner. | "
            "Pending retirement condition. | "
            "Pending review cadence. |"
        )
    return "\n".join(rows)


def _markdown_code_cell(value: str) -> str:
    compact = " ".join(value.split())
    escaped = html_escape(compact, quote=False).replace("|", "&#124;")
    return f"<code>{escaped}</code>"


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
        "docs/harness/first-agent-task.md",
        "docs/harness/roadmap.md",
        "docs/harness/change-contract.md",
        "docs/harness/verification-matrix.md",
        "docs/harness/sensor-registry.md",
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
        "docs/harness/source-record.schema.json",
        "docs/harness/source-record-example.json",
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
            "Core harness contract",
            "effective agent",
            "Build and test commands",
            "Implementation Discipline",
            "standard library",
            "intentional simplification",
            "Definition Of Done",
            "feature_list.json",
            "progress.md",
            "roadmap",
            "remote CI",
            "stubbed",
        ],
        ".github/copilot-instructions.md": [
            "source of truth",
            agent_file,
            "Security boundary map",
        ],
        "docs/harness/README.md": [
            "Five Core Subsystems",
            "Effective Agent Boundary",
            "The model is the LLM",
            "instructions + tools + environment + state + feedback",
            "Operating Loop",
            "When To Add Harness",
            "Assessment And Updates",
            "Bottleneck And Harness Debt",
            "controlled-variable exclusion tests",
            "project-owned generated files",
            "first-agent-task.md",
            "roadmap",
            "command: sync",
            "harnessforge index",
            "harnessforge effectiveness",
            "harnessforge session",
            "harnessforge report",
            "harnessforge plan",
        ],
        "docs/harness/first-agent-task.md": [
            "First-Agent Harness Improvement Task",
            "REVIEW REQUIRED",
            "component inventory",
            "readiness signals",
            "verification matrix",
            "evidence log",
            "security boundary",
            "fresh-session test",
            "source-of-truth locale",
            "runtime and process observability",
            "Do not overwrite project-owned instructions",
            "Do not run target commands",
        ],
        "docs/harness/roadmap.md": [
            "Harness Roadmap",
            "REVIEW REQUIRED",
            "Source And Evidence Weighting",
            "Smallest Correct Work Gate",
            "Task Buckets",
            "Status Lifecycle",
            "Surface Impact Checklist",
            "Fresh-Session Test",
            "Instruction Rule Lifecycle",
            "Completion Evidence Ladder",
            "Roadmap Items",
            "Surfaces In Scope",
            "Execution Gate",
            "Done Or Retire When",
            "progress.md",
            "session-handoff.md",
        ],
        "docs/harness/change-contract.md": [
            "Problem",
            "Build Necessity Gate",
            "standard library",
            "intentional simplification",
            "Acceptance Criteria",
            "Verification",
            "Rollback",
            "current primary-source evidence",
            "runner labels",
        ],
        "docs/harness/verification-matrix.md": [
            "Change Type",
            "Required Checks",
            "When Checks Cannot Run",
            "Verification Evidence Reports",
            "harnessforge plan --target . --since HEAD",
            "harnessforge report --target .",
            "harnessforge verify --target . --json --run",
            "--json-report docs/harness/evidence/verify-<date>.json",
            "evidence ladder",
            "agent-oriented failure messages",
            "Remote CI",
            "AI/RAG/agent",
            "Agent-generated tests",
            "stubbed",
            "intentionally vulnerable",
            "does not prove real-agent effectiveness",
        ],
        "docs/harness/sensor-registry.md": [
            "Sensor Registry",
            "REVIEW REQUIRED",
            "roadmap",
            "Owner",
            "Source",
            "Purpose",
            "Retire When",
            "Agent-Oriented Failure Feedback",
            "harnessforge report",
            "does not prove real-agent effectiveness",
        ],
        "docs/harness/component-inventory.md": [
            "Component Inventory",
            "Effective Agent Boundary",
            "changes the effective agent",
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
            "target-relative report path",
            "harnessforge verify --target . --run --json-report",
            "failed, timed_out, or blocked",
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
            "system or user-flow checks",
            "high-signal defects",
            "test integrity",
            "unnecessary abstractions",
        ],
        "docs/harness/quality-document.md": [
            "Quality Document",
            "Domain Grades",
            "Harness Subsystem Health",
            "Feedback",
            "Clean-State Dimensions",
            "Complexity and scope stayed minimal",
            "Benchmark Or Task Evidence",
            "Harness Simplification",
        ],
        "docs/harness/release-controls.md": [
            "Release Controls",
            "--run --json-report",
            "owner, risk, and next action",
            "Manual platform",
            "SBOM",
            "provenance",
            "isolated directory",
            "Rollback",
            "real-agent effectiveness",
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
        "docs/harness/source-record.schema.json": [
            "HarnessForge Project Source Record",
            "targetRelativePath",
            "machine-local absolute paths",
            "docs/harness/research-sources.json",
            "harnessUsage",
        ],
        "docs/harness/source-record-example.json": [
            "source-record-example",
            "REVIEW REQUIRED",
            "docs/architecture.md",
            "harnessUsage",
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
            "Smallest Correct Change",
            "standard library",
            "intentional simplification",
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
            "Read-only sync preflight",
            "command: sync",
            "require-verify-evidence",
            "sync-exit-code",
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
        "platformSourceReview": {
            "lastReviewed": PLATFORM_SOURCE_REVIEW_DATE,
            "reviewRequiredBeforePlatformChange": True,
            "sources": [dict(source) for source in PLATFORM_SOURCE_REVIEW],
            "note": (
                "This records sources HarnessForge reviewed when generating "
                "platform guidance. Recheck current primary sources before "
                "changing platform floors, interpreter versions, runner "
                "labels, or CI image assumptions."
            ),
        },
        "requiredFiles": required_files,
        "requiredHarnessSnippets": required_snippets,
        "generatedFiles": generated_files or {},
        "reviewRequired": list(REVIEW_REQUIRED_FILES),
        "verificationCommands": list(profile.verification_commands),
        "detectedComponents": list(profile.components),
        "componentInventoryLimit": profile.component_scan_limit,
        "componentInventoryTruncated": profile.component_scan_truncated,
        "detectedWorkspaceMarkers": list(profile.workspace_markers),
        "detectedRoutingMarkers": list(profile.routing_markers),
    }
    return f"{json.dumps(manifest, indent=2)}\n"


def _components_markdown(profile: ProjectProfile) -> str:
    if not profile.components:
        return "- No package or runtime component manifests detected."
    lines = [f"- `{component}`" for component in profile.components]
    if profile.component_scan_truncated:
        lines.append(
            "- REVIEW REQUIRED: Component inventory reached the "
            f"{profile.component_scan_limit}-component detection limit. "
            "Run `harnessforge index --target . --max-files <N>` for a deeper "
            "structural map and add important omitted boundaries manually."
        )
    return "\n".join(lines)


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
