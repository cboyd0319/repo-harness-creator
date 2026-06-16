from __future__ import annotations

import shlex
from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import Any

from ..core.models import ProjectProfile
from ..core.paths import is_inside_root, path_from_relative_text

SCHEMA_VERSION = "harnessforge.nestedInstructionPlan.v1"
DEFAULT_CANDIDATE_LIMIT = 20
WORKFLOW_PROBE_BYTES = 65536
SIGNAL_LIMIT = 6
DOC_NAMES = {
    "readme.md",
    "readme.rst",
    "readme.txt",
}
DOC_PARTS = {
    "doc",
    "docs",
    "documentation",
}
LOW_PRIORITY_PARTS = {
    "docs",
    "examples",
    "samples",
    "site",
}
NOISY_PARTS = {
    "3rdparty",
    "external",
    "fixture",
    "fixtures",
    "generated",
    "samples",
    "testdata",
    "third-party",
    "third_party",
    "vendor",
    "vendors",
}
ROUTING_MONOREPO_SIGNALS = {
    ".github/workflows path filters",
    ".github/workflows working-directory",
}


def build_nested_instruction_plan(
    profile: ProjectProfile,
    *,
    candidate_limit: int = DEFAULT_CANDIDATE_LIMIT,
) -> dict[str, Any]:
    existing = sorted(
        file
        for file in profile.files
        if PurePosixPath(file).name == "AGENTS.md" and file != "AGENTS.md"
    )
    components = [
        component
        for component in (_component_record(value) for value in profile.components)
        if component["path"] not in {"", "."}
    ]
    omitted_components = [
        component
        for component in (
            _component_record(value) for value in profile.component_overflow
        )
        if component["path"] not in {"", "."}
    ]
    signals = _nested_instruction_signals(profile, components, existing)
    candidates = []
    omitted_candidates = []
    if signals:
        candidates = _candidate_records(
            _ranked_components(profile, components, existing),
            recommended_action="review_required",
        )
        omitted_candidates = _candidate_records(
            _ranked_components(profile, omitted_components, existing),
            recommended_action="raise_component_limit_or_review_manually",
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": (
            "review_required" if candidates or omitted_candidates else "no_action"
        ),
        "writeByDefault": False,
        "rootAgentsPresent": "AGENTS.md" in profile.files,
        "monorepoSignals": signals,
        "existingNestedAgents": existing[:candidate_limit],
        "existingNestedAgentCount": len(existing),
        "candidateComponents": candidates[:candidate_limit],
        "candidateCount": len(candidates),
        "omittedCandidateComponents": omitted_candidates[:candidate_limit],
        "omittedCandidateCount": len(omitted_candidates),
        "candidateLimit": candidate_limit,
        "candidateListTruncated": len(candidates) > candidate_limit,
        "omittedCandidateListTruncated": len(omitted_candidates) > candidate_limit,
        "guidance": (
            "Use root AGENTS.md as a short repo-wide router. Add nested "
            "AGENTS.md only for meaningful components whose stack, commands, "
            "ownership, constraints, or verification differ."
        ),
        "omittedGuidance": (
            "Omitted candidates came from the component inventory overflow. "
            "Raise --component-limit or review the omitted paths manually before "
            "adding nested instruction files."
            if omitted_candidates
            else ""
        ),
    }


def _component_record(component: str) -> dict[str, Any]:
    path, markers = _parse_component(component)
    return {"path": path, "markers": markers}


def _parse_component(component: str) -> tuple[str, list[str]]:
    if component.endswith(")") and " (" in component:
        path, marker_text = component[:-1].split(" (", 1)
        markers = [marker.strip() for marker in marker_text.split(",")]
        return path, [marker for marker in markers if marker]
    return component, []


def _nested_instruction_signals(
    profile: ProjectProfile,
    components: list[dict[str, Any]],
    existing: list[str],
) -> list[str]:
    signals = list(profile.workspace_markers)
    signals.extend(
        marker
        for marker in profile.routing_markers
        if marker in ROUTING_MONOREPO_SIGNALS
    )
    if len(components) >= 4:
        signals.append("4+ detected component boundaries")
    if profile.component_scan_truncated:
        signals.append("component inventory truncated")
    if existing:
        signals.append("existing nested AGENTS.md")
    return list(dict.fromkeys(signals))


def _has_nested_agent(existing: list[str], component: str) -> bool:
    prefix = component.rstrip("/") + "/"
    return any(path.startswith(prefix) for path in existing)


def _ranked_components(
    profile: ProjectProfile,
    components: list[dict[str, Any]],
    existing: list[str],
) -> list[dict[str, Any]]:
    return sorted(
        (
            _ranked_component(profile, component)
            for component in components
            if not _has_nested_agent(existing, component["path"])
        ),
        key=_rank_sort_key,
    )


def _candidate_records(
    ranked_components: list[dict[str, Any]],
    *,
    recommended_action: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rank, ranked in enumerate(ranked_components, start=1):
        component = ranked["component"]
        path = component["path"]
        records.append(
            {
                "path": path,
                "instructionPath": f"{path}/AGENTS.md",
                "rank": rank,
                "reason": _candidate_reason(component, ranked["rankSignals"]),
                "rankSignals": ranked["rankSignals"],
                "reviewFocus": ranked["reviewFocus"],
                "recommendedAction": recommended_action,
            }
        )
    return records


def _ranked_component(
    profile: ProjectProfile,
    component: dict[str, Any],
) -> dict[str, Any]:
    path = component["path"]
    score = _base_component_score(path, component["markers"])
    signal_entries: list[tuple[int, str, str]] = []

    verification = _verification_signals(profile, path)
    for detail in verification:
        signal_entries.append((60, f"verification source: {detail}", "verification"))

    workflows = _workflow_signals(profile, path)
    for detail in workflows:
        signal_entries.append((35, f"workflow routing: {detail}", "workflow-routing"))

    local_docs = _local_doc_signals(profile, path)
    for detail in local_docs:
        signal_entries.append((20, f"local docs: {detail}", "local-docs"))

    if component["markers"]:
        markers = ", ".join(component["markers"][:3])
        signal_entries.append((12, f"boundary markers: {markers}", "boundary-markers"))

    parts = {part.lower() for part in PurePosixPath(path).parts}
    if parts & NOISY_PARTS:
        signal_entries.append(
            (-40, "lower priority: generated/vendor/example path", "noise")
        )
    elif parts & LOW_PRIORITY_PARTS:
        signal_entries.append((-15, "lower priority: docs/example path", "noise"))

    score += sum(weight for weight, _, _ in signal_entries)
    ordered = sorted(signal_entries, key=lambda item: (-item[0], item[1]))
    rank_signals = _dedupe([label for _, label, _ in ordered])[:SIGNAL_LIMIT]
    review_focus = _dedupe(
        focus for weight, _, focus in ordered if weight > 0 and focus != "noise"
    )
    if not review_focus:
        review_focus = ["boundary-markers"]
    return {
        "component": component,
        "path": path,
        "score": score,
        "rankSignals": rank_signals,
        "reviewFocus": review_focus,
    }


def _rank_sort_key(ranked: dict[str, Any]) -> tuple[int, int, str]:
    path = ranked["path"]
    return (-int(ranked["score"]), _path_depth(path), path)


def _base_component_score(path: str, markers: list[str]) -> int:
    first_segment = path.split("/", 1)[0]
    if first_segment in {"apps", "packages", "services", "crates"}:
        score = 40
    elif first_segment in {"src", "cmd", "pkg", "lib"}:
        score = 35
    elif first_segment in {"tools", "scripts", "hack"}:
        score = 25
    elif first_segment in {"test", "tests", "spec"}:
        score = 10
    elif first_segment in {"docs", "examples", "samples", "site"}:
        score = -5
    elif first_segment in {"external", "third_party", "vendor", "vendors"}:
        score = -20
    else:
        score = 15
    if markers:
        score += 5
    if "BUILD" in markers or "BUILD.bazel" in markers:
        score += 5
    return score


def _verification_signals(profile: ProjectProfile, component: str) -> list[str]:
    signals: list[str] = []
    for record in profile.verification_command_records:
        source_path = _normalize_path_text(record.source_path)
        if source_path and _path_within(source_path, component):
            signals.append(source_path)
            continue
        command_path = _component_path_in_command(record.command, component)
        if command_path:
            signals.append(command_path)
    return _dedupe(signals)[:3]


def _component_path_in_command(command: str, component: str) -> str:
    component = component.strip("/")
    if not component:
        return ""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    for token in tokens:
        for normalized in _command_path_candidates(token):
            if _path_within(normalized, component):
                return component
    return ""


def _command_path_candidates(token: str) -> list[str]:
    candidates = [_normalize_path_text(token)]
    if "=" in token:
        candidates.append(_normalize_path_text(token.split("=", 1)[1]))
    return [
        candidate
        for candidate in _dedupe(candidates)
        if "/" in candidate or "\\" in token
    ]


def _workflow_signals(profile: ProjectProfile, component: str) -> list[str]:
    signals: list[str] = []
    for relative in profile.files:
        if not relative.startswith(".github/workflows/"):
            continue
        if PurePosixPath(relative).suffix.lower() not in {".yml", ".yaml"}:
            continue
        text = _read_text_probe(profile, relative)
        if not text:
            continue
        if _component_mentioned(text, component):
            signals.append(relative)
    return _dedupe(signals)[:3]


def _local_doc_signals(profile: ProjectProfile, component: str) -> list[str]:
    signals: list[str] = []
    for relative in profile.files:
        if not _path_within(relative, component):
            continue
        if _is_local_doc(relative):
            signals.append(relative)
    return _dedupe(sorted(signals, key=lambda value: (_path_depth(value), value)))[:3]


def _is_local_doc(relative: str) -> bool:
    if relative.startswith("docs/harness/"):
        return False
    path = PurePosixPath(relative)
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    if name in DOC_NAMES:
        return True
    return bool(DOC_PARTS & parts) and path.suffix.lower() in {".md", ".rst", ".txt"}


def _read_text_probe(profile: ProjectProfile, relative: str) -> str:
    path = profile.root / path_from_relative_text(relative)
    if not is_inside_root(path, profile.root):
        return ""
    try:
        return path.read_bytes()[:WORKFLOW_PROBE_BYTES].decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _component_mentioned(text: str, component: str) -> bool:
    component = component.strip("/")
    if not component:
        return False
    quoted = {component, f"./{component}", f"{component}/", f"{component}/**"}
    return any(value in text for value in quoted)


def _path_within(path: str, component: str) -> bool:
    path = _normalize_path_text(path)
    component = _normalize_path_text(component)
    if not path or not component:
        return False
    return path == component or path.startswith(component.rstrip("/") + "/")


def _normalize_path_text(value: str) -> str:
    normalized = value.strip().strip("\"'").replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def _path_depth(path: str) -> int:
    return len(PurePosixPath(path).parts)


def _dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _candidate_reason(component: dict[str, Any], rank_signals: list[str]) -> str:
    if rank_signals:
        return "component ranked for nested instructions by " + "; ".join(
            rank_signals[:3]
        )
    markers = component["markers"]
    if markers:
        return "component has boundary markers: " + ", ".join(markers[:4])
    return "component has its own detected boundary signal"
