from __future__ import annotations

import shutil
from pathlib import PurePosixPath
from typing import Any

SCHEMA_VERSION = "harnessforge.indexAdapters.v1"

TOOL_CANDIDATES = (
    ("ctags", "symbol-index"),
    ("universal-ctags", "symbol-index"),
    ("scip", "code-intelligence-index"),
    ("tree-sitter", "structural-parser"),
)

ARTIFACT_NAMES = {
    "tags": "ctags",
    "compile_commands.json": "compile-commands",
    "cscope.out": "cscope",
}

ARTIFACT_SUFFIXES = (
    (".scip", "scip"),
    (".lsif", "lsif"),
    (".lsif.json", "lsif"),
)


def build_index_adapter_report(files: tuple[str, ...]) -> dict[str, Any]:
    tools = [
        {"name": name, "kind": kind, "available": shutil.which(name) is not None}
        for name, kind in TOOL_CANDIDATES
    ]
    artifacts = _artifact_records(files)
    available_tools = [tool for tool in tools if tool["available"]]
    status = (
        "artifact_available"
        if artifacts
        else "tool_available"
        if available_tools
        else "not_detected"
    )
    next_actions = [
        "Keep the standard-library structural index as the default.",
        "Use adapter data only when it is project-owned, fresh, and improves report or generated-output quality.",
    ]
    if artifacts:
        next_actions.append(
            "Review detected index artifacts for provenance and freshness before using them as harness evidence."
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "defaultBehavior": "standard_library_structural_index",
        "generationEnabled": False,
        "explicitOptInRequired": True,
        "detectedTools": tools,
        "detectedArtifacts": artifacts,
        "adapterCandidates": [
            "ctags",
            "SCIP",
            "LSIF",
            "compile_commands.json",
            "tree-sitter",
            "repo-owned static-analysis reports",
        ],
        "warnings": [],
        "nextActions": next_actions,
    }


def _artifact_records(files: tuple[str, ...]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for file in sorted(files):
        pure = PurePosixPath(file)
        name = pure.name
        if name in ARTIFACT_NAMES:
            records.append(
                {"path": file, "kind": ARTIFACT_NAMES[name], "source": "existing-file"}
            )
            continue
        lower = file.lower()
        for suffix, kind in ARTIFACT_SUFFIXES:
            if lower.endswith(suffix):
                records.append({"path": file, "kind": kind, "source": "existing-file"})
                break
    return records[:50]
