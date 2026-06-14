from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .models import ProjectProfile
from .paths import is_inside_root

IGNORED_DIRS = {
    ".git",
    ".hg",
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
    "dist",
    "node_modules",
    "target",
    "venv",
}

COMPONENT_MARKERS = {
    ".buckconfig",
    ".terraform.lock.hcl",
    "BUILD",
    "BUILD.bazel",
    "Cargo.toml",
    "Gemfile",
    "Makefile",
    "MODULE.bazel",
    "Pipfile",
    "REPO.bazel",
    "WORKSPACE",
    "WORKSPACE.bazel",
    "composer.json",
    "build.gradle",
    "build.gradle.kts",
    "global.json",
    "go.mod",
    "go.work",
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


def detect_project(
    root: Path,
    *,
    explicit_package_manager: str | None = None,
    explicit_commands: tuple[str, ...] = (),
) -> ProjectProfile:
    root = root.resolve()
    files = tuple(list_project_files(root))
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
            "package.json",
            "pnpm-workspace.yaml",
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
            "MODULE.bazel",
            "MODULE.bazel.lock",
            "REPO.bazel",
            "WORKSPACE",
            "WORKSPACE.bazel",
            "pants.toml",
            "terragrunt.hcl",
            "Dockerfile",
            ".devcontainer/devcontainer.json",
        )
        if file in file_set
    )
    stack = _primary_stack(file_set, package_json, languages)
    commands = explicit_commands or _verification_commands(
        file_set,
        package_json,
        pyproject,
        cargo_toml,
        package_managers,
        stack,
    )
    components = _detect_components(file_set)
    workspace_markers = _detect_workspace_markers(
        root, file_set, package_json, pyproject, cargo_toml, composer_json
    )
    routing_markers = _detect_routing_markers(root, file_set)
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
    )


def list_project_files(root: Path, *, max_files: int = 4000) -> list[str]:
    results: list[str] = []

    def walk(current: Path, relative: str) -> None:
        if len(results) >= max_files:
            return
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            return
        for entry in entries:
            if len(results) >= max_files:
                return
            if entry.name in IGNORED_DIRS:
                continue
            rel = f"{relative}/{entry.name}" if relative else entry.name
            if entry.is_symlink():
                continue
            if entry.is_dir():
                walk(entry, rel)
            elif entry.is_file():
                results.append(rel)

    walk(root, "")
    return results


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
    package_manager = package_json.get("packageManager") if package_json else None
    if isinstance(package_manager, str):
        manager_name = package_manager.split("@", 1)[0].strip()
        if manager_name in {"bun", "npm", "pnpm", "yarn"}:
            managers.append(manager_name)
    if "bun.lock" in file_set or "bun.lockb" in file_set:
        managers.append("bun")
    if "pnpm-lock.yaml" in file_set or "pnpm-workspace.yaml" in file_set:
        managers.append("pnpm")
    if "yarn.lock" in file_set:
        managers.append("yarn")
    if "package-lock.json" in file_set or "package.json" in file_set:
        managers.append("npm")
    if "uv.lock" in file_set:
        managers.append("uv")
    if "poetry.lock" in file_set:
        managers.append("poetry")
    if "Cargo.toml" in file_set:
        managers.append("cargo")
    if "go.mod" in file_set:
        managers.append("go")
    return tuple(_dedupe(managers))


def _detect_components(file_set: set[str]) -> tuple[str, ...]:
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
    for directory in sorted(directories, key=lambda item: (item.count("/"), item)):
        markers = ", ".join(_dedupe(sorted(directories[directory])))
        components.append(f"{directory} ({markers})")
    return tuple(components[:80])


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
    for marker in (
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
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
    file_set: set[str], package_json: dict[str, Any] | None, languages: set[str]
) -> str:
    if {"MODULE.bazel", "REPO.bazel", "WORKSPACE", "WORKSPACE.bazel"} & file_set:
        return "bazel"
    if "pants.toml" in file_set:
        return "pants"
    if ".buckconfig" in file_set:
        return "buck"
    deps = _package_deps(package_json)
    if package_json:
        if {"react", "next", "@vitejs/plugin-react"} & deps or any(
            file.endswith(".tsx") for file in file_set
        ):
            return "typescript-react"
        if "typescript" in languages:
            return "typescript"
        return "node"
    priority = [
        ("python", "python"),
        ("go", "go"),
        ("rust", "rust"),
        ("java", "java"),
        ("dotnet", "dotnet"),
        ("php", "php"),
        ("ruby", "ruby"),
        ("terraform", "terraform"),
        ("docs", "docs"),
    ]
    for language, stack in priority:
        if language in languages:
            return stack
    return "generic"


def _verification_commands(
    file_set: set[str],
    package_json: dict[str, Any] | None,
    pyproject: dict[str, Any] | None,
    cargo_toml: dict[str, Any] | None,
    package_managers: tuple[str, ...],
    stack: str,
) -> tuple[str, ...]:
    commands: list[str] = []
    commands.extend(_make_commands(file_set))
    if package_json:
        commands.extend(_node_commands(package_json, package_managers))
    if stack == "python":
        commands.extend(_python_commands(file_set, pyproject, package_managers))
    if stack == "go":
        commands.append("go test ./...")
    if stack == "rust":
        rust_command = (
            "cargo test --workspace"
            if cargo_toml and "workspace" in cargo_toml
            else "cargo test"
        )
        commands.append(rust_command)
    if stack == "java":
        if "pom.xml" in file_set:
            commands.append("mvn test")
        if "gradlew" in file_set:
            commands.append("./gradlew test")
        elif "build.gradle" in file_set or "build.gradle.kts" in file_set:
            commands.append("gradle test")
    if stack == "dotnet":
        commands.append("dotnet test")
    if stack == "php" and "composer.json" in file_set:
        commands.append("composer test")
    if stack == "ruby":
        commands.append("bundle exec rake test")
    if stack == "terraform":
        commands.append("terraform fmt -check -recursive")
    if stack == "bazel":
        commands.append("bazel test //...")
    if stack == "pants":
        commands.append("pants test ::")
    if stack == "buck":
        commands.append("buck2 test //...")
    commands = _dedupe(commands)
    if not commands:
        commands = (
            'echo "No project verification check detected. Replace this line '
            'with the smallest reliable project check."',
        )
    return tuple(commands)


def _make_commands(file_set: set[str]) -> list[str]:
    makefile = "Makefile" if "Makefile" in file_set else "makefile" if "makefile" in file_set else ""
    if not makefile:
        return []
    # Keep this intentionally simple and side-effect-light.
    return ["make check"]


def _node_commands(
    package_json: dict[str, Any], package_managers: tuple[str, ...]
) -> list[str]:
    scripts = package_json.get("scripts")
    if not isinstance(scripts, dict):
        return []
    manager = next((item for item in package_managers if item in {"pnpm", "yarn", "bun", "npm"}), "npm")
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


def _python_commands(
    file_set: set[str],
    pyproject: dict[str, Any] | None,
    package_managers: tuple[str, ...],
) -> list[str]:
    prefix = "uv run " if "uv" in package_managers else ""
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
