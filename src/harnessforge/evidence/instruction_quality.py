from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..paths import is_inside_root, path_from_relative_text

INSTRUCTION_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
)

SECTION_MARKERS = {
    "projectOverview": (
        "project overview",
        "purpose",
        "this project",
        "this repo",
        "repository",
    ),
    "startup": (
        "startup",
        "first-run",
        "first run",
        "setup",
        "bootstrap",
        "install",
    ),
    "verification": (
        "verification",
        "verify",
        "test",
        "tests",
        "lint",
        "check",
        "pytest",
        "unittest",
        "npm test",
        "cargo test",
        "go test",
    ),
    "constraints": (
        "must",
        "never",
        "do not",
        "security",
        "boundary",
        "constraints",
        "non-negotiable",
    ),
    "state": (
        "current-state.md",
        "handoff",
        "state",
        "roadmap",
        "feature_list",
        "feature-list",
    ),
    "routing": (
        "docs/",
        ".md",
        "read ",
        "route",
        "source of truth",
        "source-of-truth",
        "see ",
    ),
}

ACTION_RE = re.compile(
    r"\b("
    r"ask|avoid|check|confirm|do not|follow|keep|never|prefer|preserve|"
    r"read|record|reject|respect|review|run|treat|update|use|verify"
    r")\b",
    re.IGNORECASE,
)
PATH_RE = re.compile(
    r"(`[^`]+`)|(\b[\w.-]+/[\w./-]+\b)|(\b[\w.-]+\.(?:md|json|toml|ya?ml|py|js|ts|rs|go|sh|ps1)\b)"
)
COMMAND_RE = re.compile(
    r"\b("
    r"python(?:3)?|pytest|unittest|npm|pnpm|yarn|cargo|go test|make|just|"
    r"mvn|gradle|composer|bundle|ruff|mypy|eslint|tsc|harnessforge"
    r")\b",
    re.IGNORECASE,
)
NOISE_RE = re.compile(
    r"\b(TODO|TBD|lorem ipsum|placeholder|coming soon|fix later)\b|"
    r"NEEDS CLARIFICATION|REVIEW REQUIRED|\?\?\?",
    re.IGNORECASE,
)

COUNT_METHOD = "utf8_bytes_whitespace_words_splitlines"
BUDGET_MODE = "warning"
PRIMARY_BUDGET = {
    "target_words": 800,
    "max_words": 1000,
    "target_lines": 140,
    "max_lines": 220,
    "target_bytes": 16_000,
    "max_bytes": 20_000,
}
ROUTER_BUDGET = {
    "target_words": 300,
    "max_words": 500,
    "target_lines": 80,
    "max_lines": 120,
    "target_bytes": 8_000,
    "max_bytes": 12_000,
}
LONG_LINE_LIMIT = 220


@dataclass(frozen=True)
class InstructionQualityItem:
    path: str
    surface_type: str
    status: str
    score: int
    budget_status: str
    line_count: int
    word_count: int
    byte_count: int
    char_count: int
    content_line_count: int
    signal_line_count: int
    noise_line_count: int
    signal_ratio: float
    target_words: int
    max_words: int
    target_lines: int
    max_lines: int
    target_bytes: int
    max_bytes: int
    missing_sections: tuple[str, ...]
    findings: tuple[str, ...]


@dataclass(frozen=True)
class InstructionQualityReport:
    status: str
    average_score: int | None
    files: tuple[InstructionQualityItem, ...]
    largest_files: tuple[InstructionQualityItem, ...]
    missing_sections: tuple[str, ...]
    warnings: tuple[str, ...]


def analyze_instruction_quality(
    root: Path,
    files: tuple[str, ...],
) -> InstructionQualityReport:
    root = root.resolve()
    file_set = set(files)
    items: list[InstructionQualityItem] = []
    instruction_paths = tuple(path for path in INSTRUCTION_FILES if path in file_set)
    primary_path = instruction_paths[0] if instruction_paths else ""
    for path_text in instruction_paths:
        if path_text not in file_set:
            continue
        text = _read_text(root, path_text)
        if text is None:
            continue
        items.append(_analyze_file(path_text, text, primary_path=primary_path))
    if not items:
        return InstructionQualityReport(
            status="absent",
            average_score=None,
            files=(),
            largest_files=(),
            missing_sections=(),
            warnings=(),
        )
    missing_sections = tuple(
        sorted(set.intersection(*(set(item.missing_sections) for item in items)))
    )
    average_score = round(sum(item.score for item in items) / len(items))
    statuses = {item.status for item in items}
    budget_statuses = {item.budget_status for item in items}
    if "weak" in statuses:
        status = "weak"
    elif "over_hard" in budget_statuses:
        status = "needs_review"
    elif "needs_review" in statuses:
        status = "needs_review"
    else:
        status = "strong"
    largest_files = tuple(
        sorted(items, key=lambda item: (item.byte_count, item.word_count), reverse=True)[
            :5
        ]
    )
    quality_warnings = [
        f"instruction quality warning: {item.path} is {item.status} "
        f"(score {item.score}/100)."
        for item in items
        if item.status != "strong"
    ]
    budget_warnings = [
        f"instruction budget warning: {item.path} is over hard budget "
        f"({item.word_count} words, {item.line_count} lines, {item.byte_count} bytes)."
        for item in items
        if item.budget_status == "over_hard"
    ]
    return InstructionQualityReport(
        status=status,
        average_score=average_score,
        files=tuple(items),
        largest_files=largest_files,
        missing_sections=missing_sections,
        warnings=tuple(quality_warnings + budget_warnings),
    )


def instruction_quality_to_dict(
    report: InstructionQualityReport,
) -> dict[str, Any]:
    return {
        "summary": {
            "status": report.status,
            "averageScore": report.average_score,
            "fileCount": len(report.files),
            "missingSections": list(report.missing_sections),
            "budgetMode": BUDGET_MODE,
            "countMethod": COUNT_METHOD,
        },
        "files": [
            {
                "path": item.path,
                "surfaceType": item.surface_type,
                "status": item.status,
                "score": item.score,
                "budgetStatus": item.budget_status,
                "lineCount": item.line_count,
                "wordCount": item.word_count,
                "byteCount": item.byte_count,
                "charCount": item.char_count,
                "contentLineCount": item.content_line_count,
                "signalLineCount": item.signal_line_count,
                "noiseLineCount": item.noise_line_count,
                "signalRatio": item.signal_ratio,
                "targetWords": item.target_words,
                "maxWords": item.max_words,
                "targetLines": item.target_lines,
                "maxLines": item.max_lines,
                "targetBytes": item.target_bytes,
                "maxBytes": item.max_bytes,
                "missingSections": list(item.missing_sections),
                "findings": list(item.findings),
            }
            for item in report.files
        ],
        "largestFiles": [
            {
                "path": item.path,
                "surfaceType": item.surface_type,
                "wordCount": item.word_count,
                "lineCount": item.line_count,
                "byteCount": item.byte_count,
                "budgetStatus": item.budget_status,
            }
            for item in report.largest_files
        ],
        "warnings": list(report.warnings),
    }


def _analyze_file(
    path: str,
    text: str,
    *,
    primary_path: str,
) -> InstructionQualityItem:
    surface_type = _surface_type(path, text, primary_path)
    budget = PRIMARY_BUDGET if surface_type == "primary_instruction" else ROUTER_BUDGET
    lines = text.splitlines()
    word_count = len(text.split())
    byte_count = len(text.encode("utf-8"))
    content_lines = [line for line in lines if _is_content_line(line)]
    signal_lines = [line for line in content_lines if _is_signal_line(line)]
    noise_lines = [line for line in content_lines if _is_noise_line(line)]
    coverage = _section_coverage(text, surface_type=surface_type)
    missing_sections = tuple(
        section for section, covered in coverage.items() if not covered
    )
    budget_status = _budget_status(
        word_count=word_count,
        line_count=len(lines),
        byte_count=byte_count,
        budget=budget,
    )
    signal_ratio = (
        round(len(signal_lines) / len(content_lines), 2) if content_lines else 0.0
    )
    findings = _findings(
        line_count=len(lines),
        char_count=len(text),
        signal_ratio=signal_ratio,
        noise_count=len(noise_lines),
        missing_sections=missing_sections,
        budget_status=budget_status,
    )
    score = _score(
        content_line_count=len(content_lines),
        line_count=len(lines),
        char_count=len(text),
        signal_ratio=signal_ratio,
        noise_count=len(noise_lines),
        missing_sections=missing_sections,
        budget_status=budget_status,
    )
    return InstructionQualityItem(
        path=path,
        surface_type=surface_type,
        status=_status(score),
        score=score,
        budget_status=budget_status,
        line_count=len(lines),
        word_count=word_count,
        byte_count=byte_count,
        char_count=len(text),
        content_line_count=len(content_lines),
        signal_line_count=len(signal_lines),
        noise_line_count=len(noise_lines),
        signal_ratio=signal_ratio,
        target_words=int(budget["target_words"]),
        max_words=int(budget["max_words"]),
        target_lines=int(budget["target_lines"]),
        max_lines=int(budget["max_lines"]),
        target_bytes=int(budget["target_bytes"]),
        max_bytes=int(budget["max_bytes"]),
        missing_sections=missing_sections,
        findings=findings,
    )


def _score(
    *,
    content_line_count: int,
    line_count: int,
    char_count: int,
    signal_ratio: float,
    noise_count: int,
    missing_sections: tuple[str, ...],
    budget_status: str,
) -> int:
    if content_line_count == 0:
        return 0
    score = 100 - (len(missing_sections) * 10)
    if signal_ratio < 0.35:
        score -= 20
    elif signal_ratio < 0.5:
        score -= 10
    if noise_count:
        score -= min(15, 5 + noise_count)
    if budget_status == "over_hard":
        score -= 15
    elif budget_status == "over_target":
        score -= 5
    if line_count > 300 or char_count > 24_000:
        score -= 15
    elif line_count > 180 or char_count > 16_000:
        score -= 5
    return max(0, min(100, score))


def _status(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 60:
        return "needs_review"
    return "weak"


def _findings(
    *,
    line_count: int,
    char_count: int,
    signal_ratio: float,
    noise_count: int,
    missing_sections: tuple[str, ...],
    budget_status: str,
) -> tuple[str, ...]:
    findings: list[str] = []
    if missing_sections:
        findings.append("missing_sections")
    if signal_ratio < 0.5:
        findings.append("low_signal_ratio")
    if noise_count:
        findings.append("placeholder_or_review_noise")
    if budget_status != "under_target":
        findings.append(budget_status)
    if line_count > 180 or char_count > 16_000:
        findings.append("large_startup_surface")
    return tuple(findings)


def _section_coverage(text: str, *, surface_type: str) -> dict[str, bool]:
    lower = text.lower()
    if surface_type == "platform_router":
        return {
            "routing": any(marker in lower for marker in SECTION_MARKERS["routing"]),
        }
    return {
        section: any(marker in lower for marker in markers)
        for section, markers in SECTION_MARKERS.items()
    }


def _surface_type(path: str, text: str, primary_path: str) -> str:
    if path == primary_path:
        return "primary_instruction"
    lower = text.lower()
    if "agents.md" in lower or "shared repo guidance" in lower:
        return "platform_router"
    return "secondary_instruction"


def _budget_status(
    *,
    word_count: int,
    line_count: int,
    byte_count: int,
    budget: dict[str, int],
) -> str:
    if (
        word_count > budget["max_words"]
        or line_count > budget["max_lines"]
        or byte_count > budget["max_bytes"]
    ):
        return "over_hard"
    if (
        word_count > budget["target_words"]
        or line_count > budget["target_lines"]
        or byte_count > budget["target_bytes"]
    ):
        return "over_target"
    return "under_target"


def _is_content_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return False
    if set(stripped) <= {"|", "-", ":", " "}:
        return False
    return True


def _is_signal_line(line: str) -> bool:
    return bool(
        ACTION_RE.search(line)
        or PATH_RE.search(line)
        or COMMAND_RE.search(line)
        or line.lstrip().startswith(("-", "*", "1."))
    )


def _is_noise_line(line: str) -> bool:
    return bool(NOISE_RE.search(line) or len(line.strip()) > LONG_LINE_LIMIT)


def _read_text(root: Path, path_text: str) -> str | None:
    try:
        path = root / path_from_relative_text(path_text)
    except ValueError:
        return None
    if not is_inside_root(path, root) or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
