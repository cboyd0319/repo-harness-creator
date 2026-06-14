#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)(?:\s*#\s*(.+))?\s*$")
PINNED_SPEC_RE = re.compile(
    r"^[A-Za-z0-9_.-]+==[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9_.+-]*)?$"
)


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


if __name__ == "__main__":
    raise SystemExit(main())
