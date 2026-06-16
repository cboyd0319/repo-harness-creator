# Current State

Last Updated: 2026-06-16 UTC

## Current Objective

RunHaven field testing exposed review-finalization gaps that are now accepted
as the next product buildout. Release prep stays paused until structured
high-risk surface acceptance, review finalization, state migration, manifest
refresh, skill-wiring validation, and related report/maturity fixes are
implemented or explicitly deferred by maintainers. Structured high-risk surface
acceptance is implemented; review-finalization automation is next.

## Product State

- HarnessForge is an alpha/pre-release Python 3.13+ CLI and composite GitHub
  Action for creating, assessing, and updating AI coding-agent harnesses.
- No external deployment or compatibility boundary exists yet. Prefer the clean
  current product contract over legacy shims unless maintainers declare a
  release boundary.
- Product boundaries are explicit: repo-local HarnessForge docs and workflows,
  generated target harness content, CLI/runtime behavior, GitHub Action
  behavior, optional workflow scaffolds, tests/fixtures, release/package
  surfaces, research ledger, security/privacy controls, and platform contracts
  are separate surfaces.
- Target repos must not receive HarnessForge repo-local self-healing, local
  machine paths, sibling-checkout commands, personal tool mandates, or wording
  that makes HarnessForge canonical after initial generation.
- Generated target harnesses use the organized `docs/harness/` layout, include
  a zero-install `.agents/skills/harness/SKILL.md`, and keep repository docs
  and checks authoritative unless the owner opts into HarnessForge checks.

## State Contract

- `feature_list.json`: machine-readable feature state and major durable product
  evidence only.
- `docs/harness/evidence/evidence-log.md`: meaningful verification, audit,
  release, or source-review evidence only.
- `current-state.md`: current objective, restart context, blockers, trusted
  verification, touched surfaces, and next step.
- Do not recreate separate root progress or session-handoff files.

## Latest Verified Work

- `docs/` is organized into top-level product docs plus `docs/harness/`.
  `docs/harness/` uses the generated target layout: top-level `README.md`,
  `authoritative-facts.md`, and `manifest.json`, with detail under
  `boundaries/`, `feedback/`, `state/`, `evidence/`, `research/`,
  `operations/`, `release/`, and `schemas/`.
- `src/harnessforge/` is organized into top-level public entrypoints
  `cli.py` and `github_action.py`, plus `assessment/`, `core/`, `project/`,
  `generation/`, `evidence/`, and `templates/`.
- Manifest, roadmap, authoritative-facts, component-inventory, and evidence
  docs now name the organized source paths. Old flat module path references
  were removed except for stable schema identifiers such as
  `harnessforge.verify.v1`.
- Self-audit now includes a HarnessForge source package boundary check so
  stray top-level modules fail the product repo audit.
- Feature-state scope drift now treats `feature_list.json` and
  `current-state.md` as docs/state updates rather than `other`.
- The repo-local harness skill is deployed at `.agents/skills/harness/`,
  wired from `AGENTS.md`, and marked active for this repository. Generated
  target copies still start pending first-agent review.
- The main README has a prominent alpha/pre-release banner directly under the
  badges.
- `harnessforge report` now includes feature-state scope drift,
  runtime/process observability, and optional index-adapter status. Action
  summaries and `release-check` surface the same signals.
- `harnessforge enhance` and `init --enhance-existing --dry-run --json` now
  include task-class guidance and rule lifecycle metadata.
- The public-repo corpus has an offline metadata refresh script plus explicit
  `--verify-remote` mode for networked owner checks.
- Audit scoring now accepts completed or retired first-agent lifecycle state
  and correctly scores this repo's roadmap router against `docs/roadmap.md`.
- The accepted pre-release backlog is closed. Optional package/release evidence
  imports remain release-prep decisions, not current buildout blockers.
- RunHaven's manual harness repair exposed accepted next tasks: target-side
  high-risk review evidence, a review-finalization command or mode, split-state
  migration to `current-state.md`, structured review status values, manifest
  metadata refresh, harness skill-wiring validation, compact verification
  evidence capture, clearer advisory-versus-actionable report output, and a
  RunHaven-shaped regression fixture.
- High-risk surface acceptance is now target-contained evidence in
  `docs/harness/evidence/first-agent-review.json`. Readiness, report,
  release-check, GitHub Action summaries, and local self-reporting consume the
  evidence without treating generated pending placeholders as accepted review.
  This repo records accepted advisory review for its four instruction entry
  points and two workflows; generated target repos still start pending.

## Trusted Verification

- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 266 tests.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root . --check`
  passed.
- `PYTHONPATH=src:. python3 scripts/refresh_public_repo_corpus.py` passed.
- `PYTHONPATH=src:. python3 -m harnessforge corpus --min-score 90` passed
  with 13 fixtures and minimum score `100`.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 100`
  passed at `100/100`.
- `PYTHONPATH=src:. python3 -m harnessforge report --target . --since HEAD --json`
  produced parseable JSON with audit `100`, feature-state `aligned`,
  observability `strong`, and index-adapter status `tool_available`.
- After locking the RunHaven-derived next tasks, JSON validation, Markdown
  link check, `git diff --check`, self-audit, and report JSON smoke passed.
  The report showed audit `100`, feature-state `aligned`, docs fan-out
  `not_required`, readiness `warning`, and maturity `generated` with next
  level `reviewed`.
- After implementing structured high-risk acceptance, focused CLI/generator/
  Action/maturity tests passed with 172 tests; full unit discovery passed with
  266 tests; compileall passed; pin check passed; `git diff --check` passed;
  self-audit stayed `100/100`; report JSON smoke showed readiness `ready`,
  review-required `0`, accepted high-risk surfaces `6`, docs fan-out `warning`,
  maturity `reviewed`, and audit `100`. `python3 -m ruff check .` could not
  run because Ruff is not installed in the active interpreter.
- `PYTHONPATH=src:. python3 -m harnessforge release-check --target . --since HEAD --json`
  produced parseable JSON and returned the expected strict-gate blocked exit.
- `PYTHONPATH=src:. python3 -m harnessforge quickstart --target . --interactive --json`
  produced parseable JSON.
- `./init.sh` passed with 265 tests and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed with 265 tests and self-audit
  `100/100`.
- `git diff --check`, compileall, JSON validation, durable-doc local-path
  scan, and stale artifact cleanup passed.

## Touched Surfaces

- `current-state.md`
- `docs/roadmap.md`
- `docs/harness/evidence/evidence-log.md`
- `feature_list.json`
- `docs/action.md`
- `docs/capabilities.md`
- `docs/usage.md`
- `docs/harness/boundaries/component-inventory.md`
- `docs/harness/evidence/first-agent-review.json`
- `docs/harness/manifest.json`
- `docs/harness/research/source-record.schema.json`
- `docs/harness/research/source-record-example.json`
- `docs/harness/state/first-agent-task.md`
- `docs/harness/state/roadmap.md`
- `.agents/skills/harness/`
- `scripts/refresh_public_repo_corpus.py`
- `src/harnessforge/assessment/`
- `src/harnessforge/core/`
- `src/harnessforge/evidence/high_risk_acceptance.py`
- `src/harnessforge/generation/`
- `src/harnessforge/project/`
- `src/harnessforge/`
- `tests/`

## Blockers

- No known blockers.

## Next Step

Implement the RunHaven-derived review-finalization command or mode from
`docs/roadmap.md` before release prep resumes.
