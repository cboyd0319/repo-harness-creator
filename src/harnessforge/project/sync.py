from __future__ import annotations

from typing import Any

from .readiness import ReadinessReport, format_readiness, readiness_to_dict

SYNC_EXIT_CODES = {
    "ready": 0,
    "warning": 1,
    "blocked": 2,
}


def sync_exit_code(report: ReadinessReport) -> int:
    return SYNC_EXIT_CODES.get(report.verdict, 2)


def sync_check_to_dict(report: ReadinessReport, exit_code: int) -> dict[str, Any]:
    readiness = readiness_to_dict(report)
    return {
        "mode": "check",
        "target": readiness["target"],
        "verdict": readiness["verdict"],
        "exitCode": exit_code,
        "readiness": readiness,
    }


def format_sync_check(report: ReadinessReport) -> str:
    return f"Sync check: {report.verdict}\n\n{format_readiness(report)}"
