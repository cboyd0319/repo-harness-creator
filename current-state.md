# Current State

Last Updated: 2026-06-16 UTC

## Current Objective

The accepted non-release backlog is complete when HarnessForge has completed or
explicitly deferred every accepted pre-release item in `docs/roadmap.md`:
token economics research, Kubernetes-scale discovery ranking, generated
guidance quality, feature-state gates, instruction lifecycle/SNR review,
generated harness fallback hardening, deeper `enhance` planning, selected
index/SBOM adapters, policy preset evidence, more real-repo fixtures, expanded
large-public-repo field runs, and deeper instruction-quality scoring.
Release prep starts only after that backlog is closed or intentionally deferred
by the maintainer.

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
- The RunHaven-derived backlog, deterministic large-repo slices, and script
  cleanup are closed. The maintainer has promoted the remaining non-release
  follow-up work into accepted pre-release backlog before release prep.
  Optional package/release evidence imports remain release-prep decisions, not
  current buildout blockers.
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
- `harnessforge finalize-review` and Action `command: finalize-review` now
  finalize first-agent review evidence explicitly. Apply mode can retire the
  first-agent task, refresh manifest metadata, and record accepted advisory
  high-risk surface evidence only when maintainers pass the acceptance flag.
- Destructive, overwrite-capable, apply-mode, or command-executing local CLI
  paths warn and require confirmation. Non-interactive runs must pass `--yes`;
  interactive terminals must type `yes`. Covered paths include `init --force`,
  `update --apply`, `blueprint apply`, `verify --run`, and
  `finalize-review --apply`.
- Readiness and report JSON now expose structured `reviewSurfaces` plus
  `reviewStatusSummary` with machine status values. `finalize-review` consumes
  those fields instead of parsing human-readable review-required strings.
- `harnessforge migrate-state` and Action `command: migrate-state` now plan
  and explicitly apply bounded migration from root `progress.md` and
  `session-handoff.md` into `current-state.md`. Apply mode preserves the
  legacy files, requires `--yes` for non-interactive CLI writes, and does not
  run target commands. Audit scoring now penalizes stale split root state.
- Readiness, report, release-check, and Action summaries now validate
  repo-local harness skill wiring when a HarnessForge-style harness is present.
  The validator checks skill frontmatter, reference file presence, reference
  paths, zero-install guidance, and whether root instructions route
  harness-maintenance work to `.agents/skills/harness/SKILL.md`.
- `harnessforge verify --evidence-summary` and Action `verify-summary` now
  write compact `harnessforge.verifySummary.v1` evidence without stdout or
  stderr previews. Readiness and release gates consume both full verify reports
  and compact verify summaries.
- `harnessforge report` now includes `harnessforge.reviewWork.v1`, separating
  unresolved actionable review work from accepted advisory inventory.
  `docs/harness/feedback/report-json-contract.md` documents stable downstream
  report fields.
- The offline public-repo corpus now includes a RunHaven-shaped reviewed-harness
  fixture with existing instruction routers, CI workflow, multiple container
  runtime files, `current-state.md`, retired first-agent lifecycle evidence,
  accepted high-risk surface review, and reviewed maturity/report expectations.
- Public docs, generated templates, the composite Action docs, release controls,
  verification guidance, and the live manifest are updated for compact verify
  evidence, review-work reporting, the report JSON contract, and the
  RunHaven-shaped fixture.
- Repo-local `.github/` surfaces were rechecked. The Copilot router and PR
  template remain short, portable, and repo-owned. CI now compiles `scripts`,
  runs the research ledger check, uses job timeouts, and gates this repo at
  self-audit score `100`. The scheduled self-heal workflow now passes `--yes`
  for non-interactive writes, verifies the research ledger, stages
  `.agents/skills/harness`, fails on unstaged or untracked output, and uses
  signed-off commits. Generated target-repo templates still keep the generic
  audit default and do not receive repo-local self-healing.
- Automatic GitHub Actions workflows are parked during alpha/pre-release to
  avoid runner cost while commits are frequent. The reviewed workflow
  definitions live at `.github/workflows/ci.yml.disabled` and
  `.github/workflows/harness-self-heal.yml.disabled`; restore runnable `.yml`
  suffixes only at an intentional release-prep boundary.
- The main README has been reorganized around the public product questions:
  what HarnessForge is, why repo owners want it, what makes it useful, and the
  repo-local versus generated versus Action boundaries. The duplicate
  at-a-glance/value-prop table was removed, while required README snippets and
  command references remain intact.
- The main README dedupe pass removed the duplicate command catalog and merged
  repeated boundary/default-safety prose into one concise section. Detailed
  command usage stays in `docs/usage.md`; full generated-file and security
  boundaries stay in `docs/capabilities.md`.
- Latest CI failure on `main` was traced to test helpers that used
  `sys.executable` as a generated target verification command. In CI-style
  editable installs that value is a temp venv path, so generated fixture
  harnesses contained machine-local absolute paths and failed installed-package
  report/audit expectations. CLI and Action tests now use portable `python3`
  on POSIX and `python` on Windows for generated fixture commands.
- `docs/capabilities.md` is now organized as a reader-facing guide: quick map,
  repository understanding, harness generation, existing-instruction review,
  audit/report/release evidence, opt-in extensions, default boundaries,
  generated files, security model, effectiveness boundary, and repo-local
  self-healing.
- `docs/harness/research/` was refreshed and tightened. The source inbox and
  lock file were regenerated from the fixed allowlist, the human-maintained
  research notes now distinguish implemented work from future candidates, and
  `sources.md` records which research files are generated versus
  human-maintained.
- `docs/harness/research/README.md` now owns the repo-local research directory
  map, generated-file boundary, update rules, and verification commands.
  Generated target harnesses now include a compact
  `docs/harness/research/README.md` that points to `sources.md`,
  `research-inbox.md`, and source-record schema/example files while keeping
  HarnessForge product-level research allowlists out of target repos.
- `docs/harness/research/large-public-repo-corpus.json` now defines a
  13-repo real large public GitHub field corpus separate from the offline
  fixture corpus used by `harnessforge corpus`.
- `scripts/analyze_large_public_repos.py` analyzes existing or explicitly
  cloned public checkouts under ignored `.harnessforge/large-public-repos/`.
  It does not run target commands, keeps reports target-relative, detects
  existing nested `AGENTS.md`, and emits review-required nested instruction
  scope candidates instead of writing nested files by default.
- Initial field evidence covered Kubernetes, VS Code, and Bazel. All three
  cloned and analyzed successfully. The run exposed accepted product follow-up
  gaps: generation dry-runs need a large-repo `max-files` or index-reuse path,
  and large monorepos need review-required nested `AGENTS.md` scope planning in
  product report/dry-run flows.
- `docs/harness/research/large-public-repo-gap-analysis.md` now turns that
  field evidence into a build-order gap analysis. It separates deterministic
  product fixes from review-required heuristics, optional adapters, and
  release-prep evidence needs.
- The first deterministic large-repo fix is implemented. `create_harness`,
  `quickstart`, `init`, applied `update`, and Action generation paths accept
  explicit file scan limits; dry-run JSON and generated manifests report scan
  coverage; `.harnessforge/` scratch checkouts are ignored by repo detection.
  Refreshed field evidence no longer reports `generator_default_scan_limit`.
- Nested instruction planning now uses shared product code through
  `harnessforge.nestedInstructionPlan.v1`. `report`, `index`, `enhance`,
  `quickstart`, and `init --dry-run` surface review-required nested
  `AGENTS.md` candidates for monorepos without writing nested instruction
  files by default. The field analyzer consumes the same planner.
- Nested instruction candidate ranking now uses component-local `localDocs`,
  verification command attribution, and workflow path/working-directory
  signals. Candidate JSON includes compact `rankSignals` and `reviewFocus`
  while keeping nested `AGENTS.md` writes disabled by default.
- Component-overflow-derived nested instruction candidates now remain separate
  under `omittedCandidateComponents`, `omittedCandidateCount`,
  `omittedCandidateListTruncated`, and `omittedGuidance`. This keeps normal
  candidate lists bounded while telling maintainers when to raise
  `--component-limit` or manually review omitted component scopes.
- `docs/roadmap.md` now includes an accepted research-backed harness token
  economics task requiring receipts on whether comprehensive repo harnesses
  increase or decrease agent token consumption before generated sizing or
  loading behavior changes.
- `docs/roadmap.md` now treats all remaining non-release follow-up work as
  accepted pre-release backlog before release prep: Kubernetes-scale discovery
  ranking, generated guidance quality, feature-state gates, instruction
  lifecycle/SNR review, generated harness fallback hardening, deeper
  `enhance`, selected index/SBOM adapters, policy preset evidence, more
  real-repo fixtures, expanded large-public-repo field runs, and deeper
  instruction-quality scoring.
- `script cleanup and organization` is implemented. Root verification entrypoints,
  repo-local maintenance utilities under `scripts/`, and generated script
  templates have compact top-of-file purpose headers. The current script layout
  stayed in place because each script remains referenced by docs, entrypoints,
  tests, corpus tooling, or generated target harnesses.
- `.gitignore` now covers the repo's current OS/editor noise, local secrets,
  agent/tool overrides, Python caches and environments, temporary
  package-manager artifacts, build and coverage outputs, HarnessForge scratch
  space, transient reports, and root AI-generated scratch reports.
- Token economics now has an initial source-backed research note and metric
  schema. The note directly maps repository-harness mechanisms to possible
  context/token and execution effects, treats the Walking Labs lectures as
  mechanism rationale rather than quantitative proof, and records static
  HarnessForge fixture sizing as proxy evidence only. The evidence path is now
  locked: native agent telemetry first, Codex JSONL for the first parser spike,
  Claude Code OpenTelemetry for cache read/write and tool-span buckets,
  optional Promptfoo/Langfuse/Phoenix/OpenLLMetry support after native traces
  exist, and proxy/gateway token logs only as API-level supplements.
  Controlled provider or agent task traces are still required before changing
  generated sizing, routing, summarization, or lazy-loading behavior.
- Research refresh now allows normal fetch mode to regenerate stale generated
  lock and inbox files after source allowlist changes while keeping
  `--check` strict about generated-output consistency.
- Large-repo file coverage reporting now uses `harnessforge.fileCoverage.v1`.
  `index`, `report`, `quickstart`, `init --dry-run`, Action report summaries,
  and large-public-repo field evidence expose scanned count, total tracked
  count when git is available, scan-eligible counts, intentionally skipped
  tracked-file counts, inventory source, category coverage, omitted examples,
  and warnings. The refreshed Kubernetes, VS Code, and Bazel field run shows
  Bazel complete for eligible coverage, VS Code budget-limited only for one
  remaining eligible path, and Kubernetes still genuinely budget-limited;
  `file_discovery_priority` remains open for deeper Kubernetes-scale ranking.
- Component inventory overflow now uses `harnessforge.componentOverflow.v1`.
  `index`, `report`, `quickstart`, `init`, `update`, `release-check`, the
  GitHub Action, and the field analyzer accept component limits where they
  already expose file scan limits. Field evidence now reports Kubernetes
  `44/44`, VS Code `80/145`, and Bazel `80/186` included/detected
  components at the default cap.
- Verification command metadata now uses
  `harnessforge.verificationCommands.v1`. Detection keeps the existing command
  strings but adds command class, scope, source type, source path, source
  detail, and confidence. `index`, `report`, generated manifests, Action report
  summaries, quickstart/init profile JSON, and large-public-repo field evidence
  consume the metadata without executing target commands.
- Source-of-truth detection now separates global `sourceOfTruth` docs from
  component-local `localDocs`. `index`, `report`, compact `repoMap`, Action
  summaries, and large-public-repo field evidence expose both counts so root
  startup guidance stays high-signal while nested README/docs files remain
  discoverable for scoped work.

## Trusted Verification

- Latest completed full verification: affected CLI/Action/generator/corpus/
  report/maturity suite passed with 198 tests; full unit discovery passed with
  285 tests; `./init.sh` passed with 285 tests and self-audit `100/100`;
  compileall, pin check, research source check, public corpus metadata check,
  JSON validation, `git diff --check`, durable-doc local-path scan, self-audit
  `100/100`, report JSON smoke, expected-block release-check JSON smoke, and
  offline corpus quality gate with 14 fixtures at minimum score `100` passed.
- Current cleanup/docs pass verification: `./init.sh` passed with 285 tests and
  self-audit `100/100`; `harnessforge corpus --min-score 90` passed with 14
  fixtures at minimum score `100`; report JSON smoke showed schema
  `harnessforge.report.v1`, audit `100`, readiness `ready`, skill wiring
  `wired`, and `0` unresolved review-work items; release-check JSON smoke
  returned the expected strict-gate blocked exit for missing current run-mode
  verify evidence; JSON validation, stale-doc scans, artifact scans, and `git
  diff --check` passed.
- Current `.github/` pass verification: `tests.test_pins` passed with 21
  tests; `tests.test_generate_audit tests.test_local_entrypoints` passed with
  63 tests; full unit discovery passed with 287 tests; compileall, pin check,
  research source check, JSON validation, self-audit `100/100`, and `./init.sh`
  passed.
- Current Actions parking verification: focused pins, generated-audit, and
  Action tests passed with 110 tests; `scripts/check_pins.py --root .` passed
  while scanning parked workflow definitions; self-audit stayed `100/100`;
  JSON validation and diff hygiene passed.
- Current file-coverage verification: affected CLI, Action, field-analysis,
  and report-contract tests passed with 141 tests; focused field-analysis and
  report-contract tests passed with 7 tests after doc/manifest alignment;
  full unit discovery passed with 299 tests; compileall, pin check, research
  source check, JSON validation, report JSON smoke, expected-block
  release-check JSON smoke, durable-doc local-path scan, and diff hygiene
  passed; self-audit stayed `100/100`; refreshed field evidence analyzed
  Kubernetes, VS Code, and Bazel with zero failures, Bazel complete for
  eligible coverage, and VS Code budget-limited only for one remaining
  eligible path.
- Current component-overflow verification: focused detect, CLI, Action, and
  field-analysis tests passed with 47 tests; compile/py_compile checks passed;
  full unit discovery passed with 301 tests; compileall, pin check, research
  source check, JSON validation, report JSON smoke, expected-block
  release-check JSON smoke, durable-doc local-path scan, diff hygiene, and
  self-audit `100/100` passed. Refreshed Kubernetes, VS Code, and Bazel field
  evidence analyzed 3/3 repos with zero failures and records included/total
  component counts.
- Current verification-command metadata verification: focused detect, CLI,
  Action, generated-audit, and large-public-repo analyzer tests passed with
  107 tests; full unit discovery passed with 302 tests; compileall, pin check,
  research source check, JSON validation, report JSON smoke, expected-block
  release-check JSON smoke, durable-doc local-path scan, diff hygiene, and
  self-audit `100/100` passed. Refreshed Kubernetes, VS Code, and Bazel field
  evidence analyzed 3/3 repos with zero failures and records high-confidence
  source attribution for detected verification commands.
- Current source/local-doc split verification: focused generated-audit,
  index, Action report, large-public-repo analyzer, and public-corpus tests
  passed with 67 tests; full unit discovery passed with 302 tests; compileall,
  pin check, research source check, JSON validation, report JSON smoke,
  expected-block release-check JSON smoke, durable-doc local-path scan, diff
  hygiene, and self-audit `100/100` passed. Refreshed Kubernetes, VS Code, and
  Bazel field evidence analyzed 3/3 repos with zero failures and now reports
  global/local doc counts, including Kubernetes `2/103`, VS Code `4/67`, and
  Bazel `3/79`.
- Current nested-candidate ranking verification: focused CLI and
  field-analyzer regressions passed; full unit discovery passed with 302 tests;
  compileall, pin check, research source check, JSON validation, report JSON
  smoke, expected-block release-check JSON smoke, and self-audit `100/100`
  passed. Refreshed Kubernetes, VS Code, and Bazel field evidence analyzed 3/3
  repos with zero failures and ranked candidates using local docs,
  verification sources, and workflow routing signals.
- Current nested-plan index/enhance verification: focused CLI and field
  analyzer regressions passed with 6 tests after fixing the overflow fixture;
  full unit discovery passed with 304 tests;
  refreshed field evidence analyzed Kubernetes, VS Code, and Bazel with 3/3
  successful repos and zero failures. The persisted field report now shows
  normal and omitted nested candidate counts, including VS Code `77/65` and
  Bazel `79/106` candidates/omitted at the default 80-component cap.
- Current README pass verification: required README manifest snippet check
  passed with no missing snippets; duplicate literal prose scan found no
  repeated meaningful lines; `tests.test_generate_audit` passed with 59 tests;
  self-audit passed at `100/100`; `git diff --check` passed.
- Current CI-fix verification: `gh run view 27628725293 --job 81697487692
  --log` identified the failing CI `Tests` step; the three affected report and
  release-check tests passed locally; a fresh Python 3.13 venv reproduced the
  CI editable-install path; installed-package `python -m unittest discover -s
  tests` passed with 287 tests after the fix.
- Current README dedupe verification: required README manifest snippet check
  passed with no missing snippets; literal duplicate meaningful-line scan found
  no repeated lines; README is 181 lines and 969 words before final checks.
- Current capabilities/research cleanup verification: refreshed 107 research
  sources with 1 known source failure (`redhat-structured-workflows` returns
  HTTP 403); `scripts/refresh_research.py --root . --check` passed; JSON
  validation for all research JSON files passed; durable research docs local
  path scan found no leaks; required capabilities manifest snippet check passed
  with no missing snippets; duplicate meaningful-line scan for
  `docs/capabilities.md` found no repeats; `tests.test_generate_audit`,
  `tests.test_pins`, and `tests.test_verify_contract` passed with 85 tests;
  self-audit passed at `100/100`; `git diff --check` passed; `./init.sh`
  passed with 287 tests and self-audit `100/100`.
- Current research README verification: generated harness smoke confirmed
  `docs/harness/research/README.md` is generated and
  `docs/harness/research/research-sources.json` is not; required live manifest
  snippet check passed; `tests.test_generate_audit`, `tests.test_refresh_research`,
  and `tests.test_pins` passed with 100 tests; `scripts/refresh_research.py
  --root . --check` passed; self-audit passed at `100/100`; `git diff --check`
  passed; `./init.sh` passed with 287 tests and self-audit `100/100`.
- Current large public repo field-corpus verification: corpus JSON and field
  evidence JSON parse cleanly; `scripts/analyze_large_public_repos.py --list
  --json` passed; real analysis against Kubernetes, VS Code, and Bazel passed
  with three analyzed repos and zero failed repos; focused large-corpus and
  public-corpus tests passed with 5 tests; local-path scan across new required
  artifacts found no machine-local path text; focused pin/corpus tests passed
  with 27 tests; `./init.sh` passed with 290 tests, pin check, research source
  check, and self-audit `100/100`.
- Current gap-analysis verification: `docs/harness/research/large-public-repo-gap-analysis.md`
  was checked against the field evidence JSON and roadmap source; JSON
  validation and diff hygiene passed.
- Current large-repo scan-limit verification: focused generator, CLI, Action,
  and field-analysis regressions passed with 8 tests; full unit discovery
  passed with 294 tests; pin check, research check, self-audit `100/100`, JSON
  validation, local-path scan, and diff hygiene passed; index/report smokes
  showed 174 files with no truncation; real field analysis against Kubernetes,
  VS Code, and Bazel passed with 3 analyzed repos, 0 failures, and no
  `generator_default_scan_limit` finding. Remaining cross-repo finding is
  `nested_agents_plan`.
- Current nested-instruction verification: focused CLI, Action, and
  field-analysis tests passed with 135 tests; full unit discovery passed with
  296 tests; compileall, pin check, research check, self-audit `100/100`, JSON
  validation, local-path scan, and diff hygiene passed; real field analysis
  against Kubernetes, VS Code, and Bazel passed with 3 analyzed repos, 0
  failures, and `harnessforge.nestedInstructionPlan.v1` candidate plans for
  all three repos.
- Current cleanup pass removed ignored local artifacts: `__pycache__`, `*.pyc`,
  `.DS_Store`, `.pytest_cache`, `htmlcov`, and `.coverage` if present.
- Current script cleanup verification: focused local-entrypoint, generated
  harness, pin, public-corpus, and large-public-repo script tests passed with
  93 tests; compileall across `scripts`, `src`, and `tests` passed;
  `git check-ignore` confirmed representative `.harnessforge`, `.DS_Store`,
  `__pycache__`, `node_modules`, virtualenv, coverage, test-results, and
  dist artifacts are ignored; a direct purpose-header scan checked 9 live and
  generated script/template files; `git diff --check` passed; `./init.sh`
  passed with 306 tests, pin check, research source check, and self-audit
  `100/100`.
- Current token-economics research verification: AGY-assisted discovery,
  direct source review, Walking Labs lecture review, and a 14-fixture static
  HarnessForge sizing proxy informed the research note; focused
  `tests.test_refresh_research` passed with 21 tests; generated-content tests
  passed with 60 tests; research refresh checked 125 sources with one known
  Red Hat 403 and `--check` passed; JSON validation, representative
  `.gitignore` checks, durable-doc local-path scan, diff hygiene, and
  self-audit `100/100` passed. Controlled provider or agent task traces remain
  the unclosed evidence gap.
- Current known local verification gap: `pwsh -NoProfile -File ./init.ps1`
  cannot run in this shell because PowerShell command execution fails before
  repo code loads with a .NET `System.IO.FileLoadException`. `pwsh -v` reports
  PowerShell 7.6.2, but even `pwsh -NoProfile -NonInteractive -Command
  'Write-Output ok'` fails the same way. This is a local PowerShell runtime
  gap, not evidence of a HarnessForge script failure.

## Touched Surfaces

- `current-state.md`
- `feature_list.json`
- `docs/roadmap.md`
- `docs/harness/evidence/evidence-log.md`
- `docs/harness/research/README.md`
- `docs/harness/research/harness-token-economics-research.md`
- `docs/harness/research/research-inbox.md`
- `docs/harness/research/research-sources.json`
- `docs/harness/research/research-sources.lock.json`
- `docs/harness/research/sources.md`
- `docs/harness/research/token-economics-metric.schema.json`
- `scripts/refresh_research.py`
- `src/harnessforge/templates/research-sources.json.tmpl`
- `tests/test_refresh_research.py`

## Blockers

- No product blockers.
- Local PowerShell command execution is blocked by a host .NET assembly-load
  error before repo code runs; use direct Python/POSIX verification until the
  local `pwsh` runtime is repaired or run `init.ps1` on a healthy Windows or
  PowerShell host.

## Next Step

Continue the Harness Token Economics Research item by running controlled
minimal, moderate, and comprehensive harness task traces using
`harnessforge.tokenEconomicsMetric.v1`. Start with a tiny Codex
`exec --json` parser or one captured JSONL run that emits a single normalized
record, then repeat one low-risk task across the three profiles in isolated
roots. Release prep should remain last and should start only after accepted
non-release work is closed or explicitly deferred by the maintainer.
