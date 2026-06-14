from __future__ import annotations

import json
import platform
import re
import sys
from pathlib import Path
from typing import Any


def doctor_report() -> dict[str, Any]:
    python_ok = sys.version_info >= (3, 13)
    os_report = _os_report()
    return {
        "python": {
            "version": platform.python_version(),
            "ok": python_ok,
            "required": "3.13+",
        },
        "platform": os_report,
        "ok": python_ok and os_report["ok"],
    }


def format_doctor(report: dict[str, Any]) -> str:
    lines = [
        "HarnessForge doctor",
        f"Python: {report['python']['version']} ({'ok' if report['python']['ok'] else 'unsupported'})",
        f"Platform: {report['platform']['name']} ({'ok' if report['platform']['ok'] else 'unsupported'})",
    ]
    for warning in report["platform"].get("warnings", []):
        lines.append(f"Warning: {warning}")
    return "\n".join(lines)


def doctor_json(report: dict[str, Any]) -> str:
    return f"{json.dumps(report, indent=2)}\n"


def _os_report() -> dict[str, Any]:
    system = platform.system()
    if system == "Darwin":
        version = platform.mac_ver()[0]
        major = _first_int(version)
        return {
            "name": f"macOS {version or 'unknown'}",
            "ok": major is not None and major >= 15,
            "required": "macOS 15+",
            "warnings": [],
        }
    if system == "Windows":
        release = platform.release()
        version = platform.version()
        build = _windows_build(version)
        ok = release in {"11", "2025"} or (build is not None and build >= 22000)
        return {
            "name": f"Windows {release} build {build or version}",
            "ok": ok,
            "required": "Windows 11+",
            "warnings": [],
        }
    if system == "Linux":
        os_release = _read_os_release()
        name = os_release.get("PRETTY_NAME") or "Linux"
        distro = os_release.get("ID", "").lower()
        version_id = os_release.get("VERSION_ID", "")
        if distro == "ubuntu":
            ok = _version_at_least(version_id, "22.04")
            warnings: list[str] = []
        else:
            ok = True
            warnings = [
                "Linux distribution is not Ubuntu. Support is best effort when Python 3.13+ is available."
            ]
        return {
            "name": name,
            "ok": ok,
            "required": "Ubuntu 22.04+ floor; other modern Linux distributions best effort",
            "warnings": warnings,
        }
    return {
        "name": system or "unknown",
        "ok": False,
        "required": "macOS 15+, Windows 11+, or Ubuntu 22.04+ Linux",
        "warnings": [],
    }


def _read_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return {}
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        data[key] = value.strip().strip('"')
    return data


def _first_int(value: str) -> int | None:
    match = re.match(r"(\d+)", value)
    return int(match.group(1)) if match else None


def _windows_build(version: str) -> int | None:
    parts = version.split(".")
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
    return None


def _version_at_least(actual: str, required: str) -> bool:
    def parts(value: str) -> tuple[int, ...]:
        return tuple(int(part) for part in re.findall(r"\d+", value))

    actual_parts = parts(actual)
    required_parts = parts(required)
    return actual_parts >= required_parts
