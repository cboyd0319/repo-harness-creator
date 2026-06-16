#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)(?:\s*#\s*(.+))?\s*$")
PINNED_SPEC_RE = re.compile(
    r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?"
    r"==[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9_.+-]*)?$"
)
EXACT_PYTHON_RE = re.compile(
    r"^([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?"
    r"==([0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9_.+-]*)?)(?:\s*;.*)?$"
)
EXACT_NPM_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
EXACT_JVM_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)+(?:[-.][0-9A-Za-z]+)*$")
GRADLE_PLUGIN_RE = re.compile(
    r"\bid\s*(?:\(\s*)?['\"]([^'\"]+)['\"]\s*\)?\s*version\s*['\"]([^'\"]+)['\"]"
)
GRADLE_DEPENDENCY_RE = re.compile(
    r"\b(?:api|implementation|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly)"
    r"\s*(?:\(\s*)?['\"]([^:'\"]+):([^:'\"]+):([^'\")]+)['\"]"
)
PROFILE_IMAGE_RE = re.compile(
    r"(?:['\"]image['\"]|image)\s*[:=]\s*['\"]([^'\"]+)['\"]"
)
FORBIDDEN_BUILD_HOOKS = {"build.rs", "setup.py"}
CONTAINERFILE_NAMES = {"Containerfile", "Dockerfile"}
PYTHON_LEDGER_SECTIONS = ("python", "python_packages", "python_dependencies")
PACKAGE_LEDGER_SECTIONS = (
    "package_json",
    "node",
    "node_runtime",
    "agent_cli",
    "npm_packages",
)
INTEGRITY_LEDGER_SECTIONS = (
    "package_integrity",
    "npm_integrity",
    "agent_cli_integrity",
)
MAVEN_LEDGER_SECTIONS = ("maven_dependencies", "gradle_dependencies", "java_dependencies")
GRADLE_PLUGIN_LEDGER_SECTIONS = ("gradle_plugins", "java_plugins")
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
    ".harnessforge",
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
INTENTIONALLY_VULNERABLE_DIR_NAMES = {
    "intentionally-vulnerable",
    "intentionally_vulnerable",
    "vulnerable",
    "vulnerabilities",
    "dvwa",
    "securityshepherd",
    "juice-shop",
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
    ledger_failures, ledger = _load_pin_ledger(root)
    failures.extend(ledger_failures)
    failures.extend(_check_pyproject(root / "pyproject.toml", ledger, required=True))
    failures.extend(_check_action_pins(root))
    failures.extend(_check_container_pins(root, ledger))
    failures.extend(_check_python_requirements(root, ledger))
    failures.extend(_check_package_json_pins(root, ledger))
    failures.extend(_check_package_lock_integrity(root, ledger))
    failures.extend(_check_maven_pins(root, ledger))
    failures.extend(_check_gradle_pins(root, ledger))
    failures.extend(_check_profile_image_tags(root, ledger))
    failures.extend(_check_forbidden_build_hooks(root))
    return failures


def _load_pin_ledger(root: Path) -> tuple[list[str], dict[str, Any]]:
    path = root / "pins.toml"
    if not path.exists():
        return [], {}
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        return [f"pins.toml is invalid TOML: {error}"], {}
    return [], data


def _check_pyproject(
    path: Path, ledger: dict[str, Any], *, required: bool = True
) -> list[str]:
    if not path.exists():
        if not required:
            return []
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
            continue
        failures.extend(
            _check_python_requirement_ledger(
                "pyproject.toml build-system",
                requirement,
                ledger,
            )
        )
    python_ledger = _ledger_section(ledger, "python")
    minimum_supported = _ledger_string(python_ledger.get("minimum_supported"))
    project = data.get("project", {})
    if minimum_supported:
        requires_python = (
            project.get("requires-python") if isinstance(project, dict) else None
        )
        if (
            not isinstance(requires_python, str)
            or minimum_supported not in requires_python
        ):
            failures.append(
                "pyproject.toml requires-python should include "
                f"pins.toml python.minimum_supported {minimum_supported!r}"
            )
    dependencies = data.get("project", {}).get("dependencies", [])
    if isinstance(dependencies, list):
        for requirement in dependencies:
            if not _is_exact_or_non_registry(requirement):
                failures.append(
                    "project dependency must use an exact pin or direct URL: "
                    f"{requirement!r}"
                )
                continue
            failures.extend(
                _check_python_requirement_ledger(
                    "pyproject.toml project dependency",
                    requirement,
                    ledger,
                )
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
                    continue
                failures.extend(
                    _check_python_requirement_ledger(
                        f"pyproject.toml optional dependency {group!r}",
                        requirement,
                        ledger,
                    )
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
            if ref.startswith(("./", "../", "docker://")):
                continue
            if "@" not in ref:
                failures.append(
                    f"{relative}:{number} action reference has no @ pin: {ref}"
                )
                continue
            action, version = ref.rsplit("@", 1)
            if "/" not in action:
                failures.append(
                    f"{relative}:{number} action owner/repo is invalid: {ref}"
                )
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


def _check_container_pins(root: Path, ledger: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    has_ledger = "container_images" in ledger
    ledger_entries = _container_ledger_entries(ledger)
    for path in _walk_named_files(root, CONTAINERFILE_NAMES):
        relative = path.relative_to(root)
        lines = path.read_text(encoding="utf-8").splitlines()
        stage_aliases = _container_stage_aliases(lines)
        for number, line in enumerate(lines, 1):
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
            if image.lower() in stage_aliases:
                continue
            if image.lower() != "scratch" and "@sha256:" not in image:
                failures.append(
                    f"{relative}:{number} container base image should use "
                    "@sha256 digest"
                )
                continue
            if image.lower() != "scratch" and has_ledger:
                parsed = _parse_container_image(image)
                if parsed is None or not _container_image_in_ledger(
                    parsed, ledger_entries
                ):
                    failures.append(
                        f"{relative}:{number} container image {image!r} is not "
                        "recorded in pins.toml [container_images]"
                    )
    return failures


def _container_stage_aliases(lines: list[str]) -> set[str]:
    aliases: set[str] = set()
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 4 or not parts or parts[0] != "FROM":
            continue
        for index, part in enumerate(parts):
            if part.upper() == "AS" and index + 1 < len(parts):
                aliases.add(parts[index + 1].lower())
                break
    return aliases


def _check_python_requirements(root: Path, ledger: dict[str, Any]) -> list[str]:
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
            if _parse_exact_python_pin(requirement) is None:
                failures.append(
                    f"{relative}:{number} Python requirement should use an exact == pin"
                )
                continue
            failures.extend(
                _check_python_requirement_ledger(
                    f"{relative}:{number} Python requirement",
                    requirement,
                    ledger,
                )
            )
    return failures


def _check_package_json_pins(root: Path, ledger: dict[str, Any]) -> list[str]:
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
                    continue
                if isinstance(version, str) and not _is_non_registry_spec(version):
                    failures.extend(
                        _check_package_version_ledger(
                            f"{relative}: {section}.{name}",
                            name,
                            version.strip(),
                            ledger,
                        )
                    )
    return failures


def _check_package_lock_integrity(root: Path, ledger: dict[str, Any]) -> list[str]:
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
        direct_names = _package_lock_direct_names(data, packages)
        for package_path, details in sorted(packages.items()):
            if not package_path.startswith("node_modules/"):
                continue
            if not isinstance(details, dict):
                failures.append(
                    f"{relative}: invalid package-lock entry {package_path}"
                )
                continue
            version = details.get("version")
            resolved = details.get("resolved")
            integrity = details.get("integrity")
            label = details.get("name") or package_path.removeprefix("node_modules/")
            if not isinstance(version, str) or not version:
                failures.append(
                    f"{relative}: package-lock entry {label} has no version"
                )
            if not isinstance(resolved, str) or not resolved.startswith(
                "https://registry.npmjs.org/"
            ):
                failures.append(
                    f"{relative}: package-lock entry {label} has no npm "
                    "registry tarball"
                )
            if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
                failures.append(
                    f"{relative}: package-lock entry {label} has no sha512 integrity"
                )
            failures.extend(
                _check_package_integrity_ledger(
                    relative,
                    label,
                    integrity,
                    direct_names,
                    ledger,
                )
            )
    return failures


def _check_maven_pins(root: Path, ledger: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, {"pom.xml"}):
        relative = path.relative_to(root)
        try:
            tree = ElementTree.parse(path)
        except (ElementTree.ParseError, OSError) as error:
            failures.append(f"{relative}: invalid Maven XML: {error}")
            continue
        root_element = tree.getroot()
        properties = _maven_properties(root_element)
        for dependency in root_element.iter():
            if _xml_local_name(dependency.tag) != "dependency":
                continue
            group_id = _child_text(dependency, "groupId")
            artifact_id = _child_text(dependency, "artifactId")
            version = _resolve_maven_property(
                _child_text(dependency, "version"), properties
            )
            if not group_id or not artifact_id or not version:
                continue
            coordinate = f"{group_id}:{artifact_id}"
            label = f"{relative}: Maven dependency {coordinate}"
            if not _is_exact_jvm_version(version):
                failures.append(f"{label} should use an exact version: {version!r}")
                continue
            failures.extend(
                _check_jvm_ledger(label, coordinate, version, ledger, MAVEN_LEDGER_SECTIONS)
            )
    return failures


def _check_gradle_pins(root: Path, ledger: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for path in _walk_named_files(root, {"build.gradle", "build.gradle.kts"}):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for plugin_id, version in GRADLE_PLUGIN_RE.findall(text):
            label = f"{relative}: Gradle plugin {plugin_id}"
            if not _is_exact_jvm_version(version):
                failures.append(f"{label} should use an exact version: {version!r}")
                continue
            failures.extend(
                _check_jvm_ledger(
                    label,
                    plugin_id,
                    version,
                    ledger,
                    GRADLE_PLUGIN_LEDGER_SECTIONS,
                )
            )
        for group_id, artifact_id, version in GRADLE_DEPENDENCY_RE.findall(text):
            coordinate = f"{group_id}:{artifact_id}"
            label = f"{relative}: Gradle dependency {coordinate}"
            if not _is_exact_jvm_version(version):
                failures.append(f"{label} should use an exact version: {version!r}")
                continue
            failures.extend(
                _check_jvm_ledger(label, coordinate, version, ledger, MAVEN_LEDGER_SECTIONS)
            )
    return failures


def _check_profile_image_tags(root: Path, ledger: dict[str, Any]) -> list[str]:
    if "profile_images" not in ledger:
        return []
    ledger_images = _profile_ledger_images(ledger)
    found_images: set[str] = set()
    failures: list[str] = []
    profile_files = {"profiles.py", "profiles.toml", "profiles.json"}
    for path in _walk_named_files(root, profile_files):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for image in PROFILE_IMAGE_RE.findall(text):
            found_images.add(image)
            if image not in ledger_images:
                failures.append(
                    f"{relative}: profile image {image!r} is not recorded in "
                    "pins.toml [profile_images]"
                )
    if found_images:
        for image in sorted(ledger_images - found_images):
            failures.append(
                f"pins.toml [profile_images] entry {image!r} is not used by "
                "profile files"
            )
    return failures


def _check_python_requirement_ledger(
    label: str,
    requirement: object,
    ledger: dict[str, Any],
) -> list[str]:
    if not ledger:
        return []
    parsed = _parse_exact_python_pin(requirement)
    if parsed is None:
        return []
    name, version = parsed
    ledger_pin = _lookup_ledger_value(ledger, PYTHON_LEDGER_SECTIONS, name)
    if ledger_pin is None:
        return [
            f"{label} {requirement!r} is not recorded in pins.toml "
            "[python/python_packages/python_dependencies]"
        ]
    if ledger_pin != version:
        return [
            f"{label} {name}=={version} does not match pins.toml value "
            f"{ledger_pin!r}"
        ]
    return []


def _check_package_version_ledger(
    label: str,
    package_name: str,
    version: str,
    ledger: dict[str, Any],
) -> list[str]:
    if not ledger:
        return []
    ledger_pin = _lookup_ledger_value(ledger, PACKAGE_LEDGER_SECTIONS, package_name)
    if ledger_pin is None:
        return [
            f"{label} {version!r} is not recorded in pins.toml "
            "[package_json/node/node_runtime/agent_cli/npm_packages]"
        ]
    if ledger_pin != version:
        return [
            f"{label} version {version!r} does not match pins.toml value "
            f"{ledger_pin!r}"
        ]
    return []


def _check_package_integrity_ledger(
    relative: Path,
    package_name: str,
    integrity: object,
    direct_names: set[str],
    ledger: dict[str, Any],
) -> list[str]:
    if not ledger:
        return []
    ledger_integrity = _lookup_ledger_value(
        ledger,
        INTEGRITY_LEDGER_SECTIONS,
        package_name,
        field="integrity",
    )
    if package_name not in direct_names and ledger_integrity is None:
        return []
    if ledger_integrity is None:
        return [
            f"{relative}: package-lock integrity for {package_name} is not "
            "recorded in pins.toml [package_integrity/npm_integrity/"
            "agent_cli_integrity]"
        ]
    if integrity != ledger_integrity:
        return [
            f"{relative}: package-lock integrity for {package_name} does not "
            f"match pins.toml value {ledger_integrity!r}"
        ]
    return []


def _check_jvm_ledger(
    label: str,
    name: str,
    version: str,
    ledger: dict[str, Any],
    sections: tuple[str, ...],
) -> list[str]:
    if not ledger:
        return []
    ledger_pin = _lookup_ledger_value(ledger, sections, name)
    if ledger_pin is None:
        return [f"{label} {version!r} is not recorded in pins.toml {sections}"]
    if ledger_pin != version:
        return [
            f"{label} version {version!r} does not match pins.toml value "
            f"{ledger_pin!r}"
        ]
    return []


def _maven_properties(root_element: ElementTree.Element) -> dict[str, str]:
    properties: dict[str, str] = {}
    for child in root_element:
        if _xml_local_name(child.tag) != "properties":
            continue
        for property_node in child:
            if property_node.text and property_node.text.strip():
                properties[_xml_local_name(property_node.tag)] = property_node.text.strip()
    return properties


def _resolve_maven_property(value: str, properties: dict[str, str]) -> str:
    if value.startswith("${") and value.endswith("}"):
        return properties.get(value[2:-1], value)
    return value


def _child_text(element: ElementTree.Element, name: str) -> str:
    for child in element:
        if _xml_local_name(child.tag) == name and child.text:
            return child.text.strip()
    return ""


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_exact_python_pin(requirement: object) -> tuple[str, str] | None:
    if not isinstance(requirement, str):
        return None
    text = requirement.strip()
    if " @ " in text:
        return None
    match = EXACT_PYTHON_RE.match(text)
    if not match:
        return None
    return match.group(1), match.group(2)


def _is_exact_jvm_version(version: str) -> bool:
    value = version.strip()
    if not EXACT_JVM_RE.match(value):
        return False
    return not any(token in value.upper() for token in ("SNAPSHOT", "LATEST", "RELEASE"))


def _ledger_section(ledger: dict[str, Any], section: str) -> dict[str, Any]:
    value = ledger.get(section, {})
    if isinstance(value, dict):
        return value
    return {}


def _lookup_ledger_value(
    ledger: dict[str, Any],
    sections: tuple[str, ...],
    package_name: str,
    *,
    field: str = "version",
) -> str | None:
    candidates = _ledger_key_candidates(package_name)
    for section_name in sections:
        section = _ledger_section(ledger, section_name)
        for candidate in candidates:
            if candidate not in section:
                continue
            value = _ledger_string_or_field(section[candidate], field)
            if value is not None:
                return value
    return None


def _ledger_string_or_field(value: object, field: str) -> str | None:
    direct = _ledger_string(value)
    if direct is not None:
        return direct
    if not isinstance(value, dict):
        return None
    for key in (field, "version", "value"):
        item = _ledger_string(value.get(key))
        if item is not None:
            return item
    return None


def _ledger_string(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _ledger_key_candidates(package_name: str) -> tuple[str, ...]:
    candidates: list[str] = []
    base = package_name.rsplit("/", maxsplit=1)[-1].removeprefix("@")
    for value in (package_name, base):
        if value and value not in candidates:
            candidates.append(value)
        normalized = _normalize_ledger_key(value)
        if normalized and normalized not in candidates:
            candidates.append(normalized)
    base_normalized = _normalize_ledger_key(base)
    if base_normalized and not base_normalized.endswith("_cli"):
        cli_name = f"{base_normalized}_cli"
        if cli_name not in candidates:
            candidates.append(cli_name)
    return tuple(candidates)


def _normalize_ledger_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _container_ledger_entries(ledger: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for value in _ledger_section(ledger, "container_images").values():
        if isinstance(value, str):
            parsed = _parse_container_image(value)
            if parsed is not None:
                entries.append(parsed)
            continue
        if not isinstance(value, dict):
            continue
        image = _ledger_string(value.get("image")) or _ledger_string(
            value.get("repository")
        )
        tag = _ledger_string(value.get("tag"))
        digest = _ledger_string(value.get("digest"))
        if image and "@sha256:" in image:
            parsed = _parse_container_image(image)
            if parsed is not None:
                if tag:
                    parsed["tag"] = tag
                if digest:
                    parsed["digest"] = digest
                entries.append(parsed)
            continue
        if tag and digest:
            entry = {"tag": tag, "digest": _normalize_sha256_digest(digest)}
            if image:
                entry["repository"] = image
            entries.append(entry)
    return entries


def _parse_container_image(image: str) -> dict[str, str] | None:
    if "@sha256:" not in image:
        return None
    repository_tag, digest_suffix = image.split("@sha256:", maxsplit=1)
    digest = f"sha256:{digest_suffix}"
    repository = repository_tag
    tag = ""
    last_segment = repository_tag.rsplit("/", maxsplit=1)[-1]
    if ":" in last_segment:
        repository, tag = repository_tag.rsplit(":", maxsplit=1)
    parsed = {
        "repository": repository,
        "repository_key": _normalize_container_repository(repository),
        "tag": tag,
        "digest": digest,
    }
    return parsed


def _container_image_in_ledger(
    image: dict[str, str], entries: list[dict[str, str]]
) -> bool:
    for entry in entries:
        if entry.get("tag") != image.get("tag"):
            continue
        if entry.get("digest") != image.get("digest"):
            continue
        repository = entry.get("repository")
        if not repository:
            return True
        if _normalize_container_repository(repository) == image.get("repository_key"):
            return True
    return False


def _normalize_container_repository(repository: str) -> str:
    if repository.startswith("docker.io/library/"):
        return repository.removeprefix("docker.io/library/")
    if repository.startswith("library/"):
        return repository.removeprefix("library/")
    return repository


def _normalize_sha256_digest(digest: str) -> str:
    if digest.startswith("sha256:"):
        return digest
    return f"sha256:{digest}"


def _package_lock_direct_names(
    data: dict[str, Any], packages: dict[str, Any]
) -> set[str]:
    names: set[str] = set()
    root_package = packages.get("")
    if isinstance(root_package, dict):
        for key in ("dependencies", "devDependencies", "optionalDependencies"):
            dependencies = root_package.get(key, {})
            if isinstance(dependencies, dict):
                names.update(str(name) for name in dependencies)
    top_level_dependencies = data.get("dependencies", {})
    if isinstance(top_level_dependencies, dict):
        names.update(str(name) for name in top_level_dependencies)
    return names


def _profile_ledger_images(ledger: dict[str, Any]) -> set[str]:
    images: set[str] = set()
    for value in _ledger_section(ledger, "profile_images").values():
        direct = _ledger_string(value)
        if direct:
            images.add(direct)
            continue
        if not isinstance(value, dict):
            continue
        image = _ledger_string(value.get("image"))
        tag = _ledger_string(value.get("tag"))
        value_field = _ledger_string(value.get("value"))
        if value_field:
            images.add(value_field)
        if image and tag:
            separator = "" if image.endswith(":") else ":"
            images.add(f"{image}{separator}{tag}")
        elif image:
            images.add(image)
        elif tag:
            images.add(tag)
    return images


def _check_forbidden_build_hooks(root: Path) -> list[str]:
    failures: list[str] = []
    has_rust = bool(_walk_named_files(root, {"Cargo.toml"}))
    for path in _walk_named_files(root, FORBIDDEN_BUILD_HOOKS):
        relative = path.relative_to(root)
        if path.name == "build.rs" and has_rust:
            continue
        failures.append(f"build hook file is not allowed in this repo: {relative}")
    return failures


def _is_exact_or_non_registry(requirement: object) -> bool:
    if not isinstance(requirement, str):
        return False
    text = requirement.strip()
    if " @ " in text:
        return True
    return _parse_exact_python_pin(text) is not None


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
            directory
            for directory in directories
            if directory not in SCAN_SKIP_DIRS
            and directory.lower() not in INTENTIONALLY_VULNERABLE_DIR_NAMES
        ]
        yield current, directories, names


def _is_exact_npm_version(version: object) -> bool:
    if not isinstance(version, str):
        return False
    value = version.strip()
    if _is_non_registry_spec(value):
        return True
    return bool(EXACT_NPM_RE.match(value))


def _is_non_registry_spec(version: str) -> bool:
    return version.strip().startswith(NON_REGISTRY_PREFIXES)


if __name__ == "__main__":
    raise SystemExit(main())
