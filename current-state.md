# Current State

Last Updated: 2026-06-24 UTC

## Current Objective

The accepted non-release backlog is complete when HarnessForge has completed or
explicitly deferred every accepted pre-release item in `docs/roadmap.md`:
token economics research, Kubernetes-scale discovery ranking, generated
guidance quality, feature-state gates, instruction lifecycle/SNR review,
generated harness fallback hardening, deeper `enhance` planning, selected
index/SBOM adapters, policy preset evidence, more real-repo fixtures, expanded
large-public-repo field runs, deeper instruction-quality scoring, and the core
harness model course correction.
Release prep starts only after that backlog is closed or intentionally deferred
by the maintainer.

## Key Decisions

Decisions that shape the implementation so a later session does not undo them.

- Course-mining additions stay doc/template-only with no new dependencies; the
  audit map-length cap stays at 300 lines rather than tightening to 220,
  because rendered instruction files run longer than templates and a tighter
  cap risks false audit failures on valid target repos.

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

- 2026-06-24: Harness-engineering foundations pass. Read the full Walking Labs
  `learn-harness-engineering/docs/en` course (12 lectures, 6 projects,
  references, templates, openai-advanced pack, SOPs) and recorded
  `docs/harness/research/harness-engineering-foundations.md`: source lineage,
  the two five-subsystem framings (academic instructions/tools/environment/
  state/feedback vs the operational instructions/state/verification/scope/
  lifecycle product contract), the seven-to-five audit-bucket mapping, the
  maturity ladder, and the structure-is-not-effectiveness boundary.
  `harnessforge audit` now reports the mapping in JSON (`coreModel`, per-domain
  `coreSubsystem`/`surfaceClass`) and formatted output (`feedback [verification
  core]`, `tools [support surface]`), owned by `DOMAIN_CORE_SUBSYSTEM` in
  `audit.py`. This advances the roadmap Core Harness Model Course Correction
  item by resolving the seven-vs-five question (report both with clear labels);
  remaining work there is report/release-check/maturity wording alignment and a
  generated-contract regression check.
- 2026-06-24: Deep Walking Labs course-mining pass added reviewed harness
  primitives to generated templates and the matching own-harness docs
  (evaluator independence, run-baseline-first startup, front-loaded
  non-negotiables, a Key Decisions slot, clean-context review, simplification
  ablation, golden-journey/runtime-observability/architecture-hot-spot prompts,
  and a Date+Revisit-Trigger debt column). `feature_state` now reports an
  advisory `verifiedCompletionRate`. Generated lean-footprint byte tripwires
  were raised once (140k->144k total, 70k->73k markdown) with line guards
  unchanged.
- 2026-06-24: Re-verified all pins against live PyPI/GitHub. `setuptools==82.0.1`
  and Action default Python `3.13.14` already latest; bumped `actions/checkout`
  v6->v7.0.0 and `actions/setup-python` v6->v6.3.0 (full-SHA pinned) across
  `action.yml`, workflows, templates, manifest snippets, and docs.
- 2026-06-24: Docs accuracy pass corrected stale generated-footprint and
  test-count figures (`docs/roadmap.md`, `quality-document.md`) and refreshed
  pin-verification dates; full suite (316 tests), self-audit `100/100`, pin
  check, and `git diff --check` pass.
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
- The first token-economics normalizer slice is implemented. The
  `harnessforge.tokenEconomicsMetric.v1` schema now has a nullable
  `reasoningOutput` token bucket, `harnessforge.evidence.token_economics`
  parses reviewed Codex JSONL events into schema-shaped records, and
  `scripts/normalize_token_trace.py --source codex-jsonl` writes normalized
  records from an input trace plus metadata sidecar without running agents.
  Metadata sidecars can now provide
  `trajectoryOverrides.durationSeconds` for externally measured wall-clock
  duration when native Codex JSONL events lack timestamps.
- The first live Codex JSONL smoke trace is normalized at
  `docs/harness/evidence/token-economics/codex-jsonl-smoke-2026-06-16.json`.
  It reports one read-only orientation turn over `AGENTS.md` and the
  token-economics research note: input `40,348`, cached input `19,200`, output
  `1,034`, reasoning output `815`, two command tool calls, and two file reads.
  The record is explicitly `inconclusive`; it proves the capture path only and
  does not compare harness profiles.
- A two-repeat minimal/moderate/comprehensive Codex profile comparison was
  attempted in ignored scratch space and rejected. Even with
  `codex exec --ignore-user-config`, some raw traces loaded a user-level
  orientation skill outside the target and raw `pwd` output contained local
  working-directory paths. No profile-comparison metric records were promoted.
- A clean isolated Codex profile comparison is now recorded. The runner used
  scratch `HOME` and `CODEX_HOME`, symlinked auth only, `--ignore-user-config`,
  `--ignore-rules`, disabled hooks/plugins/memories/apps/multi-agent features,
  read-only sandboxing, and ignored scratch target roots. Six normalized
  minimal/moderate/comprehensive orientation records are committed under
  `docs/harness/evidence/token-economics/`. Totals were minimal
  `24,728-25,220`, moderate `27,729-28,905`, and comprehensive
  `27,734-27,883` visible tokens. The result remains `inconclusive` for
  product behavior because the task was a tiny non-held-out read-only
  orientation task, but it proves clean profile tracing and shows stored
  harness size is not the same as loaded context.
- A clean isolated Codex implementation repair comparison is also recorded.
  One tiny Python repair task ran under minimal, moderate, and comprehensive
  profiles with workspace-write sandboxing. All three changed `demo.py` from
  `41` to `42` and passed `python3 -m unittest discover -s tests`. Totals were
  minimal `82,118`, moderate `74,871`, and comprehensive `74,862` visible
  tokens, each with one edit and two verification runs. This is still
  `inconclusive` for product behavior, but it adds the first edit plus
  verification trace evidence.
- A more representative HarnessForge-derived duration override repair batch is
  also recorded. Three repeats each ran under minimal, moderate, and
  comprehensive profiles with per-run scratch `HOME` and `CODEX_HOME`, symlinked
  auth only, `--ignore-user-config`, `--ignore-rules`, disabled
  hooks/plugins/memories/apps/multi-agent features, and workspace-write
  sandboxing. All nine changed only
  `src/harnessforge/evidence/token_economics.py` and passed
  `PYTHONPATH=src:. python3 -m unittest tests.test_token_economics`. Median
  totals were minimal `205,636`, moderate `189,703`, and comprehensive
  `245,872` visible tokens. Median durations were minimal `63.556`, moderate
  `52.698`, and comprehensive `62.161` seconds. The result is mixed and still
  `inconclusive`, but it finally shows a larger loaded-context contrast:
  minimal loaded `665` harness chars, while moderate and comprehensive commonly
  loaded about `98K` harness chars.
- A HarnessForge-derived unrevealed failure repair batch is also recorded.
  Three repeats each ran under minimal, moderate, and comprehensive profiles
  with the same isolated runner. The prompt did not name the seeded defects;
  target verification first exposed two focused source failures. All nine runs
  changed only `src/harnessforge/evidence/token_economics.py` and passed the
  focused token-economics unittest module. Median totals were minimal
  `163,183`, moderate `204,213`, and comprehensive `241,409` visible tokens.
  Median durations were minimal `39.542`, moderate `38.169`, and comprehensive
  `41.097` seconds. This result is still `inconclusive`, but it contrasts with
  the explicit duration-override batch: minimal was cheapest here, while
  moderate was cheapest when the prompt named the desired behavior.
- An external OWASP pytm repair batch is now recorded from ignored scratch
  copies of public commit `e452aaf`. Three repeats each ran under minimal,
  moderate, and comprehensive scratch profiles against the focused
  `python -m pytest -q tests/test_flows_helpers.py` contract. All nine runs
  changed only `pytm/flows.py`, passed the focused pytest module with 4 tests,
  and received human review for source-only scope and behavior-preserving
  repair shape. Median totals were minimal `110,924`, moderate `133,320`, and
  comprehensive `138,835` visible tokens; median durations were minimal
  `37.801`, moderate `39.238`, and comprehensive `44.365` seconds. This is the
  first external-real-repo repair evidence, but it remains `inconclusive`
  because the regression was seeded rather than true held-out.
- An external Bluepeak-AI React/TypeScript repair batch is now recorded from
  ignored scratch copies of public commit `8049dd4`. Three repeats each ran
  under minimal, moderate, and comprehensive scratch profiles against the
  focused `npm test -- --run react/tests/trust-ui.test.tsx` contract. All nine
  runs changed only `react/src/components/TrustBadge.tsx`, passed the focused
  Vitest file with 1 test, and received human review for source-only scope and
  behavior-preserving repair shape. Median totals were minimal `352,355`,
  moderate `306,817`, and comprehensive `313,196` visible tokens; median
  durations were minimal `76.572`, moderate `67.195`, and comprehensive
  `84.365` seconds. The result remains `inconclusive`: moderate was cheapest
  in this React/TypeScript batch, while minimal was cheapest in the external
  pytm batch.
- A Bluepeak trajectory-delta review corrected JavaScript/TypeScript
  verification matching so config-file reads and `node_modules/vitest` searches
  do not count as verification runs. The nine Bluepeak records were
  regenerated; each now records three actual `npm test` executions. The review
  explains the unexpected comprehensive result: extra startup docs did not
  shorten this focused UI repair, and comprehensive repeat 3 spent the most
  work on Vite/Vitest environment inspection.
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
- Current token-economics normalizer verification: `tests.test_token_economics`
  passed red/green with 2 tests; targeted parser and local-entrypoint tests
  passed with 8 tests; `scripts/normalize_token_trace.py --source codex-jsonl`
  smoke passed; full unit discovery passed with 309 tests; compileall,
  research source check, JSON validation, durable local-path scan, diff
  hygiene, and self-audit `100/100` passed. No live agent trace was run in
  this slice.
- Current Codex JSONL smoke verification: `codex exec --json --ephemeral
  --sandbox read-only` produced one ignored raw trace under `.harnessforge/`;
  `scripts/normalize_token_trace.py --source codex-jsonl` emitted
  `docs/harness/evidence/token-economics/codex-jsonl-smoke-2026-06-16.json`;
  targeted parser and local-entrypoint tests passed with 9 tests; full unit
  discovery passed with 310 tests; compileall, research source check, JSON
  validation, durable local-path scan, diff hygiene, and self-audit `100/100`
  passed. The trace was read-only and no project tests or edits ran inside the
  traced Codex session.
- Current rejected profile-comparison verification: two-repeat
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --sandbox read-only` runs completed in ignored scratch
  roots, but raw-trace review found non-target user-level skill loading in some
  runs. The attempted comparison was recorded as rejected evidence and no
  normalized profile records were committed.
- Current isolated profile-comparison verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox read-only`
  runs completed for two repeats. Raw-trace review found no user-level
  skill/plugin leakage. Six normalized profile records parse as JSON and passed
  local-path scans. Focused parser/local-entrypoint tests passed with 9 tests;
  full unit discovery passed with 310 tests; compileall, research source
  check, diff hygiene, and self-audit `100/100` passed. The raw JSONL remains
  ignored under `.harnessforge/`.
- Current isolated implementation-comparison verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox
  workspace-write` runs completed once each. Raw-trace review found no
  user-level skill/plugin leakage. Scratch target verification passed for all
  three profiles with `python3 -m unittest discover -s tests`; normalized
  implementation records parse as JSON and passed local-path scans. Focused
  parser/local-entrypoint tests passed with 9 tests; full unit discovery
  passed with 310 tests; compileall, research source check, diff hygiene, and
  self-audit `100/100` passed.
- Current representative duration-override verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox
  workspace-write` runs completed three repeats each. Raw-trace review found no
  non-target user-level skill/plugin loading. Scratch target verification
  passed in all nine targets with the focused token-economics unittest command;
  raw file-change events touched only
  `src/harnessforge/evidence/token_economics.py`. Nine normalized records parse
  as JSON and passed local-path scans. Focused parser/local-entrypoint tests
  passed with 10 tests; full unit discovery passed with 311 tests; compileall,
  research source check, JSON validation, diff hygiene, and self-audit
  `100/100` passed.
- Current unrevealed-failure verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox
  workspace-write` runs completed three repeats each. Raw-trace review found no
  non-target user-level skill/plugin loading or secret-shaped strings. Scratch
  target verification passed in all nine targets with the focused
  token-economics unittest command; raw file-change events touched only
  `src/harnessforge/evidence/token_economics.py`. Nine normalized records parse
  as JSON and passed local-path scans. Focused parser/local-entrypoint tests
  passed with 10 tests; full unit discovery passed with 311 tests; compileall,
  research source check, JSON validation, diff hygiene, and self-audit
  `100/100` passed.
- Current external pytm repair verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox
  workspace-write` runs completed three repeats each against ignored OWASP pytm
  scratch copies. Raw-trace review found no non-target user-level
  skill/plugin loading or secret-shaped strings; raw file-change events touched
  only `pytm/flows.py`. Scratch target post-checks passed in all nine targets
  with `python -m pytest -q tests/test_flows_helpers.py`; nine normalized
  records were generated under `docs/harness/evidence/token-economics/`.
  Focused token-economics/local-entrypoint tests passed with 10 tests; full
  unit discovery passed with 311 tests; compileall, research source check,
  JSON validation, durable local-path scan, diff hygiene, and self-audit
  `100/100` passed after the external batch.
- Current external Bluepeak repair verification: isolated
  minimal/moderate/comprehensive `codex exec --json --ephemeral
  --ignore-user-config --ignore-rules --disable hooks --disable plugins
  --disable memories --disable apps --disable multi_agent --sandbox
  workspace-write` runs completed three repeats each against ignored
  Bluepeak-AI frontend scratch copies. Raw-trace review found no non-target
  user-level skill/plugin loading or secret-shaped strings; raw file-change
  events touched only `react/src/components/TrustBadge.tsx`. Scratch target
  post-checks passed in all nine targets with
  `npm test -- --run react/tests/trust-ui.test.tsx`; nine normalized records
  were generated under `docs/harness/evidence/token-economics/`.
  Follow-up trajectory review regenerated those records with corrected
  JavaScript/TypeScript verification matching; all nine now show three actual
  `npm test` executions. Full unit discovery passed with 311 tests; compileall,
  research source check, JSON validation, durable local-path scan, diff
  hygiene, and self-audit `100/100` passed for this correction slice.
- Current known local verification gap: `pwsh -NoProfile -File ./init.ps1`
  cannot run in this shell because PowerShell command execution fails before
  repo code loads with a .NET `System.IO.FileLoadException`. `pwsh -v` reports
  PowerShell 7.6.2, but even `pwsh -NoProfile -NonInteractive -Command
  'Write-Output ok'` fails the same way. This is a local PowerShell runtime
  gap, not evidence of a HarnessForge script failure.

## Touched Surfaces

- `src/harnessforge/assessment/audit.py`
- `tests/test_generate_audit.py`
- `docs/harness/research/harness-engineering-foundations.md`
- `docs/harness/research/README.md`
- `docs/harness/research/sources.md`
- `docs/harness/README.md`
- `docs/roadmap.md`
- `current-state.md`
- `docs/harness/evidence/evidence-log.md`

## Blockers

- No product blockers.
- Local PowerShell command execution is blocked by a host .NET assembly-load
  error before repo code runs; use direct Python/POSIX verification until the
  local `pwsh` runtime is repaired or run `init.ps1` on a healthy Windows or
  PowerShell host.

## Next Step

Continue the Harness Token Economics Research item by running controlled
minimal, moderate, and comprehensive harness task traces using
`harnessforge.tokenEconomicsMetric.v1`. The next useful slice is true held-out
repair evidence or a larger public checkout that exercises broader discovery
and routing, with human quality review. Keep the
isolated Codex runner so non-target skills/plugins/hooks/memory do not enter
the traces. Add Claude Code OpenTelemetry only when native Codex JSONL is
insufficient for cache-creation or tool-span buckets. Release prep should
remain last and should start only after accepted non-release work is closed or
explicitly deferred by the maintainer.
