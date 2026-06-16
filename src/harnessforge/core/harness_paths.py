from __future__ import annotations

from pathlib import Path


HARNESS_SKILL_PATH = ".agents/skills/harness/SKILL.md"
HARNESS_SKILL_REFERENCE_PATH = ".agents/skills/harness/references/repo-harness.md"

CANONICAL_HARNESS_PATHS = {
    "readme": "docs/harness/README.md",
    "manifest": "docs/harness/manifest.json",
    "authoritative_facts": "docs/harness/authoritative-facts.md",
    "feature_list_schema": "docs/harness/schemas/feature-list.schema.json",
    "first_agent_task": "docs/harness/state/first-agent-task.md",
    "first_agent_review": "docs/harness/evidence/first-agent-review.json",
    "roadmap": "docs/harness/state/roadmap.md",
    "clean_state_checklist": "docs/harness/state/clean-state-checklist.md",
    "evidence_log": "docs/harness/evidence/evidence-log.md",
    "entropy_control": "docs/harness/state/entropy-control.md",
    "change_contract": "docs/harness/boundaries/change-contract.md",
    "component_inventory": "docs/harness/boundaries/component-inventory.md",
    "dependency_change_policy": "docs/harness/boundaries/dependency-change-policy.md",
    "security_boundary_map": "docs/harness/boundaries/security-boundary-map.md",
    "feature_privacy_labels": "docs/harness/boundaries/feature-privacy-labels.json",
    "verification_matrix": "docs/harness/feedback/verification-matrix.md",
    "sensor_registry": "docs/harness/feedback/sensor-registry.md",
    "evaluator_rubric": "docs/harness/feedback/evaluator-rubric.md",
    "quality_document": "docs/harness/feedback/quality-document.md",
    "release_controls": "docs/harness/release/release-controls.md",
    "source_record_schema": "docs/harness/research/source-record.schema.json",
    "source_record_example": "docs/harness/research/source-record-example.json",
    "research_sources": "docs/harness/research/research-sources.json",
    "research_inbox": "docs/harness/research/research-inbox.md",
    "sources": "docs/harness/research/sources.md",
    "agent_operating_model": "docs/harness/operations/agent-operating-model.md",
    "multi_agent_orchestration": "docs/harness/operations/multi-agent-orchestration.md",
}


def harness_path(key: str) -> str:
    return CANONICAL_HARNESS_PATHS[key]


def existing_harness_path(_root: Path, key: str) -> str:
    return CANONICAL_HARNESS_PATHS[key]


def first_existing_text(files: dict[str, str], key: str) -> str:
    return files.get(CANONICAL_HARNESS_PATHS[key], "")


def first_existing_key(files: dict[str, str], key: str) -> str | None:
    relative_path = CANONICAL_HARNESS_PATHS[key]
    if relative_path in files:
        return relative_path
    return None


def any_existing_key(files: dict[str, str], key: str) -> bool:
    return first_existing_key(files, key) is not None
