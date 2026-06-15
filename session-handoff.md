# Session Handoff

Last Updated: 2026-06-15 UTC

## Current Objective

Continue reducing HarnessForge harness maintenance and token cost while keeping
generated harness quality, product boundaries, and verification evidence intact.

## What Changed

- Evidence-gated harness maturity levels are implemented in unified report,
  release-check, and Action summaries. Levels are cumulative: generated,
  reviewed, verified, release-ready, then measured.
- Maturity remains separate from structural audit score and reports the next
  blocked evidence tier instead of treating a high audit score as proof of
  real-agent effectiveness.
- GitHub Action summaries are polished for report and sync. `command: report`
  now writes a compact signal table with readiness, score, drift, docs
  fan-out, verify/effectiveness evidence, instruction quality, first-agent
  lifecycle, repo-map counts, and SBOM count. `command: sync` now includes
  warning, review-required, runnable-check, instruction-quality, first-agent,
  and verify-evidence status.
- Compact repo maps are implemented in `index --json` and unified report. The
  map records primary languages, components, source-of-truth docs, manifest
  kinds, entrypoints, boundary examples, verification commands,
  review-required files, unknowns, and SBOM evidence without private code
  summaries.
- Existing SPDX and CycloneDX-style SBOM files are detected and cited. Normal
  read-only flows do not generate SBOMs or run target commands.
- Instruction-quality reporting is implemented in readiness and unified report.
  It reports startup instruction section coverage, signal/noise, placeholder
  noise, word/line/byte budget status, largest instruction surfaces, and
  warning-mode count metadata.
- The implementation borrows the useful Persona content-budget patterns:
  deterministic counts, explicit budgets, largest-offender reporting, and
  warning-mode review rather than hard blocking target repos.
- Local `docs/harness/evidence/first-agent-review.json` now exists so the
  repo-local harness shape matches generated target harnesses.
- Local `AGENTS.md` is 998 words, below the 1,000-word hard budget for primary
  startup instructions.
- First-agent lifecycle evidence is implemented. Generated targets include
  `docs/harness/evidence/first-agent-review.json`, and report/readiness
  classify first-agent review as pending, completed, retired, blocked, invalid,
  or stale.
- Agent Skills `.md` references are now treated as the canonical source URLs
  for generated repo skill guidance.
- Generated repo skills were rechecked against the Agent Skills specification.
  `SKILL.md` now uses a one-level
  `references/repo-harness.md` route, with detailed repo paths in the bundled
  reference file.
- RunHaven's deployed skill copy was updated to the same shape during the
  active harness migration; RunHaven audit is now `100/100`.
- Generated target harness Markdown was compacted without deleting safety
  surfaces.
- Representative generated Markdown is now 69,927 bytes after adding
  first-agent lifecycle evidence, down from 85,839 bytes and 1,730 lines.
- Representative generated total output is now 139,404 bytes after adding
  first-agent lifecycle evidence, down from 160,684 bytes and 4,190 lines at
  the start of the second pass.
- Generated targets no longer receive this repo's product-local research
  source allowlist; generated manifests are compact machine-readable JSON.
- Repo-local `remaining-ideas-research.md` was compacted from 913 lines to 86
  lines; active `docs/harness` Markdown is now 2,764 lines.
- Generated audit remains `100/100`.
- `tests/test_generate_audit.py` now includes generated-footprint regression
  caps for Markdown and total output.
- Root startup state was compacted from 2,557 combined lines to 153 combined
  lines. Historical detail remains in git history and the compact evidence log.
- Local and generated startup routes now read compact state first and make
  heavier docs task-specific.

## Files

- `src/harnessforge/maturity.py`
- `tests/test_maturity.py`
- `src/harnessforge/report.py`
- `src/harnessforge/release_check.py`
- `src/harnessforge/github_action.py`
- `src/harnessforge/templates/agent-operating-model.md.tmpl`
- `src/harnessforge/templates/agents.md.tmpl`
- `src/harnessforge/templates/authoritative-facts.md.tmpl`
- `src/harnessforge/templates/first-agent-task.md.tmpl`
- `src/harnessforge/templates/harness-readme.md.tmpl`
- `src/harnessforge/templates/harness-skill.md.tmpl`
- `src/harnessforge/templates/harness-skill-reference.md.tmpl`
- `src/harnessforge/templates/first-agent-review.json.tmpl`
- `src/harnessforge/templates/quality-document.md.tmpl`
- `src/harnessforge/templates/roadmap.md.tmpl`
- `src/harnessforge/templates/security-boundary-map.md.tmpl`
- `src/harnessforge/templates/source-record.schema.json.tmpl`
- `src/harnessforge/templates/source-record-example.json.tmpl`
- `src/harnessforge/templates/sources.md.tmpl`
- `src/harnessforge/templates/verification-matrix.md.tmpl`
- `src/harnessforge/audit.py`
- `src/harnessforge/generate.py`
- `src/harnessforge/first_agent.py`
- `src/harnessforge/github_action.py`
- `src/harnessforge/harness_paths.py`
- `src/harnessforge/indexer.py`
- `src/harnessforge/instruction_quality.py`
- `src/harnessforge/readiness.py`
- `src/harnessforge/report.py`
- `tests/test_generate_audit.py`
- `tests/test_cli.py`
- `tests/test_github_action.py`
- `docs/action.md`
- `AGENTS.md`
- `docs/harness/manifest.json`
- `docs/harness/README.md`
- `docs/harness/evidence/evidence-log.md`
- `docs/harness/evidence/first-agent-review.json`
- `docs/harness/research/source-record.schema.json`
- `docs/harness/research/source-record-example.json`
- `docs/roadmap.md`
- `progress.md`
- `session-handoff.md`

## Verification To Trust

Latest checks:

- focused maturity, CLI, and Action tests passed with 110 tests
- full unit discovery passed with 258 tests
- compile, JSON validation, pin check, research source check, self-audit
  `100/100`, generated smoke audit `100/100`, report JSON smoke,
  expected-block release-check JSON smoke, diff hygiene, and local-path scan
  passed
- local report JSON emitted `harnessforge.maturity.v1` with current level
  `generated` and next level `reviewed`
- local release-check JSON emitted valid maturity summary and returned expected
  strict-gate `blocked` status
- accepted roadmap item remains for reorganizing `src/harnessforge/`
- focused CLI tests passed with 82 tests
- focused Action tests passed with 21 tests
- focused generated/audit tests passed with 56 tests
- full unit discovery passed with 251 tests
- fresh generated-target audit passed at `100/100`
- HarnessForge self-audit passed at `100/100`
- index/report JSON smokes emitted `harnessforge.repoMap.v1`
- HarnessForge `git diff --check` passed
- JSON validation passed for `feature_list.json`, `docs/harness/manifest.json`,
  and `docs/harness/evidence/first-agent-review.json`
- local-path scan found only intentional redaction fixtures and regexes
- local `AGENTS.md` is 998 words, below the hard budget

Earlier optimization checks also passed before the spec adjustment:

- compile passed
- explicit Agent Skills spec validation passed for a fresh render and the
  RunHaven deployed skill
- RunHaven audit passed at `100/100`
- self-audit passed at `100/100`
- JSON validation passed for `feature_list.json` and
  `docs/harness/manifest.json`
- report smoke passed with no duplicate durable fact blocks
- public fixture corpus passed with 13 fixtures and minimum score `100`
- stale flat-path scan was clean
- representative generated Markdown was 69,927 bytes and total generated output
  was 139,404 bytes after adding first-agent evidence

Rerun focused tests after any further template or scoring edit.

## Constraints To Preserve

- Generated target repos must not receive HarnessForge repo-local self-healing
  docs or workflows.
- Generated docs should not say HarnessForge is canonical for a target repo.
  Repo-owned docs and checks are canonical unless the owner opts into the
  GitHub Action or a recurring HarnessForge command.
- Contributors should not need HarnessForge installed after initial generation.
  The generated repo skill is the zero-install maintenance path.
- Keep root startup files compact. Put durable product rules in the specific
  harness doc that owns them.
- Avoid adding compatibility shims before release unless a maintainer declares a
  real compatibility boundary.

## Blockers

- No known blockers.

## Next Session

If the user wants more backlog work, continue with instruction-quality and
signal-to-noise task-class guidance, optional SBOM adapter design,
`src/harnessforge/` organization, expanded policy presets, or interactive
quickstart/init UX. The user asked to commit and push after the current turn,
then continue.
