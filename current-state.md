# Current State

Last Updated: 2026-06-15 UTC

## Current Objective

Consolidate routine harness state so local and generated harnesses use one
current-state file, keep `feature_list.json` machine-readable, and reserve the
evidence log for meaningful verification evidence.

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

- Root `progress.md` and `session-handoff.md` are obsolete. Local and generated
  harnesses now use root `current-state.md`.
- Generated target harnesses create `current-state.md` and no longer render
  progress or session-handoff templates.
- Audit scoring, session snapshots, manifest snippets, self-heal staging, and
  generated docs use the new state contract.
- `feature_list.json` remains because audit/release state needs a
  machine-readable feature ledger.
- `docs/harness/evidence/evidence-log.md` remains for meaningful preserved
  verification, release, audit, or source-review evidence only.

## Trusted Verification

- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 258 tests.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root . --check`
  passed.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed at `100/100`.
- Generated target CLI smoke passed: `init` wrote `current-state.md`, did not
  write old progress/handoff files, and audit returned `100/100`.
- Session JSON smoke passed and reports `current-state.md` with no old root
  progress/handoff entries.
- `git diff --check`, `compileall`, and JSON validation passed.

## Touched Surfaces

- `docs/roadmap.md`
- `docs/harness/authoritative-facts.md`
- `docs/harness/boundaries/component-inventory.md`
- `docs/harness/state/`
- `docs/harness/feedback/`
- `src/harnessforge/`
- `src/harnessforge/templates/`
- `.github/workflows/harness-self-heal.yml`
- `tests/`

## Blockers

- No known blockers.

## Next Step

Continue accepted pre-release backlog before release prep: optional SBOM
adapter design, expanded policy presets, interactive quickstart/init UX, and
`src/harnessforge/` organization.
