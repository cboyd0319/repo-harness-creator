from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA_VERSION = "harnessforge.observability.v1"

RUNTIME_SIGNALS = (
    ("init.sh", "startup-entrypoint"),
    ("init.ps1", "startup-entrypoint"),
    (".github/workflows/ci.yml", "ci-verification"),
    ("scripts/check_pins.py", "pin-check"),
    ("scripts/refresh_research.py", "source-refresh-check"),
    ("tests", "test-suite"),
)

PROCESS_SIGNALS = (
    ("current-state.md", "current-state"),
    ("feature_list.json", "feature-state"),
    ("docs/harness/boundaries/change-contract.md", "change-contract"),
    ("docs/harness/feedback/verification-matrix.md", "verification-matrix"),
    ("docs/harness/feedback/sensor-registry.md", "sensor-registry"),
    ("docs/harness/evidence/evidence-log.md", "evidence-log"),
    ("docs/harness/feedback/evaluator-rubric.md", "evaluator-rubric"),
    ("docs/harness/release/release-controls.md", "release-controls"),
)


def build_observability_report(root: Path, files: tuple[str, ...]) -> dict[str, Any]:
    file_set = set(files)
    runtime = _detected(root, file_set, RUNTIME_SIGNALS)
    process = _detected(root, file_set, PROCESS_SIGNALS)
    warnings: list[str] = []
    next_actions: list[str] = []
    if len(runtime) < 2:
        warnings.append(
            "Runtime observability is thin; add or document startup, test, log, health, or smoke signals."
        )
    if len(process) < 4:
        warnings.append(
            "Process observability is thin; add or document state, verification, evidence, and acceptance signals."
        )
    if warnings:
        next_actions.append(
            "Improve observability before making reliability or release-readiness claims."
        )
    status = "strong" if not warnings else "needs_review"
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "summary": {
            "runtimeSignalCount": len(runtime),
            "processSignalCount": len(process),
        },
        "runtimeSignals": runtime,
        "processSignals": process,
        "warnings": warnings,
        "nextActions": next_actions,
    }


def _detected(
    root: Path,
    file_set: set[str],
    signals: tuple[tuple[str, str], ...],
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for path, kind in signals:
        present = path in file_set or (root / path).is_dir()
        if present:
            result.append({"path": path, "kind": kind, "source": "detected"})
    return result
