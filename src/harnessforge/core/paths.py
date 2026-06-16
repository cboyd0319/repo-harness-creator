from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath

SEPARATOR_RE = re.compile(r"[\\/]+")


def is_absolute_path_text(path_text: str) -> bool:
    text = path_text.strip()
    if not text:
        return False
    windows_path = PureWindowsPath(text)
    return (
        Path(text).is_absolute()
        or PurePosixPath(text).is_absolute()
        or bool(windows_path.drive or windows_path.root)
    )


def path_from_relative_text(path_text: str) -> Path:
    parts = [
        part
        for part in SEPARATOR_RE.split(path_text)
        if part and part != "."
    ]
    if not parts:
        return Path(".")
    return Path(*parts)


def is_inside_root(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True
