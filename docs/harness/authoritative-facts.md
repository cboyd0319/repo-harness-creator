# Authoritative Facts And Docs Routing

Status: live

Use this file to reduce harness maintenance fan-out. Do not copy every fact
into every doc. Update the authoritative owner first, then update only the
surfaces listed in the routing table when the change affects them.

## Boundary Types Covered

| Boundary Type | Default Owner |
| --- | --- |
| Local repo harness | `docs/harness/README.md`, `docs/harness/boundaries/component-inventory.md` |
| Generated target harness | `src/harnessforge/templates/`, `src/harnessforge/generate.py`, generated manifest metadata |
| CLI/runtime behavior | `src/harnessforge/cli.py`, command modules, focused CLI tests |
| Existing project files | `harnessforge enhance`, generated addenda, and project-owned instruction files |
| GitHub Action | `action.yml`, `src/harnessforge/github_action.py`, `docs/action.md` |
| Optional workflow scaffolds | Generated CI workflow template and manifest ownership metadata |
| Tests and fixture corpus | `tests/`, `src/harnessforge/public_repo_corpus.py` |
| Release/package surface | `docs/harness/release/release-controls.md`, package metadata, release evidence |
| Research and source ledger | `docs/harness/research/research-sources.json`, lock file, `docs/harness/research/sources.md` |
| Security and privacy | `docs/harness/boundaries/security-boundary-map.md`, `feature-privacy-labels.json` |
| Platform contracts | `docs/harness/manifest.json`, platform source review metadata |
| Docs and UX | README, usage, capabilities, Action docs, and this routing map |

## Fact Owners

| Fact Class | Authoritative Owner | Other Surfaces Should |
| --- | --- | --- |
| Product boundary between HarnessForge local harness, generated target harnesses, and GitHub Action | `docs/harness/boundaries/component-inventory.md` | Link or summarize only the relevant boundary. |
| Pre-release compatibility and breaking-change policy | `docs/harness/boundaries/component-inventory.md`, `docs/harness/boundaries/change-contract.md` | Do not add migration docs or shims unless a release boundary is declared. |
| Repo-local versus generated `docs/harness/` layout | `docs/roadmap.md`, `docs/harness/boundaries/component-inventory.md` | Keep the local and generated organized layouts aligned; do not add repo-local flat docs back under `docs/harness/`. |
| CLI command behavior, flags, exit codes, and JSON contracts | `src/harnessforge/cli.py`, command modules, and focused tests | Summarize user-facing behavior in `docs/usage.md` when it changes. |
| GitHub Action inputs, outputs, and command modes | `action.yml`, `src/harnessforge/github_action.py`, and Action tests | Summarize in `docs/action.md` only. |
| Generated file list, required snippets, and local self-audit contract | `docs/harness/manifest.json` | Avoid duplicating snippet lists elsewhere. |
| Generated target content | `src/harnessforge/templates/` and generator tests | Update public docs only when user-visible generated behavior changes. |
| Audit scoring and report interpretation | `src/harnessforge/audit.py`, `src/harnessforge/evidence/report.py`, and tests | Keep scoring caveats in `docs/capabilities.md` and `docs/usage.md` short. |
| Accepted roadmap and backlog boundary | `docs/roadmap.md` | Reference from state files instead of duplicating full lists. |
| Current work state and evidence | `feature_list.json`, `current-state.md`, `docs/harness/evidence/evidence-log.md` | Use the specific file that owns the fact. Do not update state files as a routine bundle. |
| Verification commands and recurring gates | `docs/harness/feedback/verification-matrix.md`, `docs/harness/feedback/sensor-registry.md`, root entrypoints | Update only when a command, owner, or gate changes. |
| Research source allowlist and review evidence | `docs/harness/research/research-sources.json`, `docs/harness/research/research-sources.lock.json`, `docs/harness/research/sources.md` | Do not paste source catalogs into other docs. |

## Change-To-Docs Routing

| Change Type | Required Docs/State Updates | Usually Not Needed |
| --- | --- | --- |
| Small internal code fix with no CLI, generated output, Action, scoring, platform, security, or release impact | No durable doc update unless the active objective or next step changes | README, public docs, manifest snippets, roadmap, state bundle |
| CLI command, flag, JSON, or exit-code change | `docs/usage.md`, command tests, `docs/harness/manifest.json` only if required snippets change | `docs/capabilities.md` unless capability changes |
| Generated target artifact change | Template, generator tests, `docs/capabilities.md` generated-file list if user-visible, `docs/harness/manifest.json` for local snippet coverage | Broad README rewrite |
| Product boundary change | `docs/harness/boundaries/component-inventory.md`, focused tests, relevant public doc | Repeating the full boundary in every doc |
| Breaking generated, CLI, report, Action, or docs contract before release | `docs/harness/boundaries/component-inventory.md`, `docs/harness/boundaries/change-contract.md`, focused tests, relevant public doc | Backward-compatibility migration docs unless a release boundary exists |
| GitHub Action behavior change | `action.yml`, `docs/action.md`, Action tests, pin check if dependencies/actions change | Generated target docs unless Action output changes generated guidance |
| Audit/report scoring change | `docs/capabilities.md` or `docs/usage.md` if user-visible, scoring/report tests, `docs/harness/manifest.json` only for snippet contract | README unless positioning changes |
| Platform, dependency, workflow, or pin change | `docs/harness/boundaries/dependency-change-policy.md`, `pins.toml`, `scripts/check_pins.py`, relevant workflow/docs | Roadmap unless it changes accepted scope |
| Research source or source policy change | `docs/harness/research/sources.md`, `docs/harness/research/research-sources.json`, lock file, research check | CLI docs unless command behavior changes |
| Release-prep evidence change | `docs/harness/release/release-controls.md` when the release process changes, `docs/harness/evidence/evidence-log.md` when evidence must be preserved | Generated templates unless release guidance changes; state files unless stopping, handing off, or changing the objective |

## State File Write Thresholds

Do not update state files as a bundle.

- `feature_list.json`: update only for feature status transitions, active
  objective changes, or major product evidence that must survive beyond the
  current session.
- `current-state.md`: update only when the active objective, current verified
  state, blockers, touched surfaces, or next recommended step materially
  changes.
- `docs/harness/evidence/evidence-log.md`: update only after meaningful
  verification, release evidence, audit evidence, or source review that should
  be preserved. Do not log every focused test rerun.

## Fan-Out Budgets

Routine changes should have a small documentation footprint:

- 0-1 durable doc/state updates for isolated internal fixes.
- 1-3 docs/state updates for user-visible CLI, generated-content, Action, or
  audit changes.
- More than 3 docs/state updates only for boundary, platform, security,
  release, public README, or generated-contract changes.

When a small change appears to need more updates, stop and identify the
authoritative owner before editing. Prefer adding a link, manifest snippet, or
report field over repeating prose.

## Exceptions

Broader updates are expected for:

- product boundary changes;
- generated-file contract changes;
- security, privacy, dependency, or platform support changes;
- public README or release-prep work;
- current evidence entries after meaningful verification;
- removing stale duplicated facts.

## Audit And Report Expectations

Self-audit must ensure this map exists for the HarnessForge product repo.
`harnessforge report` should summarize whether this map is present, reviewed,
and manifest-tracked for target repos. `harnessforge report --since <ref>`
summarizes likely docs fan-out from the diff and flags stale duplicate facts
instead of requiring manual prose updates everywhere. Add
`--require-docs-fanout-budget` when over-budget fan-out or duplicate durable
fact blocks should block the report.
