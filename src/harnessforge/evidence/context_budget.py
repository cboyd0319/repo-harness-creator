from __future__ import annotations

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

OVERSIZED_LINE_LIMIT = 300
OVERSIZED_CHAR_LIMIT = 24_000
MIN_DUPLICATE_BLOCK_LINES = 4


@dataclass(frozen=True)
class InstructionContextItem:
    path: str
    line_count: int
    char_count: int
    findings: tuple[str, ...]


@dataclass(frozen=True)
class DuplicateInstructionBlock:
    left: str
    right: str
    line_count: int
    preview: str


@dataclass(frozen=True)
class ContextBudgetReport:
    instruction_files: tuple[InstructionContextItem, ...]
    duplicate_instruction_blocks: tuple[DuplicateInstructionBlock, ...]
    warnings: tuple[str, ...]


def analyze_context_budget(root: Path, files: tuple[str, ...]) -> ContextBudgetReport:
    root = root.resolve()
    file_set = set(files)
    texts: dict[str, str] = {}
    instruction_files: list[InstructionContextItem] = []

    for file in INSTRUCTION_FILES:
        if file not in file_set:
            continue
        text = _read_text(root, file)
        if text is None:
            continue
        texts[file] = text
        instruction_files.append(_instruction_context_item(file, text))

    duplicates = _duplicate_instruction_blocks(texts)
    warnings = _warnings(instruction_files, duplicates)
    return ContextBudgetReport(
        instruction_files=tuple(instruction_files),
        duplicate_instruction_blocks=tuple(duplicates),
        warnings=tuple(warnings),
    )


def context_budget_to_dict(report: ContextBudgetReport) -> dict[str, Any]:
    return {
        "instructionFiles": [
            {
                "path": item.path,
                "lineCount": item.line_count,
                "charCount": item.char_count,
                "findings": list(item.findings),
            }
            for item in report.instruction_files
        ],
        "duplicateInstructionBlocks": [
            {
                "left": item.left,
                "right": item.right,
                "lineCount": item.line_count,
                "preview": item.preview,
            }
            for item in report.duplicate_instruction_blocks
        ],
    }


def _instruction_context_item(path: str, text: str) -> InstructionContextItem:
    line_count = len(text.splitlines())
    char_count = len(text)
    findings: list[str] = []
    if line_count > OVERSIZED_LINE_LIMIT or char_count > OVERSIZED_CHAR_LIMIT:
        findings.append("oversized")
    return InstructionContextItem(
        path=path,
        line_count=line_count,
        char_count=char_count,
        findings=tuple(findings),
    )


def _duplicate_instruction_blocks(
    texts: dict[str, str]
) -> list[DuplicateInstructionBlock]:
    duplicates: list[DuplicateInstructionBlock] = []
    paths = sorted(texts)
    for left_index, left in enumerate(paths):
        left_blocks = _normalized_blocks(texts[left])
        if not left_blocks:
            continue
        for right in paths[left_index + 1 :]:
            right_blocks = _normalized_blocks(texts[right])
            overlap = sorted(
                set(left_blocks) & set(right_blocks),
                key=lambda block: (-len(block), block),
            )
            if not overlap:
                continue
            block = overlap[0]
            duplicates.append(
                DuplicateInstructionBlock(
                    left=left,
                    right=right,
                    line_count=len(block),
                    preview=block[0][:120],
                )
            )
    return duplicates


def _normalized_blocks(text: str) -> list[tuple[str, ...]]:
    lines = [_normalize_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    if len(lines) < MIN_DUPLICATE_BLOCK_LINES:
        return []
    blocks: list[tuple[str, ...]] = []
    for index in range(0, len(lines) - MIN_DUPLICATE_BLOCK_LINES + 1):
        block = tuple(lines[index : index + MIN_DUPLICATE_BLOCK_LINES])
        blocks.append(block)
    return blocks


def _normalize_line(line: str) -> str:
    stripped = " ".join(line.strip().split())
    if not stripped or stripped.startswith("#"):
        return ""
    return stripped.lower()


def _warnings(
    instruction_files: list[InstructionContextItem],
    duplicates: list[DuplicateInstructionBlock],
) -> list[str]:
    warnings: list[str] = []
    oversized = [item.path for item in instruction_files if "oversized" in item.findings]
    if oversized:
        warnings.append(
            "context budget warning: oversized instruction files detected "
            f"({', '.join(oversized[:4])})."
        )
    if duplicates:
        warnings.append(
            "duplicate instruction warning: repeated router text detected across "
            "instruction files."
        )
    return warnings


def _read_text(root: Path, file: str) -> str | None:
    try:
        path = root / path_from_relative_text(file)
    except ValueError:
        return None
    if not is_inside_root(path, root) or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
