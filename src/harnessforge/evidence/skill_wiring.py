from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.harness_paths import HARNESS_SKILL_PATH, HARNESS_SKILL_REFERENCE_PATH
from ..core.paths import is_inside_root, path_from_relative_text

SCHEMA_VERSION = "harnessforge.skillWiring.v1"
INSTRUCTION_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
)
HARNESS_MARKERS = (
    "docs/harness/manifest.json",
    "docs/harness/README.md",
    "docs/harness/state/first-agent-task.md",
    "docs/harness/evidence/first-agent-review.json",
    HARNESS_SKILL_PATH,
    HARNESS_SKILL_REFERENCE_PATH,
)
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
REFERENCE_RE = re.compile(r"`(?P<path>\.\./\.\./\.\./[^`]+)`")


@dataclass(frozen=True)
class SkillWiringReport:
    status: str
    skill_path: str
    reference_path: str
    instruction_routes: tuple[str, ...]
    resolved_references: tuple[str, ...]
    frontmatter: dict[str, str]
    warnings: tuple[str, ...]
    next_actions: tuple[str, ...]


def analyze_skill_wiring(root: Path, files: tuple[str, ...]) -> SkillWiringReport:
    root = root.resolve()
    file_set = set(files)
    expected = _harness_expected(file_set, root)
    if not expected:
        return SkillWiringReport(
            status="not_applicable",
            skill_path=HARNESS_SKILL_PATH,
            reference_path=HARNESS_SKILL_REFERENCE_PATH,
            instruction_routes=(),
            resolved_references=(),
            frontmatter={},
            warnings=(),
            next_actions=(),
        )

    warnings: list[str] = []
    resolved_references: list[str] = []
    frontmatter: dict[str, str] = {}
    skill_text = _read_text(root, HARNESS_SKILL_PATH)
    reference_text = _read_text(root, HARNESS_SKILL_REFERENCE_PATH)
    instruction_routes = _instruction_routes(root, file_set)

    if skill_text is None:
        warnings.append(f"{HARNESS_SKILL_PATH} is missing.")
    else:
        frontmatter, frontmatter_warnings = _frontmatter(skill_text)
        warnings.extend(frontmatter_warnings)
        expected_name = Path(HARNESS_SKILL_PATH).parent.name
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if name != expected_name:
            warnings.append(
                f"{HARNESS_SKILL_PATH} frontmatter name must be {expected_name}."
            )
        if name and not SKILL_NAME_RE.fullmatch(name):
            warnings.append(f"{HARNESS_SKILL_PATH} frontmatter name is invalid.")
        if not description:
            warnings.append(f"{HARNESS_SKILL_PATH} frontmatter description is missing.")
        elif len(description) > 1024:
            warnings.append(
                f"{HARNESS_SKILL_PATH} frontmatter description exceeds 1024 chars."
            )
        if "`references/repo-harness.md`" not in skill_text:
            warnings.append(
                f"{HARNESS_SKILL_PATH} does not route to references/repo-harness.md."
            )
        if "Zero-Install Rule" not in skill_text:
            warnings.append(f"{HARNESS_SKILL_PATH} is missing the zero-install rule.")

    if reference_text is None:
        warnings.append(f"{HARNESS_SKILL_REFERENCE_PATH} is missing.")
    else:
        resolved_references, reference_warnings = _resolved_references(
            root,
            reference_text,
        )
        warnings.extend(reference_warnings)
        for required in (
            "../../../current-state.md",
            "../../../docs/harness/README.md",
            "../../../docs/harness/feedback/verification-matrix.md",
            "../../../docs/harness/evidence/evidence-log.md",
        ):
            if required not in reference_text:
                warnings.append(
                    f"{HARNESS_SKILL_REFERENCE_PATH} does not reference {required}."
                )

    if not instruction_routes:
        warnings.append(
            "No root instruction file routes harness-maintenance work to "
            f"{HARNESS_SKILL_PATH}."
        )

    status = "wired" if not warnings else "incomplete"
    return SkillWiringReport(
        status=status,
        skill_path=HARNESS_SKILL_PATH,
        reference_path=HARNESS_SKILL_REFERENCE_PATH,
        instruction_routes=instruction_routes,
        resolved_references=tuple(resolved_references),
        frontmatter=frontmatter,
        warnings=tuple(warnings),
        next_actions=_next_actions(status, warnings),
    )


def skill_wiring_to_dict(report: SkillWiringReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": report.status,
        "skillPath": report.skill_path,
        "referencePath": report.reference_path,
        "instructionRoutes": list(report.instruction_routes),
        "resolvedReferences": list(report.resolved_references),
        "frontmatter": dict(report.frontmatter),
        "warnings": list(report.warnings),
        "nextActions": list(report.next_actions),
    }


def _harness_expected(file_set: set[str], root: Path) -> bool:
    if any(marker in file_set or (root / marker).exists() for marker in HARNESS_MARKERS):
        return True
    for file_name in INSTRUCTION_FILES:
        text = _read_text(root, file_name)
        if text and HARNESS_SKILL_PATH in text:
            return True
    return False


def _read_text(root: Path, relative_path: str) -> str | None:
    path = root / path_from_relative_text(relative_path)
    if not is_inside_root(path, root):
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
        return None


def _frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    warnings: list[str] = []
    if not lines or lines[0] != "---":
        return {}, [f"{HARNESS_SKILL_PATH} frontmatter is missing."]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [f"{HARNESS_SKILL_PATH} frontmatter is not closed."]
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            warnings.append(f"{HARNESS_SKILL_PATH} frontmatter line is invalid.")
            continue
        key, value = line.split(":", maxsplit=1)
        result[key.strip()] = value.strip()
    return result, warnings


def _resolved_references(root: Path, text: str) -> tuple[list[str], list[str]]:
    skill_dir = root / Path(HARNESS_SKILL_PATH).parent
    resolved: list[str] = []
    warnings: list[str] = []
    for match in REFERENCE_RE.finditer(text):
        raw = match.group("path")
        path = (skill_dir / raw).resolve(strict=False)
        if not is_inside_root(path, root):
            warnings.append(f"{HARNESS_SKILL_REFERENCE_PATH} reference escapes root.")
            continue
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            warnings.append(f"{HARNESS_SKILL_REFERENCE_PATH} reference escapes root.")
            continue
        resolved.append(relative)
        if not path.exists():
            warnings.append(
                f"{HARNESS_SKILL_REFERENCE_PATH} references missing file {relative}."
            )
    return _dedupe(resolved), warnings


def _instruction_routes(root: Path, file_set: set[str]) -> tuple[str, ...]:
    routes: list[str] = []
    for file_name in INSTRUCTION_FILES:
        if file_name not in file_set and not (root / file_name).exists():
            continue
        text = _read_text(root, file_name)
        if text and HARNESS_SKILL_PATH in text:
            routes.append(file_name)
    return tuple(_dedupe(routes))


def _next_actions(status: str, warnings: list[str]) -> tuple[str, ...]:
    if status == "wired":
        return ()
    if status == "not_applicable":
        return ()
    actions = [
        "Fix repo-local harness skill wiring before relying on generated or enhanced harness guidance."
    ]
    if any("frontmatter" in warning for warning in warnings):
        actions.append("Update skill frontmatter to match the Agent Skills contract.")
    if any("reference" in warning for warning in warnings):
        actions.append("Fix harness skill reference paths so they resolve inside the repository.")
    if any("routes" in warning for warning in warnings):
        actions.append("Route root agent instructions to .agents/skills/harness/SKILL.md.")
    return tuple(_dedupe(actions))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
