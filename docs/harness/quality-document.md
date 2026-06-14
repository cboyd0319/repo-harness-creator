# Quality Document

Last Updated: 2026-06-14

Use this as a periodic codebase health snapshot. It is separate from the
evaluator rubric: the rubric scores one work session, while this document scores
the repo over time.

## Domain Grades

| Domain | Grade | Verification Status | Agent Legibility | Key Gaps |
| --- | --- | --- | --- | --- |
| CLI package | A | 22 local tests pass | Clear module boundaries | Hosted CI still pending |
| GitHub Action | B | Local adapter tests and pin checks pass | Action docs present | Needs live `uses: ./` verification on hosted runners |
| Harness templates | A | Self-audit passes | Templates include state, security, privacy, component, and lifecycle docs | Needs real repo dogfooding beyond this bootstrap |
| Supply chain | A | Pin checker passes | Exact package pins and SHA-pinned Actions are documented | Hosted CI enforcement pending |
| Self-healing | B | Research refresh script and workflow exist | Reviewed PR loop, no silent merge | Scheduled run pending until pushed |

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
