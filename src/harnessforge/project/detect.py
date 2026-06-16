from __future__ import annotations

import json
import re
import shlex
import tomllib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from ..core.models import ProjectProfile, VerificationCommandRecord
from ..core.paths import is_inside_root
from .spec_system import analyze_spec_system, has_spec_system

MISSING_VERIFICATION_COMMAND = (
    "REVIEW REQUIRED: No project verification check detected. Replace this "
    "placeholder with the smallest reliable project check."
)

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".harnessforge",
    ".DS_Store",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".pants.d",
    ".rush",
    "__pycache__",
    "bazel-bin",
    "bazel-out",
    "bazel-testlogs",
    "build",
    "Desktop.ini",
    "desktop.ini",
    "dist",
    "node_modules",
    "target",
    "Thumbs.db",
    "venv",
}

COMPONENT_MARKERS = {
    ".buckconfig",
    ".terraform.lock.hcl",
    "BUILD",
    "BUILD.bazel",
    "Cargo.toml",
    "Gemfile",
    "Justfile",
    "Makefile",
    "MODULE.bazel",
    "Package.swift",
    "Pipfile",
    "REPO.bazel",
    "WORKSPACE",
    "WORKSPACE.bazel",
    "composer.json",
    "build.gradle",
    "build.gradle.kts",
    "Containerfile",
    "Dockerfile",
    "global.json",
    "go.mod",
    "go.work",
    "justfile",
    "lerna.json",
    "nx.json",
    "pants.toml",
    "package.json",
    "pnpm-workspace.yaml",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "rush.json",
    "settings.gradle",
    "settings.gradle.kts",
    "setup.py",
    "turbo.json",
    "turbo.jsonc",
    "uv.toml",
    "project.json",
    "backend.tf",
    "main.tf",
    "providers.tf",
    "terraform.tf",
    "terragrunt.hcl",
    "versions.tf",
}

ROOT_PRIORITY_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
    "package.json",
    "go.mod",
    "go.work",
    "Cargo.toml",
    "pom.xml",
    "MODULE.bazel",
    "WORKSPACE",
    "WORKSPACE.bazel",
    ".bazelrc",
    ".bazelversion",
    ".nvmrc",
    ".python-version",
    "Dockerfile",
    "Containerfile",
    "Makefile",
    "Justfile",
    "justfile",
)
PRIORITY_DIRECTORY_PASSES = (
    (".github", 300),
    (".agents", 200),
    ("docs/harness", 300),
    ("docs", 500),
    ("specs", 300),
    ("aspec", 300),
    ("workflows", 200),
    (".devcontainer", 100),
)
DIRECTORY_PRIORITY = {
    "src": 0,
    "scripts": 1,
    "tools": 2,
    "crates": 3,
    "apps": 4,
    "packages": 5,
    "services": 6,
    "examples": 7,
    ".github": 8,
    ".agents": 9,
    ".devcontainer": 10,
    "third_party": 80,
    "docs": 90,
    "specs": 91,
    "aspec": 92,
    "workflows": 93,
    "site": 94,
}
COMPONENT_SCAN_LIMIT = 80


def detect_project(
    root: Path,
    *,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
    max_files: int = 4000,
    max_components: int = COMPONENT_SCAN_LIMIT,
) -> ProjectProfile:
    if max_files <= 0:
        raise ValueError("--max-files must be greater than 0")
    if max_components <= 0:
        raise ValueError("--component-limit must be greater than 0")
    root = root.resolve()
    files = tuple(list_project_files(root, max_files=max_files))
    file_set = set(files)
    package_json = _read_json(root / "package.json", root)
    pyproject = _read_toml(root / "pyproject.toml", root)
    cargo_toml = _read_toml(root / "Cargo.toml", root)
    composer_json = _read_json(root / "composer.json", root)

    languages = _detect_languages(file_set, package_json)
    package_managers = _detect_package_managers(
        file_set,
        package_json,
        explicit_package_manager=explicit_package_manager,
    )
    runtime_files = tuple(
        file
        for file in (
            ".python-version",
            ".tool-versions",
            ".bazelignore",
            ".bazelrc",
            ".bazelversion",
            ".nvmrc",
            ".buckconfig",
            "pyproject.toml",
            "uv.toml",
            "Pipfile",
            "package.json",
            "pnpm-workspace.yaml",
            "tsconfig.json",
            "tsconfig.node.json",
            "turbo.json",
            "turbo.jsonc",
            "nx.json",
            "lerna.json",
            "rush.json",
            "go.mod",
            "go.work",
            "Cargo.toml",
            "pom.xml",
            "settings.gradle",
            "settings.gradle.kts",
            "build.gradle",
            "build.gradle.kts",
            "global.json",
            "composer.json",
            "Gemfile",
            "Justfile",
            "justfile",
            "Makefile",
            "Package.swift",
            "Package.resolved",
            ".config/nextest.toml",
            "validate.sh",
            "MODULE.bazel",
            "MODULE.bazel.lock",
            "REPO.bazel",
            "WORKSPACE",
            "WORKSPACE.bazel",
            "pants.toml",
            "terragrunt.hcl",
            "Dockerfile",
            "Containerfile",
            ".devcontainer/devcontainer.json",
        )
        if file in file_set
    )
    stack = _primary_stack(file_set, package_json, pyproject, languages)
    commands = explicit_commands or _verification_commands(
        root,
        file_set,
        package_json,
        pyproject,
        cargo_toml,
        package_managers,
        stack,
    )
    command_records = _verification_command_records(
        tuple(commands),
        file_set=file_set,
        explicit=bool(explicit_commands),
    )
    components, component_overflow = _detect_components(
        file_set,
        max_components=max_components,
    )
    workspace_markers = _detect_workspace_markers(
        root, file_set, package_json, pyproject, cargo_toml, composer_json
    )
    routing_markers = _detect_routing_markers(root, file_set)
    config_precedence = _config_precedence(
        file_set,
        package_json,
        explicit_package_manager=explicit_package_manager,
        explicit_commands=explicit_commands,
    )
    return ProjectProfile(
        root=root,
        name=root.name,
        stack=stack,
        languages=tuple(sorted(languages)),
        package_managers=package_managers,
        runtime_files=runtime_files,
        verification_commands=tuple(commands),
        components=components,
        files=files,
        workspace_markers=workspace_markers,
        routing_markers=routing_markers,
        config_precedence=config_precedence,
        file_scan_limit=max_files,
        file_scan_truncated=len(files) >= max_files,
        component_scan_limit=max_components,
        component_scan_truncated=bool(component_overflow),
        component_scan_total=len(components) + len(component_overflow),
        component_overflow=component_overflow,
        verification_command_records=command_records,
    )


def list_project_files(root: Path, *, max_files: int = 4000) -> list[str]:
    results: list[str] = []
    seen: set[str] = set()

    def add_file(relative: str, local_budget: list[int] | None = None) -> bool:
        if len(results) >= max_files:
            return False
        if local_budget is not None and local_budget[0] <= 0:
            return False
        if relative in seen or _ignored_relative_path(relative):
            return False
        path = root / relative
        if not path.is_file() or path.is_symlink():
            return False
        results.append(relative)
        seen.add(relative)
        if local_budget is not None:
            local_budget[0] -= 1
        return True

    def walk(
        current: Path,
        relative: str,
        *,
        local_budget: list[int] | None = None,
    ) -> None:
        if len(results) >= max_files:
            return
        if local_budget is not None and local_budget[0] <= 0:
            return

        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            return
        files = [entry for entry in entries if entry.is_file() and not entry.is_symlink()]
        directories = sorted(
            (entry for entry in entries if entry.is_dir() and not entry.is_symlink()),
            key=lambda item: (DIRECTORY_PRIORITY.get(item.name, 50), item.name.lower()),
        )
        for entry in files:
            if len(results) >= max_files:
                return
            if local_budget is not None and local_budget[0] <= 0:
                return
            rel = f"{relative}/{entry.name}" if relative else entry.name
            add_file(rel, local_budget=local_budget)
        for entry in directories:
            if len(results) >= max_files:
                return
            if local_budget is not None and local_budget[0] <= 0:
                return
            if entry.name in IGNORED_DIRS:
                continue
            rel = f"{relative}/{entry.name}" if relative else entry.name
            if _ignored_relative_path(rel):
                continue
            walk(entry, rel, local_budget=local_budget)

    for relative in ROOT_PRIORITY_FILES:
        add_file(relative)
    for relative, local_limit in PRIORITY_DIRECTORY_PASSES:
        path = root / relative
        if (
            path.is_dir()
            and not path.is_symlink()
            and not _ignored_relative_path(relative)
        ):
            walk(path, relative, local_budget=[local_limit])
    walk(root, "")
    return results


def _ignored_relative_path(relative: str) -> bool:
    return any(part in IGNORED_DIRS for part in Path(relative).parts)


def _detect_languages(
    file_set: set[str], package_json: dict[str, Any] | None
) -> set[str]:
    languages: set[str] = set()
    suffixes = {Path(file).suffix.lower() for file in file_set}
    if package_json or {".js", ".jsx", ".mjs", ".cjs"} & suffixes:
        languages.add("javascript")
    if {"tsconfig.json", "tsconfig.node.json"} & file_set or {".ts", ".tsx"} & suffixes:
        languages.add("typescript")
    if {"pyproject.toml", "requirements.txt", "setup.py"} & file_set or ".py" in suffixes:
        languages.add("python")
    if _has_agent_skill_surface(file_set):
        languages.add("docs")
    if "Package.swift" in file_set or ".swift" in suffixes:
        languages.add("swift")
    if {".sh", ".bash", ".zsh", ".command"} & suffixes:
        languages.add("shell")
    if {".cc", ".cpp", ".cxx", ".c", ".h", ".hpp"} & suffixes:
        languages.add("cpp")
    if {".bzl", ".scl"} & suffixes or any(
        Path(file).name in {"BUILD", "BUILD.bazel", "MODULE.bazel", "WORKSPACE"}
        for file in file_set
    ):
        languages.add("starlark")
    if "go.mod" in file_set or ".go" in suffixes:
        languages.add("go")
    if "go.work" in file_set:
        languages.add("go")
    if "Cargo.toml" in file_set or ".rs" in suffixes:
        languages.add("rust")
    if (
        {
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "settings.gradle",
            "settings.gradle.kts",
        }
        & file_set
        or ".java" in suffixes
    ):
        languages.add("java")
    if any(
        file.endswith((".csproj", ".fsproj", ".vbproj", ".sln", ".slnx"))
        for file in file_set
    ):
        languages.add("dotnet")
    if "composer.json" in file_set or ".php" in suffixes:
        languages.add("php")
    if "Gemfile" in file_set or ".rb" in suffixes:
        languages.add("ruby")
    if ".tf" in suffixes or "terragrunt.hcl" in file_set:
        languages.add("terraform")
    if {"MODULE.bazel", "REPO.bazel", "WORKSPACE", "WORKSPACE.bazel"} & file_set:
        languages.add("bazel")
    if "pants.toml" in file_set:
        languages.add("pants")
    if ".buckconfig" in file_set:
        languages.add("buck")
    if suffixes and suffixes <= {".md", ".txt", ".rst"}:
        languages.add("docs")
    if _has_structured_spec_surface(file_set) or has_spec_system(file_set):
        languages.add("docs")
    if _has_documentation_files(file_set) and not (
        languages
        & {
            "bazel",
            "buck",
            "cpp",
            "dotnet",
            "go",
            "java",
            "javascript",
            "pants",
            "php",
            "python",
            "ruby",
            "rust",
            "shell",
            "starlark",
            "swift",
            "terraform",
            "typescript",
        }
    ):
        languages.add("docs")
    return languages or {"generic"}


def _detect_package_managers(
    file_set: set[str],
    package_json: dict[str, Any] | None,
    *,
    explicit_package_manager: str | None,
) -> tuple[str, ...]:
    if explicit_package_manager:
        return (explicit_package_manager,)
    managers: list[str] = []
    filenames = {Path(file).name for file in file_set}
    package_manager = package_json.get("packageManager") if package_json else None
    if isinstance(package_manager, str):
        manager_name = package_manager.split("@", 1)[0].strip()
        if manager_name in {"bun", "npm", "pnpm", "yarn"}:
            managers.append(manager_name)
    if "bun.lock" in filenames or "bun.lockb" in filenames:
        managers.append("bun")
    if "pnpm-lock.yaml" in filenames or "pnpm-workspace.yaml" in filenames:
        managers.append("pnpm")
    if "yarn.lock" in filenames:
        managers.append("yarn")
    if "package-lock.json" in filenames or "package.json" in filenames:
        managers.append("npm")
    if {"Justfile", "justfile"} & filenames:
        managers.append("just")
    if "uv.lock" in filenames:
        managers.append("uv")
    if "poetry.lock" in filenames:
        managers.append("poetry")
    if "Pipfile" in filenames or "Pipfile.lock" in filenames:
        managers.append("pipenv")
    if "Cargo.toml" in filenames:
        managers.append("cargo")
    if "Package.swift" in filenames:
        managers.append("swiftpm")
    if "go.mod" in filenames:
        managers.append("go")
    if "pom.xml" in filenames:
        managers.append("maven")
    if {"build.gradle", "build.gradle.kts", "gradlew"} & filenames:
        managers.append("gradle")
    return tuple(_dedupe(managers))


def _config_precedence(
    file_set: set[str],
    package_json: dict[str, Any] | None,
    *,
    explicit_package_manager: str | None,
    explicit_commands: tuple[str, ...],
) -> tuple[str, ...]:
    sources: list[str] = []
    sources.extend(f"CLI --command: {command}" for command in explicit_commands)
    if explicit_package_manager:
        sources.append(f"CLI --package-manager: {explicit_package_manager}")
    if "docs/harness/manifest.json" in file_set:
        sources.append("docs/harness/manifest.json generated harness manifest")
    if package_json:
        package_manager = package_json.get("packageManager")
        if isinstance(package_manager, str):
            sources.append(f"package.json packageManager: {package_manager}")
        scripts = package_json.get("scripts")
        if isinstance(scripts, dict) and scripts:
            sources.append("package.json scripts")
    for marker in (
        "Justfile",
        "justfile",
        "Makefile",
        "makefile",
        "pyproject.toml",
        "uv.lock",
        "poetry.lock",
        "Pipfile",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "settings.gradle",
        "settings.gradle.kts",
        "build.gradle",
        "build.gradle.kts",
        "Package.swift",
        "composer.json",
        "Gemfile",
    ):
        if marker in file_set:
            sources.append(f"repo file: {marker}")
    for marker in (
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lock",
        "bun.lockb",
        "Cargo.lock",
        "Package.resolved",
        "go.sum",
        "poetry.lock",
        "Pipfile.lock",
    ):
        if marker in file_set:
            sources.append(f"lockfile: {marker}")
    return tuple(_dedupe(sources))


def _detect_components(
    file_set: set[str],
    *,
    max_components: int = COMPONENT_SCAN_LIMIT,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    directories: dict[str, list[str]] = {}
    for file_name in sorted(file_set):
        path = Path(file_name)
        is_dotnet_project = path.name.endswith(
            (".csproj", ".fsproj", ".sln", ".slnx", ".vbproj")
        )
        if path.name not in COMPONENT_MARKERS and not is_dotnet_project:
            continue
        directory = "." if len(path.parts) == 1 else "/".join(path.parts[:-1])
        directories.setdefault(directory, []).append(path.name)

    components: list[str] = []
    for directory in sorted(
        directories,
        key=lambda item: _component_sort_key(item, directories[item]),
    ):
        markers = ", ".join(_dedupe(sorted(directories[directory])))
        components.append(f"{directory} ({markers})")
    return (
        tuple(components[:max_components]),
        tuple(components[max_components:]),
    )


def _component_sort_key(directory: str, markers: list[str]) -> tuple[int, int, str]:
    return (
        _component_priority(directory, markers),
        0 if directory == "." else directory.count("/") + 1,
        directory,
    )


def _component_priority(directory: str, markers: list[str]) -> int:
    marker_set = set(markers)
    if directory == ".":
        return 0
    first_segment = directory.split("/", 1)[0]
    if first_segment in {"apps", "packages", "services", "crates"}:
        return 10
    if first_segment in {"src", "cmd", "pkg", "lib"}:
        return 20
    if first_segment in {"tools", "scripts", "hack"}:
        return 30
    if "BUILD" in marker_set or "BUILD.bazel" in marker_set:
        return 40
    if first_segment in {"test", "tests", "spec"}:
        return 50
    if first_segment in {"docs", "site", "examples", "samples"}:
        return 70
    if first_segment in {"vendor", "third_party", "external"}:
        return 90
    return 60


def _detect_workspace_markers(
    root: Path,
    file_set: set[str],
    package_json: dict[str, Any] | None,
    pyproject: dict[str, Any] | None,
    cargo_toml: dict[str, Any] | None,
    composer_json: dict[str, Any] | None,
) -> tuple[str, ...]:
    markers: list[str] = []
    if package_json and "workspaces" in package_json:
        markers.append("package.json workspaces")
    for marker in (
        "pnpm-workspace.yaml",
        "turbo.json",
        "turbo.jsonc",
        "nx.json",
        "lerna.json",
        "rush.json",
        "go.work",
        "settings.gradle",
        "settings.gradle.kts",
        "MODULE.bazel",
        "REPO.bazel",
        "WORKSPACE",
        "WORKSPACE.bazel",
        "pants.toml",
        ".buckconfig",
    ):
        if marker in file_set:
            markers.append(marker)
    if _has_structured_spec_surface(file_set):
        markers.append("structured project specs")
    markers.extend(analyze_spec_system(root, tuple(file_set)).workspace_markers)
    if _has_multiple_nested_components(file_set):
        markers.append("multiple nested component manifests")
    if _has_uv_workspace(pyproject):
        markers.append("pyproject.toml [tool.uv.workspace]")
    if cargo_toml and "workspace" in cargo_toml:
        markers.append("Cargo.toml [workspace]")
    if _pom_has_modules(root / "pom.xml", root):
        markers.append("pom.xml <modules>")
    if _composer_has_path_repositories(composer_json):
        markers.append("composer.json path repositories")
    return tuple(_dedupe(markers))


def _has_multiple_nested_components(file_set: set[str]) -> bool:
    component_directories: set[str] = set()
    for file_name in file_set:
        path = Path(file_name)
        is_dotnet_project = path.name.endswith(
            (".csproj", ".fsproj", ".sln", ".slnx", ".vbproj")
        )
        if path.name not in COMPONENT_MARKERS and not is_dotnet_project:
            continue
        if len(path.parts) > 1:
            component_directories.add("/".join(path.parts[:-1]))
    return len(component_directories) >= 2


def _detect_routing_markers(root: Path, file_set: set[str]) -> tuple[str, ...]:
    markers: list[str] = []
    workflow_files = tuple(
        file
        for file in sorted(file_set)
        if file.startswith(".github/workflows/")
        and Path(file).suffix.lower() in {".yml", ".yaml"}
    )
    if workflow_files:
        markers.append(".github/workflows")
    if any(
        _text_matches(root / file, root, r"(?m)^\s*paths(?:-ignore)?\s*:")
        for file in workflow_files
    ):
        markers.append(".github/workflows path filters")
    if any(
        _text_matches(root / file, root, r"(?m)^\s*working-directory\s*:")
        for file in workflow_files
    ):
        markers.append(".github/workflows working-directory")
    if any(
        file.startswith(".github/actions/")
        and Path(file).name in {"action.yml", "action.yaml"}
        for file in file_set
    ):
        markers.append(".github/actions")
    if any(
        file.startswith(".devcontainer/") and Path(file).name == "devcontainer.json"
        for file in file_set
    ):
        markers.append(".devcontainer")
    if any(file.startswith(".harness/") for file in file_set):
        markers.append(".harness")
    if any(file.startswith(".windsurf/") for file in file_set):
        markers.append(".windsurf")
    if any(file.startswith(".claude-plugin/") for file in file_set):
        markers.append(".claude-plugin")
    if any(file.startswith(".codex-plugin/") for file in file_set):
        markers.append(".codex-plugin")
    if _has_agent_skill_surface(file_set):
        markers.append("agent skills")
    if {"Justfile", "justfile"} & file_set:
        markers.append("justfile")
    if _has_structured_spec_surface(file_set):
        markers.append("structured project specs")
    markers.extend(analyze_spec_system(root, tuple(file_set)).routing_markers)
    for marker in (
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        ".claude/AGENTS.md",
        ".claude/CLAUDE.md",
        ".gemini/GEMINI.md",
        "action.yml",
        "action.yaml",
        ".github/copilot-instructions.md",
        ".bazelrc",
        ".bazelignore",
        ".bazelversion",
    ):
        if marker in file_set:
            markers.append(marker)
    return tuple(_dedupe(markers))


def _text_matches(path: Path, root: Path, pattern: str) -> bool:
    if not is_inside_root(path, root):
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return re.search(pattern, text) is not None


def _has_uv_workspace(pyproject: dict[str, Any] | None) -> bool:
    if not pyproject:
        return False
    tool = pyproject.get("tool")
    if not isinstance(tool, dict):
        return False
    uv = tool.get("uv")
    return isinstance(uv, dict) and isinstance(uv.get("workspace"), dict)


def _pom_has_modules(path: Path, root: Path) -> bool:
    if not is_inside_root(path, root) or not path.exists():
        return False
    try:
        tree = ElementTree.parse(path)
    except (ElementTree.ParseError, OSError):
        return False
    root_element = tree.getroot()
    for element in root_element.iter():
        name = element.tag.rsplit("}", 1)[-1]
        if name == "module" and element.text and element.text.strip():
            return True
    return False


def _composer_has_path_repositories(composer_json: dict[str, Any] | None) -> bool:
    if not composer_json:
        return False
    repositories = composer_json.get("repositories")
    if isinstance(repositories, dict):
        repositories = repositories.values()
    if not isinstance(repositories, list):
        return False
    for repository in repositories:
        if isinstance(repository, dict) and repository.get("type") == "path":
            return True
    return False


def _primary_stack(
    file_set: set[str],
    package_json: dict[str, Any] | None,
    pyproject: dict[str, Any] | None,
    languages: set[str],
) -> str:
    if "Cargo.toml" in file_set:
        return "rust"
    if "Package.swift" in file_set:
        return "swift"
    if {"MODULE.bazel", "REPO.bazel", "WORKSPACE", "WORKSPACE.bazel"} & file_set:
        return "bazel"
    if "pants.toml" in file_set:
        return "pants"
    if ".buckconfig" in file_set:
        return "buck"
    if package_json:
        deps = _package_deps(package_json)
        if {"react", "next", "@vitejs/plugin-react"} & deps or any(
            file.endswith(".tsx") for file in file_set
        ):
            return "typescript-react"
        if "typescript" in languages:
            return "typescript"
        return "node"
    if pyproject and _root_python_runtime_project(file_set, pyproject):
        return "python"
    if {"go.mod", "go.work"} & file_set:
        return "go"
    if {"pom.xml", "build.gradle", "build.gradle.kts"} & file_set:
        return "java"
    if any(
        Path(file).parent == Path(".")
        and file.endswith((".csproj", ".fsproj", ".vbproj", ".sln", ".slnx"))
        for file in file_set
    ):
        return "dotnet"
    if _nested_component_count(file_set) >= 2 and languages != {"terraform"}:
        return "monorepo"
    if _looks_like_docs_site(file_set):
        return "docs"
    if _looks_like_structured_docs_repo(file_set, languages):
        return "docs"
    if "composer.json" in file_set:
        return "php"
    if "Gemfile" in file_set:
        return "ruby"
    if {"pyproject.toml", "requirements.txt", "setup.py"} & file_set:
        return "python"
    priority = [
        ("python", "python"),
        ("go", "go"),
        ("rust", "rust"),
        ("swift", "swift"),
        ("java", "java"),
        ("dotnet", "dotnet"),
        ("php", "php"),
        ("ruby", "ruby"),
        ("terraform", "terraform"),
        ("cpp", "cpp"),
        ("docs", "docs"),
        ("shell", "shell"),
    ]
    for language, stack in priority:
        if language in languages:
            return stack
    return "generic"


def _looks_like_docs_site(file_set: set[str]) -> bool:
    markdown_count = sum(1 for file in file_set if Path(file).suffix.lower() == ".md")
    return markdown_count >= 5 and bool(
        {"_config.yml", "validate.sh", "mkdocs.yml", "hugo.toml", "config.toml"}
        & file_set
    )


def _looks_like_structured_docs_repo(file_set: set[str], languages: set[str]) -> bool:
    implementation_languages = languages - {"docs", "generic", "shell"}
    return _has_structured_spec_surface(file_set) and not implementation_languages


def _has_structured_spec_surface(file_set: set[str]) -> bool:
    if has_spec_system(file_set):
        return True
    markdown_paths = [
        Path(file)
        for file in file_set
        if Path(file).suffix.lower() in {".md", ".rst", ".txt"}
    ]
    if len(markdown_paths) < 3:
        return False
    names = {path.name.lower() for path in markdown_paths}
    parts = {part.lower() for path in markdown_paths for part in path.parts}
    foundation_names = {
        "foundation.md",
        "overview.md",
        "requirements.md",
        "product.md",
        "vision.md",
    }
    spec_parts = {
        "architecture",
        "design",
        "security",
        "devops",
        "ux",
        "ui",
        "work-items",
        "work_items",
        "workitems",
        "plans",
        "planning",
        "requirements",
    }
    planning_parts = {
        "work-items",
        "work_items",
        "workitems",
        "plans",
        "planning",
        "tasks",
    }
    return (
        bool(foundation_names & names)
        and bool(spec_parts & parts)
        and (bool(planning_parts & parts) or any("template" in name for name in names))
    )


def _has_documentation_files(file_set: set[str]) -> bool:
    return any(
        Path(file).suffix.lower() in {".adoc", ".md", ".rst", ".txt"}
        for file in file_set
    )


def _has_agent_skill_surface(file_set: set[str]) -> bool:
    return any(_is_agent_skill_file(file) for file in file_set)


def _is_agent_skill_file(file: str) -> bool:
    path = Path(file)
    parts = path.parts
    if path.name != "SKILL.md":
        return False
    return len(parts) >= 3 and (
        parts[0] == "skills"
        or parts[:2] in {(".claude", "skills"), (".codex", "skills")}
    )


def _nested_component_count(file_set: set[str]) -> int:
    component_dirs = {
        str(Path(file).parent)
        for file in file_set
        if Path(file).parent != Path(".") and Path(file).name in COMPONENT_MARKERS
    }
    return len(component_dirs)


def _verification_commands(
    root: Path,
    file_set: set[str],
    package_json: dict[str, Any] | None,
    pyproject: dict[str, Any] | None,
    cargo_toml: dict[str, Any] | None,
    package_managers: tuple[str, ...],
    stack: str,
) -> tuple[str, ...]:
    commands: list[str] = []
    make_commands = _make_commands(root, file_set)
    commands.extend(make_commands)
    commands.extend(_just_commands(root, file_set))
    validation_commands = _validation_script_commands(file_set)
    if "make architecture-lint" in make_commands:
        validation_commands = [
            command
            for command in validation_commands
            if command != "./tools/architecture-lint.sh"
        ]
    commands.extend(validation_commands)
    if package_json:
        commands.extend(_node_commands(package_json, package_managers))
    if stack not in {"bazel", "buck", "pants"}:
        commands.extend(_root_jvm_commands(file_set))
    if stack == "python":
        commands.extend(_python_commands(file_set, pyproject, package_managers))
    elif pyproject and _root_python_runtime_project(file_set, pyproject):
        commands.extend(_python_commands(file_set, pyproject, package_managers))
    if stack == "go":
        commands.append("go test ./...")
    if stack == "rust":
        if "just ci" not in commands:
            commands.extend(_rust_commands(root, file_set, cargo_toml))
    if stack == "swift":
        commands.extend(_swift_commands(file_set, has_make_command=bool(commands)))
    if stack == "dotnet":
        commands.append("dotnet test")
    if stack == "php" and "composer.json" in file_set:
        commands.append("composer test")
    if stack == "ruby":
        commands.append("bundle exec rake test")
    if stack == "terraform":
        commands.append("terraform fmt -check -recursive")
    if stack == "bazel" or {
        "MODULE.bazel",
        "REPO.bazel",
        "WORKSPACE",
        "WORKSPACE.bazel",
    } & file_set:
        commands.append("bazel test //...")
    if stack == "pants":
        commands.append("pants test ::")
    if stack == "buck":
        commands.append("buck2 test //...")
    commands.extend(_nested_component_commands(root, file_set))
    commands = _dedupe(commands)
    if not commands:
        commands = (MISSING_VERIFICATION_COMMAND,)
    return tuple(commands)


def _verification_command_records(
    commands: tuple[str, ...],
    *,
    file_set: set[str],
    explicit: bool,
) -> tuple[VerificationCommandRecord, ...]:
    return tuple(
        VerificationCommandRecord(
            command=command,
            command_class=_verification_command_class(command),
            scope=_verification_command_scope(command),
            source_type=source_type,
            source_path=source_path,
            source_detail=source_detail,
            confidence=confidence,
        )
        for command in commands
        for source_type, source_path, source_detail, confidence in (
            _verification_command_source(
                command,
                file_set=file_set,
                explicit=explicit,
            ),
        )
    )


def _verification_command_class(command: str) -> str:
    lower = command.lower()
    if command == MISSING_VERIFICATION_COMMAND:
        return "missing"
    if any(token in lower for token in ("fmt", "format")):
        return "format"
    if any(token in lower for token in (" test", "pytest", "unittest", "nextest")):
        return "test"
    if any(
        token in lower
        for token in (
            "lint",
            "ruff",
            "mypy",
            "clippy",
            "typecheck",
            "type-check",
            "compileall",
        )
    ):
        return "static-analysis"
    if "build" in lower:
        return "build"
    if any(token in lower for token in ("ci", "check", "validate", "verify")):
        return "aggregate"
    return "other"


def _verification_command_scope(command: str) -> str:
    lower = command.lower()
    if command == MISSING_VERIFICATION_COMMAND:
        return "none"
    if any(
        token in lower
        for token in (
            " --prefix ",
            " --project ",
            " --working-dir ",
            " --manifest-path ",
            " -f ",
            " -p ",
        )
    ):
        return "component"
    if re.search(r"\s\./[^.\s][^\s]*/\.\.\.", lower):
        return "component"
    if any(
        token in lower
        for token in (
            "./...",
            "//...",
            " --workspace",
            " --all",
            " ::",
            " .",
        )
    ):
        return "repo"
    if any(
        part in lower
        for part in (
            " apps/",
            " packages/",
            " services/",
            " crates/",
            " src/",
            " tools/",
        )
    ):
        return "component"
    return "repo"


def _verification_command_source(
    command: str,
    *,
    file_set: set[str],
    explicit: bool,
) -> tuple[str, str, str, str]:
    if command == MISSING_VERIFICATION_COMMAND:
        return ("missing-placeholder", "", "review-required placeholder", "high")
    if explicit:
        return ("cli", "", "--command", "high")
    tokens = _split_command(command)
    if not tokens:
        return ("unknown", "", "empty command", "low")
    source = _make_command_source(tokens, file_set)
    if source:
        return source
    source = _just_command_source(tokens, file_set)
    if source:
        return source
    source = _node_command_source(tokens, file_set)
    if source:
        return source
    source = _python_command_source(tokens, file_set)
    if source:
        return source
    source = _go_command_source(tokens, file_set)
    if source:
        return source
    source = _rust_command_source(tokens, file_set)
    if source:
        return source
    source = _jvm_command_source(tokens, file_set)
    if source:
        return source
    source = _swift_command_source(tokens, file_set)
    if source:
        return source
    source = _dotnet_command_source(tokens, file_set)
    if source:
        return source
    source = _composer_command_source(tokens, file_set)
    if source:
        return source
    source = _ruby_command_source(tokens, file_set)
    if source:
        return source
    source = _terraform_command_source(tokens, file_set)
    if source:
        return source
    source = _bazel_command_source(tokens, file_set)
    if source:
        return source
    source = _pants_command_source(tokens, file_set)
    if source:
        return source
    source = _buck_command_source(tokens, file_set)
    if source:
        return source
    source = _script_command_source(tokens, file_set)
    if source:
        return source
    return ("heuristic", "", "detected from project stack", "low")


def _split_command(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _make_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if tokens[0] != "make" or len(tokens) < 2:
        return None
    makefile = _first_existing(file_set, "Makefile", "makefile")
    return ("makefile-target", makefile, f"target:{tokens[1]}", "high")


def _just_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if tokens[0] != "just" or len(tokens) < 2:
        return None
    justfile = _first_existing(file_set, "Justfile", "justfile")
    return ("justfile-recipe", justfile, f"recipe:{tokens[1]}", "high")


def _node_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    manager = tokens[0]
    if manager not in {"npm", "pnpm", "yarn", "bun"}:
        return None
    directory = "."
    script = ""
    if manager == "npm" and "--prefix" in tokens:
        index = tokens.index("--prefix")
        if index + 1 < len(tokens):
            directory = tokens[index + 1]
        for candidate in tokens[index + 2 :]:
            if not candidate.startswith("-"):
                script = "test" if candidate == "test" else candidate
                break
    elif "run" in tokens:
        index = tokens.index("run")
        if index + 1 < len(tokens):
            script = tokens[index + 1]
    elif manager == "npm" and len(tokens) > 1 and tokens[1] == "test":
        script = "test"
    elif manager in {"yarn", "bun"} and len(tokens) > 1:
        script = tokens[1]
    source_path = _manifest_in_directory(file_set, directory, "package.json")
    detail = f"{manager} script:{script}" if script else f"{manager} package command"
    return ("package-script", source_path, detail, "high" if source_path else "medium")


def _python_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    runner = ""
    project_directory = "."
    explicit_project_directory = False
    if tokens[:3] == ["uv", "run", "--project"] and len(tokens) >= 5:
        runner = "uv"
        project_directory = tokens[3]
        explicit_project_directory = True
    elif tokens[:2] in (["poetry", "run"], ["pipenv", "run"]):
        runner = tokens[0]
    python_index = next(
        (
            index
            for index, token in enumerate(tokens)
            if token in {"python", "python3"} or token.endswith("/python")
        ),
        -1,
    )
    if python_index < 0:
        return None
    module = ""
    if "-m" in tokens[python_index:]:
        module_index = tokens.index("-m", python_index)
        if module_index + 1 < len(tokens):
            module = tokens[module_index + 1]
        for argument in tokens[module_index + 2 :]:
            if argument and not argument.startswith("-") and argument != ".":
                argument_directory = _project_directory_for_argument(
                    argument,
                    file_set,
                )
                if argument_directory != "." or not explicit_project_directory:
                    project_directory = argument_directory
                break
    source_path = _python_source_path(file_set, project_directory)
    detail = f"{runner + ' ' if runner else ''}python module:{module or 'unknown'}"
    return ("python-project", source_path, detail, "high" if source_path else "medium")


def _go_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if tokens[:2] != ["go", "test"]:
        return None
    directory = "."
    for token in tokens[2:]:
        if token == "./...":
            directory = "."
            break
        if token.startswith("./") and token.endswith("/..."):
            directory = token[2:-4]
            break
    source_path = _manifest_in_directory(file_set, directory, "go.mod")
    return ("go-module", source_path, "go test", "high" if source_path else "medium")


def _rust_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "cargo":
        return None
    if "--manifest-path" in tokens:
        index = tokens.index("--manifest-path")
        if index + 1 < len(tokens):
            source_path = tokens[index + 1]
            return ("rust-manifest", source_path, "cargo manifest-path", "high")
    source_path = _first_existing(file_set, "Cargo.toml")
    return ("rust-manifest", source_path, f"cargo {tokens[1] if len(tokens) > 1 else ''}".strip(), "high" if source_path else "medium")


def _jvm_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    executable = tokens[0]
    if executable in {"mvn", "./mvnw"}:
        source_path = _flag_value(tokens, "-f") or _first_existing(file_set, "pom.xml")
        return ("jvm-build", source_path, "maven", "high" if source_path else "medium")
    if executable in {"gradle", "./gradlew"}:
        directory = _flag_value(tokens, "-p") or "."
        source_path = _manifest_in_directory(
            file_set, directory, "build.gradle", "build.gradle.kts"
        )
        return ("jvm-build", source_path, "gradle", "high" if source_path else "medium")
    return None


def _swift_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "swift":
        return None
    source_path = _first_existing(file_set, "Package.swift")
    return (
        "swift-package",
        source_path,
        f"swift {tokens[1] if len(tokens) > 1 else ''}".strip(),
        "high" if source_path else "medium",
    )


def _dotnet_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if tokens[:2] != ["dotnet", "test"]:
        return None
    source_path = next(
        (
            file_name
            for file_name in sorted(file_set)
            if Path(file_name).parent == Path(".")
            and file_name.endswith((".sln", ".slnx", ".csproj", ".fsproj", ".vbproj"))
        ),
        "",
    )
    return ("dotnet-project", source_path, "dotnet test", "high" if source_path else "medium")


def _composer_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "composer":
        return None
    directory = "."
    for token in tokens:
        if token.startswith("--working-dir="):
            directory = token.split("=", 1)[1]
    if "--working-dir" in tokens:
        index = tokens.index("--working-dir")
        if index + 1 < len(tokens):
            directory = tokens[index + 1]
    source_path = _manifest_in_directory(file_set, directory, "composer.json")
    return ("php-composer", source_path, "composer script", "high" if source_path else "medium")


def _ruby_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "bundle":
        return None
    source_path = _first_existing(file_set, "Gemfile")
    for token in tokens:
        if token.startswith("--gemfile"):
            _, _, value = token.partition("=")
            if value:
                source_path = value
    return ("ruby-gemfile", source_path, "bundle rake", "high" if source_path else "medium")


def _terraform_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "terraform":
        return None
    source_path = _first_existing(
        file_set, "terraform.tf", "versions.tf", "main.tf", "providers.tf"
    )
    return (
        "terraform-config",
        source_path,
        f"terraform {tokens[1] if len(tokens) > 1 else ''}".strip(),
        "medium",
    )


def _bazel_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "bazel":
        return None
    source_path = _first_existing(
        file_set,
        "MODULE.bazel",
        "WORKSPACE.bazel",
        "WORKSPACE",
        ".bazelrc",
    )
    return ("bazel-workspace", source_path, "bazel target pattern", "high" if source_path else "medium")


def _pants_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "pants":
        return None
    source_path = _first_existing(file_set, "pants.toml")
    return ("pants-config", source_path, "pants goal", "high" if source_path else "medium")


def _buck_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    if not tokens or tokens[0] != "buck2":
        return None
    source_path = _first_existing(file_set, ".buckconfig")
    return ("buck-config", source_path, "buck2 target pattern", "high" if source_path else "medium")


def _script_command_source(
    tokens: list[str], file_set: set[str]
) -> tuple[str, str, str, str] | None:
    script = tokens[0]
    if not script.startswith("./"):
        return None
    source_path = script.removeprefix("./")
    if source_path not in file_set:
        return ("script", source_path, "script path", "medium")
    return ("script", source_path, "script path", "high")


def _flag_value(tokens: list[str], flag: str) -> str:
    if flag not in tokens:
        return ""
    index = tokens.index(flag)
    if index + 1 >= len(tokens):
        return ""
    return tokens[index + 1]


def _first_existing(file_set: set[str], *paths: str) -> str:
    return next((path for path in paths if path in file_set), "")


def _manifest_in_directory(file_set: set[str], directory: str, *names: str) -> str:
    normalized = "." if directory in {"", "."} else directory.strip("/")
    candidates = [
        name if normalized == "." else f"{normalized}/{name}"
        for name in names
    ]
    return _first_existing(file_set, *candidates)


def _python_source_path(file_set: set[str], directory: str) -> str:
    return _manifest_in_directory(
        file_set,
        directory,
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Pipfile",
    )


def _project_directory_for_argument(argument: str, file_set: set[str]) -> str:
    path = Path(argument)
    candidates = [path.as_posix()]
    candidates.extend(parent.as_posix() for parent in path.parents if parent != Path("."))
    for candidate in candidates:
        if _python_source_path(file_set, candidate):
            return candidate
    return "."


def _root_jvm_commands(file_set: set[str]) -> list[str]:
    commands: list[str] = []
    if "pom.xml" in file_set:
        maven = "./mvnw" if "mvnw" in file_set else "mvn"
        commands.append(f"{maven} test")
    if "gradlew" in file_set:
        commands.append("./gradlew test")
    elif "build.gradle" in file_set or "build.gradle.kts" in file_set:
        commands.append("gradle test")
    return commands


def _make_commands(root: Path, file_set: set[str]) -> list[str]:
    makefile = (
        "Makefile"
        if "Makefile" in file_set
        else "makefile"
        if "makefile" in file_set
        else ""
    )
    if not makefile:
        return []
    targets = _makefile_targets(root / makefile, root)
    commands: list[str] = []
    for target in ("check", "test", "architecture-lint", "validate", "lint"):
        if target in targets:
            commands.append(f"make {target}")
    return commands[:3]


def _makefile_targets(path: Path, root: Path) -> set[str]:
    if not is_inside_root(path, root):
        return set()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    targets: set[str] = set()
    for line in text.splitlines():
        if line.startswith(("\t", " ")):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*)\s*:", line)
        if not match:
            continue
        for target in match.group(1).split():
            if target.startswith(".") or "%" in target:
                continue
            targets.add(target)
    return targets


def _just_commands(root: Path, file_set: set[str]) -> list[str]:
    justfile = (
        "justfile"
        if "justfile" in file_set
        else "Justfile"
        if "Justfile" in file_set
        else ""
    )
    if not justfile:
        return []
    targets = _justfile_targets(root / justfile, root)
    if "ci" in targets:
        return ["just ci"]
    commands: list[str] = []
    for target in (
        "check",
        "fmt-check",
        "lint",
        "test",
        "gen-docs-check",
        "docs-check",
        "build",
    ):
        if target in targets:
            commands.append(f"just {target}")
    return commands[:4]


def _justfile_targets(path: Path, root: Path) -> set[str]:
    if not is_inside_root(path, root):
        return set()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    targets: set[str] = set()
    for line in text.splitlines():
        if line.startswith(("\t", " ")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "set ", "export ")):
            continue
        if ":=" in stripped:
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)(?:\s+[^:#]*)?:", line)
        if not match:
            continue
        target = match.group(1)
        if target.startswith((".", "_")) or "%" in target:
            continue
        targets.add(target)
    return targets


def _validation_script_commands(file_set: set[str]) -> list[str]:
    commands: list[str] = []
    for script in (
        "validate.sh",
        "check.sh",
        "test.sh",
        "tools/architecture-lint.sh",
        "tools/validate_harness.sh",
        "tools/check_harness_docs.sh",
        "scripts/check_harness_docs.sh",
        "tools/test_dependency_parsing.sh",
    ):
        if script in file_set:
            commands.append(f"./{script}")
    return commands[:4]


def _swift_commands(file_set: set[str], *, has_make_command: bool) -> list[str]:
    if "Package.swift" not in file_set or has_make_command:
        return []
    if any(file.startswith("Tests/") for file in file_set):
        return ["swift test"]
    return ["swift build"]


def _node_commands(
    package_json: dict[str, Any], package_managers: tuple[str, ...]
) -> list[str]:
    scripts = package_json.get("scripts")
    if not isinstance(scripts, dict):
        return []
    manager = next(
        (item for item in package_managers if item in {"pnpm", "yarn", "bun", "npm"}),
        "npm",
    )
    commands: list[str] = []
    for script in ("check", "typecheck", "type-check", "lint", "test", "build"):
        if script not in scripts:
            continue
        if manager == "npm" and script == "test":
            commands.append("npm test")
        elif manager == "yarn":
            commands.append(f"yarn {script}")
        elif manager == "bun":
            commands.append(f"bun run {script}")
        elif manager == "pnpm":
            commands.append(f"pnpm run {script}")
        else:
            commands.append(f"npm run {script}")
    return commands


def _rust_commands(
    root: Path, file_set: set[str], cargo_toml: dict[str, Any] | None
) -> list[str]:
    commands: list[str] = []
    components = _rust_toolchain_components(root, file_set)
    if (
        "rustfmt" in components
        or ".rustfmt.toml" in file_set
        or "rustfmt.toml" in file_set
    ):
        commands.append("cargo fmt --all -- --check")
    if "clippy" in components:
        commands.append(
            "cargo clippy --workspace --all-targets --all-features -- -D warnings"
        )
    rust_command = (
        "cargo test --workspace"
        if cargo_toml and "workspace" in cargo_toml
        else "cargo test"
    )
    commands.append(rust_command)
    return commands


def _rust_toolchain_components(root: Path, file_set: set[str]) -> set[str]:
    if "rust-toolchain.toml" not in file_set:
        return set()
    toolchain = _read_toml(root / "rust-toolchain.toml", root)
    if not toolchain:
        return set()
    value = toolchain.get("toolchain")
    if not isinstance(value, dict):
        return set()
    components = value.get("components")
    if not isinstance(components, list):
        return set()
    return {component for component in components if isinstance(component, str)}


def _nested_component_commands(root: Path, file_set: set[str]) -> list[str]:
    commands: list[str] = []
    has_root_cargo = "Cargo.toml" in file_set
    nested_pyproject_dirs = {
        Path(file_name).parent.as_posix()
        for file_name in file_set
        if Path(file_name).name == "pyproject.toml" and len(Path(file_name).parts) > 1
    }
    for file_name in sorted(file_set):
        path = Path(file_name)
        if len(path.parts) <= 1:
            continue
        if _is_fixture_component(path) or _is_non_project_command_component(path):
            continue
        directory = path.parent.as_posix()
        quoted_directory = shlex.quote(directory)
        if path.name == "package.json":
            package_json = _read_json(root / path, root)
            if package_json:
                manager = _component_node_manager(directory, file_set)
                commands.extend(
                    _component_node_commands(quoted_directory, package_json, manager)
                )
        elif path.name == "pyproject.toml":
            pyproject = _read_toml(root / path, root)
            python_prefix = _nested_python_runner_prefix(directory, file_set)
            commands.append(
                f"{python_prefix}python -m compileall {quoted_directory}"
            )
            test_directory = _nested_python_test_directory(
                file_set,
                directory,
                allow_repo_test_dirs=len(nested_pyproject_dirs) == 1,
            )
            if test_directory and _uses_pytest(file_set, pyproject):
                commands.append(
                    f"{python_prefix}python -m pytest {shlex.quote(test_directory)}"
                )
            elif test_directory:
                commands.append(
                    f"{python_prefix}python -m unittest discover -s "
                    f"{shlex.quote(test_directory)}"
                )
        elif path.name == "Cargo.toml" and not has_root_cargo:
            commands.append(f"cargo test --manifest-path {quoted_directory}/Cargo.toml")
        elif path.name == "go.mod":
            commands.append(f"go test ./{directory}/...")
        elif path.name == "pom.xml":
            maven = "./mvnw" if "mvnw" in file_set else "mvn"
            commands.append(f"{maven} -f {quoted_directory}/pom.xml test")
        elif path.name in {"build.gradle", "build.gradle.kts"}:
            gradle = "./gradlew" if "gradlew" in file_set else "gradle"
            commands.append(f"{gradle} -p {quoted_directory} test")
        elif path.name == "Gemfile":
            commands.append(f"bundle exec --gemfile {quoted_directory}/Gemfile rake test")
        elif path.name == "composer.json":
            commands.append(f"composer --working-dir {quoted_directory} test")
    return commands[:20]


def _is_fixture_component(path: Path) -> bool:
    return bool({"fixture", "fixtures", "testdata", "samples"} & set(path.parts))


def _is_non_project_command_component(path: Path) -> bool:
    return bool(
        {
            "docs",
            "examples",
            "external",
            "site",
            "third_party",
            "vendor",
            "vendors",
        }
        & set(path.parts)
    )


def _top_level_directories(file_set: set[str], directory: str) -> set[str]:
    prefix = f"{directory}/"
    return {
        f"{directory}/{Path(file.removeprefix(prefix)).parts[0]}"
        for file in file_set
        if file.startswith(prefix) and Path(file.removeprefix(prefix)).parts
    }


def _nested_python_runner_prefix(directory: str, file_set: set[str]) -> str:
    if "uv.lock" in file_set or f"{directory}/uv.lock" in file_set:
        return f"uv run --project {shlex.quote(directory)} "
    if f"{directory}/poetry.lock" in file_set:
        return "poetry run "
    if f"{directory}/Pipfile.lock" in file_set:
        return "pipenv run "
    return ""


def _nested_python_test_directory(
    file_set: set[str], directory: str, *, allow_repo_test_dirs: bool
) -> str:
    candidates = [f"{directory}/tests"]
    if allow_repo_test_dirs:
        candidates.extend(("scripts/tests", "tests"))
    directories = {str(Path(file).parent) for file in file_set if file.endswith(".py")}
    for candidate in candidates:
        if any(path == candidate or path.startswith(f"{candidate}/") for path in directories):
            return candidate
    return ""


def _component_node_manager(directory: str, file_set: set[str]) -> str:
    if f"{directory}/pnpm-lock.yaml" in file_set:
        return "pnpm"
    if f"{directory}/yarn.lock" in file_set:
        return "yarn"
    if f"{directory}/bun.lock" in file_set or f"{directory}/bun.lockb" in file_set:
        return "bun"
    return "npm"


def _component_node_commands(
    directory: str, package_json: dict[str, Any], manager: str
) -> list[str]:
    scripts = package_json.get("scripts")
    if not isinstance(scripts, dict):
        return []
    commands: list[str] = []
    for script in ("check", "typecheck", "type-check", "lint", "test", "build"):
        if script not in scripts:
            continue
        if manager == "pnpm":
            commands.append(f"pnpm --dir {directory} run {script}")
        elif manager == "yarn":
            commands.append(f"yarn --cwd {directory} {script}")
        elif manager == "bun":
            commands.append(f"bun --cwd {directory} run {script}")
        elif script == "test":
            commands.append(f"npm --prefix {directory} test")
        else:
            commands.append(f"npm --prefix {directory} run {script}")
    return commands


def _python_commands(
    file_set: set[str],
    pyproject: dict[str, Any] | None,
    package_managers: tuple[str, ...],
) -> list[str]:
    prefix = _python_runner_prefix(package_managers)
    commands = [f"{prefix}python -m compileall ."]
    if _uses_ruff(file_set, pyproject):
        commands.append(f"{prefix}python -m ruff check .")
    if _uses_mypy(file_set, pyproject):
        commands.append(f"{prefix}python -m mypy .")
    if _uses_pytest(file_set, pyproject):
        pytest_prefix = (
            "uv run --all-packages "
            if "uv" in package_managers and _has_uv_workspace(pyproject)
            else prefix
        )
        commands.append(f"{pytest_prefix}python -m pytest")
    elif "tests" in {Path(file).parts[0] for file in file_set if Path(file).parts}:
        commands.append(f"{prefix}python -m unittest discover")
    return commands


def _python_runner_prefix(package_managers: tuple[str, ...]) -> str:
    if "uv" in package_managers:
        return "uv run "
    if "poetry" in package_managers:
        return "poetry run "
    if "pipenv" in package_managers:
        return "pipenv run "
    return ""


def _root_python_runtime_project(
    file_set: set[str], pyproject: dict[str, Any] | None
) -> bool:
    if not pyproject:
        return False
    if "project" in pyproject or "build-system" in pyproject:
        return True
    tool = pyproject.get("tool")
    if not isinstance(tool, dict):
        return False
    if "uv" in tool or "pytest" in json.dumps(tool).lower():
        return True
    return "setup.py" in file_set


def _uses_ruff(file_set: set[str], pyproject: dict[str, Any] | None) -> bool:
    if {"ruff.toml", ".ruff.toml"} & file_set:
        return True
    return bool(
        pyproject
        and isinstance(pyproject.get("tool"), dict)
        and "ruff" in pyproject["tool"]
    )


def _uses_mypy(file_set: set[str], pyproject: dict[str, Any] | None) -> bool:
    if {"mypy.ini", ".mypy.ini"} & file_set:
        return True
    return bool(
        pyproject
        and isinstance(pyproject.get("tool"), dict)
        and "mypy" in pyproject["tool"]
    )


def _uses_pytest(file_set: set[str], pyproject: dict[str, Any] | None) -> bool:
    if {"pytest.ini", "conftest.py"} & file_set:
        return True
    if pyproject and "pytest" in json.dumps(pyproject).lower():
        return True
    return any("pytest" in file.lower() for file in file_set if file.endswith((".txt", ".in")))


def _package_deps(package_json: dict[str, Any] | None) -> set[str]:
    if not package_json:
        return set()
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package_json.get(key)
        if isinstance(value, dict):
            deps.update(value)
    return deps


def _read_json(path: Path, root: Path) -> dict[str, Any] | None:
    if not is_inside_root(path, root):
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_toml(path: Path, root: Path) -> dict[str, Any] | None:
    if not is_inside_root(path, root):
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None


def _dedupe(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = re.sub(r"\s+", " ", value.strip())
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result
