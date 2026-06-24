# Quality Document

Last Updated: 2026-06-24

Use this as a periodic codebase health snapshot. It is separate from the
evaluator rubric: the rubric scores one work session, while this document scores
the repo over time.

## Domain Grades

| Domain | Grade | Verification Status | Agent Legibility | Key Gaps |
| --- | --- | --- | --- | --- |
| CLI package | A | 316 local tests pass | Clear module boundaries | No current cleanup gap |
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

## Harness Subsystem Health

Review instructions, state, verification, scope, and lifecycle separately.
Treat verification as the first subsystem to repair when checks are missing,
stale, or vague. Tools, environment metadata, reports, workflows, and policy
docs are support surfaces.

| Subsystem | Status | Evidence | Next Improvement |
| --- | --- | --- | --- |
| Instructions | A | Root instructions and platform routers exist; self-audit instructions domain passes | Keep root instructions map-like |
| State | A | `feature_list.json`, `current-state.md`, and `docs/roadmap.md` are maintained | Keep only one active objective unless explicit multi-agent ownership exists |
| Verification | A | Unit tests, pin check, research source check, self-audit, verification matrix, and sensor registry are current | Keep checks explicit before adding broader process |
| Scope | A | Change contract, component inventory, security map, and feature dependencies are maintained | Keep generated and local surfaces from drifting into each other |
| Lifecycle | A | `current-state.md`, first-agent review, clean-state checklist, and evidence handoff are maintained | Keep restart state compact and current |

## Clean-State Dimensions

Track these dimensions at session exit and during periodic cleanup.

| Dimension | Status | Evidence | Gap |
| --- | --- | --- | --- |
| Build or static checks pass | A | `python -m compileall`, unit tests, and self-audit are routine verification | Keep Windows/macOS live platform checks as release checkpoints when not run locally |
| Tests or behavior checks pass | A | Unit discovery and focused command smokes cover current CLI behavior | Real agent task effectiveness is intentionally separate evidence |
| Current and feature state are accurate | B | `current-state.md`, `feature_list.json`, and `docs/roadmap.md` are maintained during backlog work | Keep state writes limited to the file that owns the changed fact |
| Complexity and scope stayed minimal | B | Root and generated instructions, change contract, rubric, and operating model now gate assumptions, speculative features, new dependencies, drive-by refactors, and intentional simplification ceilings | Need representative real-agent tasks to prove the guidance reduces rework |
| Temporary or stale artifacts are removed or documented | A | Local-path scans and diff hygiene are part of verification | Keep scratch reports and generated evidence target-relative |
| Standard startup path still works | B | `./init.sh` passed with 316 tests and self-audit `100/100`; local `pwsh` command execution currently fails before repo code loads | Re-run `init.ps1` on a healthy PowerShell host or after local `pwsh` is repaired before publishing release evidence |

## Benchmark Or Task Evidence

Use fixed representative tasks when making claims about harness quality,
cleanup impact, or agent effectiveness.

| Evidence Date | Harness Variant | Task Set | Completion Rate | Retries Or Cost | Defects Caught Before Review | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-06-15 | Current generated harness | Structural generated-target and audit smokes | 100/100 structural audit | Local unit/test cost only | Structural drift and missing generated sections | Not proof of real-agent effectiveness |

## Harness Simplification

At least monthly, review one harness component and decide whether it is still
useful. Keep it when it prevents repeated failures. Remove or merge it when it
adds upkeep without improving verification, restartability, or scope control.

Run an ablation when validating a component's value: snapshot the benchmark
evidence above, remove or disable one component, rerun the same task set, and
compare. Keep the component removed when grades and completion do not drop.

| Date | Component Reviewed | Ablation Result | Decision |
| --- | --- | --- | --- |
| REVIEW REQUIRED | Pending component | Degraded or unchanged | Restore or keep removed |

Structural harness scores do not prove real agent effectiveness. Record
representative before/after agent-session evidence or benchmark notes before
making release claims about agent reliability.
