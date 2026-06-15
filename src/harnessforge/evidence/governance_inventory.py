from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


MCP_CONFIGS = (
    ".mcp.json",
    ".github/copilot/mcp.json",
    ".cursor/mcp.json",
    ".continue/config.json",
)

AGENT_SETTINGS = (
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".codex/config.toml",
    ".aider.conf.yml",
    ".aider.conf.yaml",
)

AGENT_SETUP_WORKFLOWS = (
    ".github/workflows/copilot-setup-steps.yml",
    ".github/workflows/copilot-setup-steps.yaml",
)

AGENT_PLUGIN_MANIFESTS = {
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
}

ROOT_INSTALLER_SCRIPTS = {
    "bootstrap.ps1",
    "bootstrap.sh",
    "install.ps1",
    "install.sh",
    "setup.ps1",
    "setup.sh",
}

HOOK_CONFIGS = {
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "pre-commit-config.yaml",
    "pre-commit-config.yml",
    "lefthook.yaml",
    "lefthook.yml",
}

HOOK_DIRS = {
    ".githooks",
    ".git-hooks",
    ".hooks",
    ".husky",
    "git-hooks",
    "githooks",
}

AGENT_HOOK_DIRS = {
    (".claude", "hooks"),
}

HOOK_NAMES = {
    "applypatch-msg",
    "commit-msg",
    "post-applypatch",
    "post-checkout",
    "post-commit",
    "post-merge",
    "post-receive",
    "post-rewrite",
    "pre-applypatch",
    "pre-commit",
    "pre-merge-commit",
    "pre-push",
    "pre-rebase",
    "pre-receive",
    "prepare-commit-msg",
    "update",
}

ENV_TEMPLATE_NAMES = {
    ".env.example",
    ".env.sample",
    "env.example",
    "env.sample",
    "example.env",
    "sample.env",
}

ENV_LOCAL_PREFIXES = (
    ".env",
    "env.local",
)

CONFIG_SUFFIXES = {".json", ".toml", ".yaml", ".yml"}
CONTAINER_RUNTIME_FILES = {
    "Containerfile",
    "Dockerfile",
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
}


@dataclass(frozen=True)
class GovernanceItem:
    path: str
    category: str
    surfaces: tuple[str, ...]
    review_required: tuple[str, ...]


@dataclass(frozen=True)
class GovernanceInventoryReport:
    items: tuple[GovernanceItem, ...]
    warnings: tuple[str, ...]
    review_required: tuple[str, ...]


def analyze_governance_inventory(files: tuple[str, ...]) -> GovernanceInventoryReport:
    items = tuple(
        item
        for item in (_governance_item(file) for file in sorted(files))
        if item is not None
    )
    warnings: list[str] = []
    if items:
        warnings.append(
            f"governance inventory detected {len(items)} permission, "
            "environment, or agent-control surface(s)."
        )
    review_required: list[str] = []
    for item in items:
        review_required.extend(item.review_required)
    return GovernanceInventoryReport(
        items=items,
        warnings=tuple(warnings),
        review_required=tuple(_dedupe(review_required)),
    )


def governance_item_to_dict(item: GovernanceItem) -> dict[str, Any]:
    return {
        "path": item.path,
        "category": item.category,
        "surfaces": list(item.surfaces),
        "reviewRequired": list(item.review_required),
    }


def _governance_item(file: str) -> GovernanceItem | None:
    if file in MCP_CONFIGS:
        return GovernanceItem(
            path=file,
            category="mcp-config",
            surfaces=("server-trust", "external-tools"),
            review_required=(
                f"MCP configuration detected at {file}; review server scopes and trust.",
            ),
        )
    if file in AGENT_SETTINGS:
        return GovernanceItem(
            path=file,
            category="agent-settings",
            surfaces=("tool-permissions", "path-access"),
            review_required=(
                f"Agent permission/settings file detected at {file}; review tool and path access.",
            ),
        )
    if file in AGENT_SETUP_WORKFLOWS:
        return GovernanceItem(
            path=file,
            category="agent-setup-workflow",
            surfaces=("runner-setup", "credential-scope"),
            review_required=(
                f"GitHub agent setup workflow detected at {file}; review before agent use.",
            ),
        )
    if file in AGENT_PLUGIN_MANIFESTS:
        return GovernanceItem(
            path=file,
            category="agent-plugin",
            surfaces=("agent-distribution", "platform-installation"),
            review_required=(
                f"agent plugin manifest detected at {file}; review distributed "
                "skills, commands, and installation scope.",
            ),
        )
    if _is_agent_skill(file):
        return GovernanceItem(
            path=file,
            category="agent-skill",
            surfaces=("instruction-surface", "agent-capability"),
            review_required=(
                f"agent skill detected at {file}; review trigger scope and "
                "tool expectations before agent use.",
            ),
        )
    if _is_root_installer_script(file):
        return GovernanceItem(
            path=file,
            category="installer-script",
            surfaces=("local-installation", "external-write", "dependency-setup"),
            review_required=(
                f"installer script detected at {file}; review filesystem writes "
                "and dependency setup before running.",
            ),
        )
    if _is_hook(file):
        return GovernanceItem(
            path=file,
            category="hook",
            surfaces=("execution-trigger", "repo-mutation", "credential-exposure"),
            review_required=(
                f"hook detected at {file}; review commands, secrets, and mutation behavior.",
            ),
        )
    if _is_devcontainer(file):
        return GovernanceItem(
            path=file,
            category="devcontainer",
            surfaces=("container-runtime", "mounts", "post-create-commands"),
            review_required=(
                f"devcontainer detected at {file}; review container features, "
                "mounts, and post-create commands.",
            ),
        )
    if _is_container_runtime(file):
        return GovernanceItem(
            path=file,
            category="container-runtime",
            surfaces=("image-build", "runtime-isolation", "filesystem-mounts"),
            review_required=(
                f"container runtime file detected at {file}; review base images, "
                "mounts, network access, and post-start commands.",
            ),
        )
    if _is_sandbox_config(file):
        return GovernanceItem(
            path=file,
            category="sandbox",
            surfaces=("execution-boundary", "filesystem-boundary"),
            review_required=(
                f"sandbox configuration detected at {file}; review execution "
                "and filesystem boundaries.",
            ),
        )
    if _is_env_template(file):
        return GovernanceItem(
            path=file,
            category="environment-template",
            surfaces=("secret-shape", "local-environment"),
            review_required=(
                f"environment template detected at {file}; review secret names "
                "and default values.",
            ),
        )
    if _is_local_env(file):
        return GovernanceItem(
            path=file,
            category="environment-local",
            surfaces=("local-secrets", "local-environment"),
            review_required=(
                f"local environment file detected at {file}; review secret "
                "exposure before agent use.",
            ),
        )
    return None


def _is_devcontainer(file: str) -> bool:
    path = Path(file)
    return file == ".devcontainer.json" or (
        path.parts[:1] == (".devcontainer",)
        and path.suffix.lower() in CONFIG_SUFFIXES
    )


def _is_container_runtime(file: str) -> bool:
    return Path(file).name in CONTAINER_RUNTIME_FILES


def _is_sandbox_config(file: str) -> bool:
    path = Path(file)
    return path.suffix.lower() in CONFIG_SUFFIXES and (
        any(part in {".sandbox", "sandbox"} for part in path.parts)
        or "sandbox" in path.name.lower()
    )


def _is_hook(file: str) -> bool:
    path = Path(file)
    parts = path.parts
    if path.name.lower() in HOOK_CONFIGS:
        return True
    if len(parts) >= 2 and tuple(parts[:2]) in AGENT_HOOK_DIRS:
        return True
    return bool(parts) and parts[0] in HOOK_DIRS and path.name.lower() in HOOK_NAMES


def _is_agent_skill(file: str) -> bool:
    path = Path(file)
    parts = path.parts
    return path.name == "SKILL.md" and (
        len(parts) >= 3
        and (
            parts[0] == "skills"
            or parts[:2] in {(".claude", "skills"), (".codex", "skills")}
        )
    )


def _is_root_installer_script(file: str) -> bool:
    path = Path(file)
    return len(path.parts) == 1 and path.name.lower() in ROOT_INSTALLER_SCRIPTS


def _is_env_template(file: str) -> bool:
    return Path(file).name.lower() in ENV_TEMPLATE_NAMES


def _is_local_env(file: str) -> bool:
    name = Path(file).name.lower()
    return name in {".env", "env.local"} or any(
        name.startswith(prefix + ".") for prefix in ENV_LOCAL_PREFIXES
    )


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
