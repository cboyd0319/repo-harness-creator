from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import is_absolute_path_text, is_inside_root, path_from_relative_text
from .redact import redact_local_paths


def report_path(path_text: str, target: Path) -> Path | None:
    path_text = path_text.strip()
    if not path_text:
        return None
    if is_absolute_path_text(path_text):
        raise ValueError("report paths must be relative to the target repository")
    requested = path_from_relative_text(path_text)
    path = target / requested
    if not is_inside_root(path, target):
        raise ValueError("report paths must stay inside the target repository")
    return path


def write_json_payload(path_text: str, target: Path, payload: Any) -> str:
    path = report_path(path_text, target)
    if path is None:
        return ""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return relative_to_target(path, target)


def relative_to_target(path: Path, target: Path) -> str:
    try:
        return path.resolve().relative_to(target.resolve()).as_posix()
    except ValueError:
        return redact_local_paths(str(path))
