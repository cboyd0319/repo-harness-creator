#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)(?:\s*#\s*(.+))?\s*$")
PINNED_SPEC_RE = re.compile(
    r"^[A-Za-z0-9_.-]+==[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9_.+-]*)?$"
)
EXACT_NPM_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
FORBIDDEN_BUILD_HOOKS = {"build.rs", "setup.py"}
CONTAINERFILE_NAMES = {"Containerfile", "Dockerfile"}
NON_REGISTRY_PREFIXES = (
    "file:",
    "git+",
    "github:",
    "http://",
    "https://",
    "link:",
    "portal:",
    "workspace:",
)
SCAN_SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check hard pins for repo tooling.")
    parser.add_argument("--root", default=".", help="Repository root to check.")
    args = parser.parse_args(argv)

    failures = check_root(Path(args.root))
    if failures:
        print("Pin check failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Pin check passed.")
    return 0


def check_root(root: Path) -> list[str]:
    root = root.resolve()
    failures: list[str] = []
    failures.extend(_check_pyproject(root / "pyproject.toml"))
    failures.extend(_check_action_pins(root))
    failures.extend(_check_container_pins(root))
    failures.extend(_check_python_requirements(root))
    failures.extend(_check_package_json_pins(root))
    failures.extend(_check_package_lock_integrity(root))
    failures.extend(_check_forbidden_build_hooks(root))
    return failures


def _check_pyproject(path: Path) -> list[str]:
    if not path.exists():
        return ["pyproject.toml is missing"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    build_requires = data.get("build-system", {}).get("requires", [])
    failures: list[str] = []
    if not isinstance(build_requires, list) or not build_requires:
        failures.append("pyproject.toml build-system.requires must be non-empty")
        return failures
    for requirement in build_requires:
        if not isinstance(requirement, str) or not PINNED_SPEC_RE.match(requirement):
            failures.append(
                "pyproject.toml build-system requirement must use an exact pin: "
                f"{requirement!r}"
            )
    dependencies = data.get("project", {}).get("dependencies", [])
    if isinstance(dependencies, list):
        for requirement in dependencies:
            if not _is_exact_or_non_registry(requirement):
                failures.append(
                    "project dependency must use an exact pin or direct URL: "
                    f"{requirement!r}"
                )
    optional = data.get("project", {}).get("optional-dependencies", {})
    if isinstance(optional, dict):
        for group, requirements in optional.items():
            if not isinstance(requirements, list):
                continue
            for requirement in requirements:
                if not _is_exact_or_non_registry(requirement):
                    failures.append(
                        f"optional dependency {group!r} must use an exact pin "
                        f"or direct URL: {requirement!r}"
                    )
    return failures


def _check_action_pins(root: Path) -> list[str]:
    files = [root / "action.yml"]
    workflows = root / ".github" / "workflows"
    if workflows.exists():
        files.extend(sorted(workflows.glob("*.yml")))
        files.extend(sorted(workflows.glob("*.yaml")))
    failures: list[str] = []
    for path in files:
        if not path.exists():
            continue
        relative = path.relative_to(root)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = USES_RE.match(line)
            if not match:
                continue
            ref = match.group(1).strip("'\"")
            comment = (match.group(2) or "").strip()
            if ref.startswith("./") or ref.startswith("../") or ref.startswith("docker://"):
                continue
            if "@" not in ref:
                failures.append(f"{relative}:{number} action reference has no @ pin: {ref}")
                continue
            action, version = ref.rsplit("@", 1)
            if "/" not in action:
                failures.append(f"{relative}:{number} action owner/repo is invalid: {ref}")
                continue
            if not SHA_RE.match(version):
                failures.append(
                    f"{relative}:{number} external action must use a 40-char SHA: {ref}"
                )
            if not comment:
                failures.append(
                    f"{relative}:{number} SHA-pinned action needs a version comment"
                )
    return failures


def _check_container_pins(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, CONTAINERFILE_NAMES):
        relative = path.relative_to(root)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = line.strip()
            if not value.startswith("FROM "):
                continue
            parts = value.split()
            image_index = 1
            while image_index < len(parts) and parts[image_index].startswith("--"):
                image_index += 1
            if image_index >= len(parts):
                failures.append(f"{relative}:{number} container FROM has no image")
                continue
            image = parts[image_index]
            if image.lower() != "scratch" and "@sha256:" not in image:
                failures.append(
                    f"{relative}:{number} container base image should use @sha256 digest"
                )
    return failures


def _check_python_requirements(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _walk_matching_files(root, "requirements*.txt"):
        relative = path.relative_to(root)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            if value.startswith(("-r ", "--", "-e ")) or " @ " in value:
                continue
            requirement = value.split(";", maxsplit=1)[0].strip()
            if "==" not in requirement:
                failures.append(
                    f"{relative}:{number} Python requirement should use an exact == pin"
                )
    return failures


def _check_package_json_pins(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, {"package.json"}):
        relative = path.relative_to(root)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            failures.append(f"{relative}: invalid JSON: {error.msg}")
            continue
        if not isinstance(data, dict):
            continue
        for section in ("dependencies", "devDependencies", "optionalDependencies"):
            dependencies = data.get(section, {})
            if not isinstance(dependencies, dict):
                continue
            for name, version in sorted(dependencies.items()):
                if not _is_exact_npm_version(version):
                    failures.append(
                        f"{relative}: {section}.{name} should use an exact npm version"
                    )
    return failures


def _check_package_lock_integrity(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, {"package-lock.json"}):
        relative = path.relative_to(root)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            failures.append(f"{relative}: invalid JSON: {error.msg}")
            continue
        packages = data.get("packages", {}) if isinstance(data, dict) else {}
        if not isinstance(packages, dict):
            continue
        for package_path, details in sorted(packages.items()):
            if not package_path.startswith("node_modules/"):
                continue
            if not isinstance(details, dict):
                failures.append(f"{relative}: invalid package-lock entry {package_path}")
                continue
            version = details.get("version")
            resolved = details.get("resolved")
            integrity = details.get("integrity")
            label = details.get("name") or package_path.removeprefix("node_modules/")
            if not isinstance(version, str) or not version:
                failures.append(f"{relative}: package-lock entry {label} has no version")
            if not isinstance(resolved, str) or not resolved.startswith(
                "https://registry.npmjs.org/"
            ):
                failures.append(
                    f"{relative}: package-lock entry {label} has no npm registry tarball"
                )
            if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
                failures.append(f"{relative}: package-lock entry {label} has no sha512 integrity")
    return failures


def _check_forbidden_build_hooks(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, FORBIDDEN_BUILD_HOOKS):
        relative = path.relative_to(root)
        failures.append(f"build hook file is not allowed in this repo: {relative}")
    return failures


def _is_exact_or_non_registry(requirement: object) -> bool:
    if not isinstance(requirement, str):
        return False
    text = requirement.strip()
    if " @ " in text:
        return True
    name = re.split(r"[<>=!~;\[]", text, maxsplit=1)[0].strip()
    if not name:
        return False
    return text.startswith(f"{name}==")


def _walk_named_files(root: Path, names: set[str]) -> list[Path]:
    matches: list[Path] = []
    for current, _directories, filenames in _walk_repo(root):
        directory = Path(current)
        for name in sorted(filenames):
            if name in names:
                matches.append(directory / name)
    return matches


def _walk_matching_files(root: Path, pattern: str) -> list[Path]:
    matches: list[Path] = []
    for current, _directories, filenames in _walk_repo(root):
        directory = Path(current)
        for name in sorted(filenames):
            path = directory / name
            if path.match(pattern):
                matches.append(path)
    return matches


def _walk_repo(root: Path):
    for current, directories, names in os.walk(root):
        directories[:] = [
            directory for directory in directories if directory not in SCAN_SKIP_DIRS
        ]
        yield current, directories, names


def _is_exact_npm_version(version: object) -> bool:
    if not isinstance(version, str):
        return False
    value = version.strip()
    if value.startswith(NON_REGISTRY_PREFIXES):
        return True
    return bool(EXACT_NPM_RE.match(value))


if __name__ == "__main__":
    raise SystemExit(main())
