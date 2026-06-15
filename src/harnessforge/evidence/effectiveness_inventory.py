from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVAL_DIRS = {
    "benchmark",
    "benchmarks",
    "eval",
    "evals",
    "evaluation",
    "evaluations",
}

EVAL_SPEC_SUFFIXES = {
    ".json",
    ".jsonl",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
}

SCORER_NAMES = {
    "inner_loop.py",
    "scorer.py",
}

RESULT_NAMES = {
    "frontier.json",
    "run_log.jsonl",
    "results.jsonl",
    "scores.jsonl",
}


@dataclass(frozen=True)
class EffectivenessItem:
    path: str
    category: str
    signals: tuple[str, ...]
    review_required: tuple[str, ...]


@dataclass(frozen=True)
class EffectivenessInventoryReport:
    items: tuple[EffectivenessItem, ...]
    warnings: tuple[str, ...]
    review_required: tuple[str, ...]


def analyze_effectiveness_inventory(
    files: tuple[str, ...],
) -> EffectivenessInventoryReport:
    items = tuple(
        item
        for item in (_effectiveness_item(file) for file in sorted(files))
        if item is not None
    )
    warnings: list[str] = []
    if items:
        warnings.append(
            f"effectiveness eval inventory detected {len(items)} eval, "
            "scorer, or result artifact(s)."
        )
    review_required: list[str] = []
    for item in items:
        review_required.extend(item.review_required)
    return EffectivenessInventoryReport(
        items=items,
        warnings=tuple(warnings),
        review_required=tuple(_dedupe(review_required)),
    )


def effectiveness_item_to_dict(item: EffectivenessItem) -> dict[str, Any]:
    return {
        "path": item.path,
        "category": item.category,
        "signals": list(item.signals),
        "reviewRequired": list(item.review_required),
    }


def _effectiveness_item(file: str) -> EffectivenessItem | None:
    if _is_result_log(file):
        return EffectivenessItem(
            path=file,
            category="result-log",
            signals=("prior-results", "benchmark-evidence"),
            review_required=(
                f"effectiveness result artifact detected at {file}; confirm "
                "baseline, held-out split, and frozen replay limitations before "
                "using it as evidence.",
            ),
        )
    if _is_scorer(file):
        return EffectivenessItem(
            path=file,
            category="scorer",
            signals=("candidate-sensitive-metric", "quality-cost-axis"),
            review_required=(
                f"effectiveness scorer detected at {file}; confirm the metric is "
                "candidate-sensitive and tracks worst-case quality before "
                "claiming harness effectiveness.",
            ),
        )
    if _is_eval_spec(file):
        return EffectivenessItem(
            path=file,
            category="eval-spec",
            signals=("eval-design", "candidate-set"),
            review_required=(
                f"effectiveness eval artifact detected at {file}; confirm "
                "baseline, control arm, held-out split, and anti-leakage rules.",
            ),
        )
    return None


def _is_eval_spec(file: str) -> bool:
    path = Path(file)
    return (
        bool(path.parts)
        and path.parts[0] in EVAL_DIRS
        and path.suffix.lower() in EVAL_SPEC_SUFFIXES
    )


def _is_scorer(file: str) -> bool:
    path = Path(file)
    name = path.name.lower()
    return path.suffix.lower() == ".py" and (
        name in SCORER_NAMES
        or name.startswith("score_")
        or name.endswith("_scorer.py")
    )


def _is_result_log(file: str) -> bool:
    return Path(file).name.lower() in RESULT_NAMES


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
