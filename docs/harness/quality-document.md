# Quality Document

Last Updated: 2026-06-14

Use this as a periodic codebase health snapshot. It is separate from the
evaluator rubric: the rubric scores one work session, while this document scores
the repo over time.

## Domain Grades

| Domain | Grade | Verification Status | Agent Legibility | Key Gaps |
| --- | --- | --- | --- | --- |
| CLI package | A | 92 local tests pass | Clear module boundaries | No current cleanup gap |
| GitHub Action | A | Local adapter tests, pin checks, and prior hosted Action smoke pass | Action docs present | Manual platform workflow remains a release checkpoint |
| Harness templates | A | Self-audit is 100/100 and generated update dry run is clean | Templates include state, security, privacy, component, and lifecycle docs | Real agent effectiveness still needs representative task runs |
| Supply chain | A | Pin checker passes | Exact package pins and SHA-pinned Actions are documented and enforced | Release-time SBOM/provenance remains a decision |
| Self-healing | B | Research refresh script and workflow exist | Reviewed PR loop, no silent merge | Review recurring PR output before merging |

Grades: A is strong, B is usable with known gaps, C needs targeted cleanup, D is
unsafe to rely on without repair.

## Architecture Layers

| Layer | Boundary Status | Verification | Notes |
| --- | --- | --- | --- |
| CLI | Documented | `python -m unittest discover -s tests` | Keep runtime dependency-free |
| Action adapter | Documented | `tests/test_github_action.py` | Keep Action inputs mapped to library behavior |
| Component inventory | Documented | `tests/test_detect.py` | Keep nested project routing explicit before edits |
| Harness docs | Documented | `harnessforge audit --target .` | Keep root instructions short and detail in `docs/harness/` |

## Harness Simplification

At least monthly, review one harness component and decide whether it is still
useful. Keep it when it prevents repeated failures. Remove or merge it when it
adds upkeep without improving verification, restartability, or scope control.

Structural harness scores do not prove real agent effectiveness. Record
representative before/after agent-session evidence or benchmark notes before
making release claims about agent reliability.
