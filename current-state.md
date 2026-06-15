# Current State

Last Updated: 2026-06-15 UTC

## Current Objective

Close the accepted pre-release backlog and resume release prep from a clean
docs, code, and harness boundary.

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

- `harnessforge report` now includes policy preset recommendations and SBOM
  adapter status.
- Expanded blueprint-backed policy presets cover open-source libraries,
  internal services, monorepos, CLI/dev tools, infrastructure/IaC,
  mobile/desktop apps, docs/research repos, legacy migrations, and
  education/training repos in addition to the existing presets.
- `quickstart --interactive --json` emits reproducible decisions without
  prompts or writes. Non-JSON `--interactive` prints the dry-run summary first,
  skips prompts without a TTY, and asks before writing in a real terminal.
- Enhance-existing plans include per-file instruction-quality recommendations.
- Report/evidence/policy helpers moved under `src/harnessforge/evidence/`;
  public CLI and Action entrypoints remain top-level.
- The docs/backlog consistency pass found no remaining accepted pre-release
  backlog. Optional release evidence imports are tracked as release-prep
  candidates, not current buildout blockers.

## Trusted Verification

- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 261 tests.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root . --check`
  passed.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed at `100/100`.
- `PYTHONPATH=src:. python3 -m harnessforge report --target . --json` produced
  parseable JSON.
- `PYTHONPATH=src:. python3 -m harnessforge release-check --target . --json`
  produced parseable JSON and returned the expected strict-gate blocked exit.
- `PYTHONPATH=src:. python3 -m harnessforge quickstart --target . --interactive --json`
  produced parseable JSON.
- `./init.sh` passed with 261 tests and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed with 261 tests and self-audit
  `100/100`.
- `git diff --check`, compileall, JSON validation, stale old-module-path scan,
  and local-path scan passed.

## Touched Surfaces

- `docs/roadmap.md`
- `docs/action.md`
- `docs/capabilities.md`
- `docs/usage.md`
- `docs/harness/README.md`
- `docs/harness/authoritative-facts.md`
- `docs/harness/boundaries/component-inventory.md`
- `docs/harness/manifest.json`
- `docs/harness/research/remaining-ideas-research.md`
- `src/harnessforge/`
- `tests/`

## Blockers

- No known blockers.

## Next Step

Commit the backlog-closure changes, then begin release prep.
