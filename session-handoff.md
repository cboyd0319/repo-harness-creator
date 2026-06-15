# Session Handoff

Last Updated: 2026-06-15 UTC

## Current Objective

Build HarnessForge into a robust, explicit, opt-in harness platform while
preserving the boundary between portable base generation, repo-local policy,
and advanced product modes.

## Files

- `src/harnessforge/`
- `tests/`
- `docs/harness/`
- `action.yml`
- `docs/action.md`
- `docs/installation.md`
- `docs/usage.md`
- `docs/capabilities.md`
- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `.github/pull_request_template.md`
- `init.sh`
- `init.ps1`
- `tests/test_local_entrypoints.py`
- `scripts/refresh_research.py`
- `feature_list.json`
- `.github/workflows/ci.yml`
- `.github/workflows/harness-self-heal.yml`
- `scripts/check_pins.py`
- `pins.toml`
- `src/harnessforge/audit.py`
- `src/harnessforge/blueprints.py`
- `src/harnessforge/cli.py`
- `src/harnessforge/detect.py`
- `src/harnessforge/generate.py`
- `src/harnessforge/github_action.py`
- `src/harnessforge/models.py`
- `src/harnessforge/planner.py`
- `src/harnessforge/readiness.py`
- `src/harnessforge/report.py`
- `src/harnessforge/reports.py`
- `src/harnessforge/session.py`
- `src/harnessforge/sync.py`
- `src/harnessforge/verify_evidence.py`
- `src/harnessforge/spec_system.py`
- `src/harnessforge/update.py`
- `src/harnessforge/templates/claude.md.tmpl`
- `src/harnessforge/templates/gemini.md.tmpl`
- `src/harnessforge/templates/copilot-instructions.md.tmpl`
- `src/harnessforge/templates/change-contract.md.tmpl`
- `src/harnessforge/templates/component-inventory.md.tmpl`
- `src/harnessforge/templates/verification-matrix.md.tmpl`
- `src/harnessforge/templates/evidence-log.md.tmpl`
- `src/harnessforge/templates/first-agent-task.md.tmpl`
- `src/harnessforge/templates/release-controls.md.tmpl`
- `src/harnessforge/templates/research-sources.json.tmpl`
- `src/harnessforge/templates/sensor-registry.md.tmpl`
- `src/harnessforge/templates/source-record.schema.json.tmpl`
- `src/harnessforge/templates/source-record-example.json.tmpl`
- `src/harnessforge/templates/sources.md.tmpl`
- `tests/test_cli.py`
- `tests/test_detect.py`
- `tests/test_generate_audit.py`
- `tests/test_refresh_research.py`
- `tests/test_verify_contract.py`
- `tests/test_pins.py`
- `docs/harness/effectiveness-eval-contract.md`
- `docs/harness/effectiveness-evidence.schema.json`
- `docs/harness/effectiveness-evidence-example.json`
- `docs/harness/change-contract.md`
- `docs/harness/evaluator-rubric.md`
- `docs/harness/evidence-log.md`
- `docs/harness/first-agent-task.md`
- `docs/harness/manifest.json`
- `docs/harness/sources.md`
- `docs/harness/sensor-registry.md`
- `docs/harness/source-record.schema.json`
- `docs/harness/source-record-example.json`
- `docs/harness/verification-matrix.md`
- `docs/harness/reference-mining-notes.md`
- `docs/harness/remaining-ideas-research.md`
- `docs/harness/component-inventory.md`
- `.gitignore`

## Blockers

- No known blockers.
- Latest docs consistency pass reconciled the root README, harness README, and
  composite Action metadata with the current `sync`, `verify`, and Action
  behavior.
- Root README split is complete: the README is now a short landing page,
  with detailed install, usage, and capability/reference content moved to
  `docs/installation.md`, `docs/usage.md`, and `docs/capabilities.md`.
- Generated first-agent harness improvement instruction is implemented:
  generated harnesses now include `docs/harness/first-agent-task.md` and the
  canonical generated instruction file routes first agent sessions to it.
- Current remaining-ideas research pass completed without AGY. The ranked
  backlog lives in `docs/harness/remaining-ideas-research.md`. Implemented the
  first P0 item: read-only `inspect --readiness --json`, including static
  verdicts, blockers, warnings, next actions, source-of-truth signals,
  runnable checks, generated drift, and governance review surfaces.
  Implemented the second P0 item: source-of-truth spec sync detection across
  `.specify`, active feature metadata, `specs/`, `aspec/`, work-item
  templates, and repo workflow definitions. Implemented the third P0 item:
  read-only `sync --check`, which wraps readiness, generated drift,
  source-of-truth spec routing, and review-required surfaces with exit codes
  `0` ready, `1` warning, and `2` blocked. Implemented the final P0 item:
  `verify --json` default plan-mode CLI plus contract docs, schema, example,
  and fixture tests. Implemented the first P1 item: read-only workflow and work-item
  inventory in readiness. Implemented the second P1 item: context-budget and
  duplicate-instruction detection in readiness. Implemented the third P1 item:
  permission/governance inventory in readiness. Implemented the final P1 item:
  guided first-run UX with `harnessforge quickstart`. Added `verify --json`
  plan mode, config-precedence reporting, selective generated-owned update
  refresh, Java pin parsing, intentionally vulnerable training-path pin-scan
  exclusions, nested JVM wrapper preference, container runtime inventory, and
  source-verified platform metadata. The first robust opt-in product mode is
  now implemented: `harnessforge blueprint list/show/apply`, with built-in
  packs for agentic apps, spec-driven projects, web services, data/ML,
  security-sensitive repos, and workflow automation. Blueprint output is
  separate from normal `init`, writes under `docs/harness/blueprints/`, records
  ownership metadata, preserves project edits by default, and requires
  `--force` for replacement. The second robust opt-in slice is explicit
  verification execution: default `harnessforge verify` remains plan-only, and
  `harnessforge verify --run` executes checks only when requested, with
  per-command timeout, no-shell argument-list execution, run-mode JSON timing
  metadata, capped stdout/stderr previews, timeout reporting, and exit-code
  mapping. The composite Action now exposes the same boundary through
  `command: verify`, read-only plan mode by default, explicit `verify-run:
  "true"`, newline-separated `verify-command`, `verify-timeout-seconds`, a
  target-contained verify JSON report, and `verify-verdict` output.
  Rejected defaults remain large
  skill/memory trees, platform permission config, LLM-assisted init,
  autonomous push/PR workflows, and copied ASPEC/AWMAN/Maki templates.
- Current HarnessForge-adjacent research and UX batch mined local `awman`,
  `aspec`, and `maki`, plus public HarnessForge-like and harness-engineering
  sources. Accepted generic improvements: structured project spec detection,
  Just task-runner detection, architecture-lint routing without duplicate
  commands, generated-doc drift context, read-only `harnessforge inspect` with
  JSON output, and root Python-package priority over docs-site classification.
  The boundary remains explicit: HarnessForge detects and surfaces useful
  repo-local control planes, but it does not generate sibling-repo
  instructions, personal tool mandates, large skill trees, MCP
  setup, or extra agent adapters by default. That batch passed full unit
  discovery and POSIX/PowerShell entrypoints with 189 tests, compile, pin
  check, research source check, verify plan/run JSON smokes, blueprint
  JSON/apply smokes, self-audit `100/100`, local path scan, and diff hygiene.
  Readiness and sync check are warning-only
  because existing local instruction files and the two repo-local GitHub
  workflow definitions need review; there are no readiness blockers.
- Current SDD research supplement reviewed the GitHub Spec Kit article, the
  supplied local Spec Kit checkout, Fowler's SDD tools article, and
  specdriven.ai. Accepted generic ideas: detect `.specify/`, active feature
  metadata, spec lifecycle conventions, global context versus feature-scoped
  artifacts, unresolved clarification markers, incomplete requirement
  checklists, missing plan/task artifacts, and weak spec-to-task traceability.
  Keep the boundary: HarnessForge should detect and route existing SDD systems,
  not install Spec Kit, `.specify`, agent slash commands, presets, extensions,
  catalogs, or workflow engines by default.
- Current source-of-truth implementation adds a shared static spec analysis
  module, richer detect markers, generated context routing for existing SDD
  systems, readiness quality warnings, and an audit check that instruction
  files route agents to detected source-of-truth specs. It also keeps ASPEC
  and AWMAN-derived ideas in scope through `aspec/`, work-item template, and
  repo workflow definition detection without copying their formats.
- Current sync preflight implementation is a CLI and composite Action read
  path. It does not add mutation semantics, run target checks, or change
  generator output.
- Current unified report implementation is a CLI and composite Action read
  path. It composes readiness, audit, generated drift, index, verify evidence,
  effectiveness evidence, first-agent task status, and platform contract into
  JSON or Markdown without running target commands.
- Current enhance-existing review-plan implementation adds
  `init --enhance-existing --dry-run --json`. It parses existing instruction
  sections, reports canonical section coverage, counts missing sections and
  proposed edits, and emits review-required proposals for missing sections,
  platform-router routes, local paths, local tool mandates, verification
  conflicts, duplicate guidance, bloated instruction files, and unreadable
  files. Proposed edits include sanitized placeholder patch previews and
  patch-preview counts. HarnessForge does not write project-owned cleanup edits
  automatically. The dedicated read-only `harnessforge enhance` command now
  exposes that review plan directly, with text and JSON output, no command
  execution, and no writes.
- Current sensor registry implementation adds a review-required generated
  `docs/harness/sensor-registry.md`, manifest required-file and snippet
  coverage, generated ownership metadata, and live harness ownership/source/
  purpose/retirement records for recurring checks. It does not execute target
  commands or claim real-agent effectiveness.
- The main README has been reorganized to make the project easier to understand
  from the outside: value proposition first, then at-a-glance outcomes,
  differentiators, boundaries, quickstart, readiness/sync, generated files,
  audit/update, Action use, security, and verification.
- Current `verify --json` defaults to read-only plan mode and has explicit
  run mode behind `--run`. It includes
  `docs/harness/verify-json-contract.md`, `verify-json.schema.json`, and
  `verify-json-example.json`, and reports detected or explicit project checks
  with stable planned, passed, failed, blocked, or timed-out statuses.
- Current workflow/work-item inventory work is read-only and advisory. It adds
  `src/harnessforge/workflow_inventory.py`, readiness JSON fields
  `workflowInventory` and `workItemInventory`, and review-required warnings for
  setup, teardown, remediation, push, pull-request, CI-polling, and credential
  surfaces. It detects existing repo surfaces; it does not generate ASPEC,
  AWMAN, workflow engines, or automation defaults.
- Current context-budget work is read-only and advisory. It adds
  `src/harnessforge/context_budget.py` and readiness JSON field
  `contextBudget`, reporting instruction file size and duplicate instruction
  blocks across AGENTS, Claude, Gemini, and Copilot instruction routers.
- Current governance inventory work is read-only and advisory. It adds
  `src/harnessforge/governance_inventory.py` and readiness JSON field
  `governanceInventory`, reporting MCP configs, agent settings, hooks,
  devcontainers, sandbox configs, agent setup workflows, and env
  files/templates without reading or exposing secret values.
- Current guided first-run UX is read-only. `harnessforge quickstart` composes
  detection, readiness, dry-run generation planning, preserved-file reporting,
  generated review placeholders, review-required surfaces, and next commands
  without writing target files.
- Current local Harness Forge and Meta-Harness paper review was done without
  AGY against the local Harness Forge sibling repo and the user-supplied paper
  PDF. Accepted ideas are eval discipline rather than generated files:
  candidate-sensitive quality metrics, full-history queryable logs,
  frozen-replay avoidance, held-out validation, anti-leakage, do-no-harm
  quality floors, worst-case quality tracking, validation-before-expensive-eval,
  and explicit skill/plugin/installer governance inventory. The review also
  extended `governanceInventory` to detect agent skills, agent plugin
  manifests, and root installer scripts.
- Current expanded reference-repo quality batch ran shadow generation and
  content review against agent-governance-toolkit, apple-container,
  Bluepeak-AI, JobSentinel, nhl-betting-analytics, persona, RunHaven,
  rustguard, and WormsWMD-macOS-Fix. Accepted fixes: docs-heavy
  multi-component repos now detect as monorepos, Swift Package Manager repos
  detect as `swift`, shell projects can use repo-local validation scripts,
  Makefile commands are inferred only from declared targets, nested uv Python
  projects can route pytest to a single repo-level `scripts/tests` tree, and
  generated/enhanced context now calls out Swift, Python, shell, Terraform,
  container image, and Tauri surfaces. Current shadow outcomes: AGT is
  `monorepo`; apple-container is `swift` with `make check` and `make test`;
  Bluepeak is `monorepo` with backend pytest and frontend checks; JobSentinel
  retains npm plus Tauri Cargo checks; NHL includes Cargo, harness-doc, and uv
  pytest checks; Worms is `shell` with its harness and dependency-parsing
  checks. Remaining low shadow scores are project-owned stale manifests,
  PowerShell entrypoint drift, existing absolute scratch paths, or existing
  snippet drift that HarnessForge reports rather than silently rewriting.
  Current verification passes full unit discovery with 130 tests, compile, pin
  check, JSON validation, self-audit `100/100`, and diff hygiene.
- Current reference-repo quality batch completed the VexShield and Bazel
  generated-content exercises with manual ideal harness sketches and temporary
  shadow generation. Accepted fixes: stronger root-first and priority-based
  discovery for huge repos, C/C++ and Starlark detection, Rust-first handling
  for root Cargo workspaces that also have Bazel markers, Rust fmt/clippy/test
  command inference, Bazel checks retained as secondary checks, nested
  component command inference, fixture/vendor/docs command skips, hidden
  Claude/Gemini instruction detection, tool-only root Python config no longer
  producing `python -m compileall .`, explicit failing placeholders when no
  verification command is detected, generated project-context guidance, and
  `--enhance-existing` support for reviewed addenda that preserve existing
  instruction text. The Bazel shadow run now detects stack `bazel`, adds
  Bazel-specific boundary context to enhanced `AGENTS.md`, and audits at
  `93/100` because existing project-owned instructions still contain hardcoded
  scratch-path examples; HarnessForge reports that quality issue instead of
  silently rewriting it. Current verification passes full unit discovery with
  123 tests, compile, pin check, JSON validation, self-audit `100/100`, and
  diff hygiene.
- Current pins-ledger batch added `pins.toml` and ledger-backed checks to the
  live and generated pin checkers. When `pins.toml` exists, checks now tie
  Python pins, `package.json` direct package versions, package-lock integrity,
  Containerfile base image tags and digests, and profile image tags back to the
  ledger. Current verification passes focused tests with 36 tests, full unit
  discovery with 87 tests, compile, `pins.toml` parse, pin check, diff hygiene,
  self-audit `100/100`, POSIX entrypoint, and PowerShell entrypoint.
- Current script and boundary batch keeps three HarnessForge surfaces separate:
  this repo's live harness, generated target-repo harness artifacts, and the
  published GitHub Action. The product audit now honors a target repo's declared
  runtime/runner boundary, so macOS-only targets are not forced to restore
  PowerShell or document unrelated OS floors. Root entrypoints compile
  `scripts/` as product code, PowerShell entrypoints prefer `python3` before
  `python`, Python requirement extras stay tied to the base `pins.toml` package
  entry, non-version strings such as `==latest` are rejected, and the Action
  docs/tests now state that Action runs are input-driven and target-contained.
  Current verification passes focused tests with 50 tests, full unit discovery
  with 92 tests, compile, syntax checks, metadata parse, pin check, diff
  hygiene, self-audit `100/100`, RunHaven audit `100/100`, POSIX entrypoint,
  and PowerShell entrypoint.
- Current cleanup batch refreshed stale bootstrap entries in
  `docs/harness/quality-document.md` and renamed the internal GitHub Action
  output delimiter prefix from the old project wording to `harnessforge`.
  Focused verification passed Action tests, targeted compile, pin check,
  self-audit `100/100`, stale-string scan, and diff hygiene.
- Current release-prep batch passed local POSIX and PowerShell release gates
  with 92 tests, pin check, and self-audit `100/100` on macOS 26.5.1 with
  Python 3.14.5. An isolated wheel smoke built and installed
  `harnessforge-0.1.0-py3-none-any.whl` in a fresh venv outside the repo,
  confirmed `harnessforge --version`, generated a target harness, audited it at
  `100/100`, and recorded SHA-256
  `34134b559fafe823c5f9b9b5f041eaf387b226ca9300b8b1abdfdc1f997e657e`.
  Remote manual macOS/Windows CI, SBOM/provenance decision, and release tag
  remain gated.
- Current generated/local boundary batch keeps generated `GEMINI.md` support
  for Gemini and Antigravity loading, but adds regression coverage that
  generated instruction entrypoints do not impose repo-local AGY/Antigravity
  research mandates. Live and generated boundary maps now state that generated
  harnesses must not inherit HarnessForge's local agent/tooling mandates.
  Focused generator/refresh tests passed with 44 tests, full unit discovery
  passed with 93 tests, pin check passed, diff hygiene passed, and self-audit
  stayed `100/100`.
- Current deep generated-surface boundary batch separates live HarnessForge
  self-heal/research workflow behavior, generated optional workflow scaffolds,
  and published composite Action behavior. Generated self-heal scaffolds are
  documented and tested as manual by default, without scheduled research
  refresh inheritance; they stage generated router files and preserve custom
  `--agent-file` values. The published Action docs now state that the Action is
  input-driven and does not schedule jobs, refresh research, create branches,
  commit, push, or open pull requests by itself. Audit now follows the
  manifest-declared canonical instruction file, so custom-agent generated
  harnesses audit at `100/100`. Focused tests passed with 70 tests, full unit
  discovery passed with 97 tests, compile passed, pin check passed,
  JSON/template parsing passed, generated default/custom target audits passed
  at `100/100`, diff hygiene passed, and self-audit stayed `100/100`.
- Current generator release-prep batch adds generated-file ownership metadata,
  drift reporting, and platform-contract options. Generated manifests now
  record generator identity, platform contract, generated-file ownership,
  template SHA-256, and content SHA-256 metadata. `harnessforge update
  --drift-report` reports generated-file drift without writing updates. CLI
  init/update and the composite Action accept `--platform-contract` for
  cross-platform, macOS-only, Windows-only, or Linux-only target contracts.
  Platform-specific generation omits unsupported local entrypoints, and
  optional self-heal scaffolds verify through the generated entrypoint for the
  selected contract. Optional workflow scaffold warnings are louder, Python
  detection adds Ruff and mypy commands from config, and generated placeholders
  that require project decisions are marked `REVIEW REQUIRED`. Current
  verification passes full unit discovery with 103 tests, compile, pin check,
  JSON parsing, self-audit `100/100`, diff hygiene, and rendered target smokes.
- Current reference-repo compatibility batch audited 25 sibling repositories
  under the local GitHub checkout parent with direct read-only detection/audit/dry-run
  checks, temporary generated-harness smoke tests, and a read-only AGY
  supplement. Accepted fixes: explicit platform-contract audit precedence with
  old-manifest fallback, docs-only and monorepo environment profiles, root
  Maven/Gemfile manifest priority, docs-site `validate.sh` detection,
  Poetry/Pipenv Python command prefixes, nested package-manager labels,
  skipped-file ownership/hash metadata that avoids immediate drift, clearer
  preserved-file onboarding warnings, Rust `build.rs` allowance when Cargo is
  present, and Docker multi-stage alias handling. Default init still preserves
  existing instruction files; the side-by-side path is now surfaced as
  `--agent-file HARNESSFORGE_AGENTS.md`. Current verification passes full unit
  discovery with 116 tests, compile, pin check, JSON parsing, self-audit
  `100/100`, diff hygiene, and rendered compatibility smokes.
- Current OpenAI Codex AI-native engineering guide review imported
  Delegate/Review/Own SDLC boundaries, agent-generated test integrity guidance,
  high-signal review criteria, and the official source URL into the fixed
  allowlist. Current Codex SDLC controls batch passes focused tests with 42
  tests, full unit discovery with 85 tests, compile, pin check, JSON
  validation, research refresh with 107 sources and one known Red Hat 403,
  diff hygiene, local-path scan, POSIX entrypoint, PowerShell entrypoint, and
  self-audit `100/100`.
- Current best-practices, memory, and MIT sibling HarnessForge review imported
  compact generated routers for Claude, Gemini, and Copilot; local agent
  override ignore patterns; command-trust wording; and personal-state treatment
  for platform auto-memory. Dependency-heavy blueprints, MCP/settings
  scaffolding, global config writes, hooks, and auto-permission config remain
  deferred.
- Current platform-router batch passes focused generator/CLI tests with 31
  tests, full unit discovery with 85 tests, compile, pin check, JSON
  validation, diff hygiene, local-path scan, POSIX entrypoint, PowerShell
  entrypoint, and self-audit `100/100`.
- Current generated-harness alignment batch passes focused CLI/Action/generator
  tests with 45 tests, full unit discovery with 81 tests, compile, pin check,
  diff hygiene, and self-audit `100/100`.
- Generated harnesses now include an advisory `scripts/check_pins.py`, a
  `release-controls.md` artifact, and best-effort local self-audit from
  generated POSIX/PowerShell entrypoints when `harnessforge` is available.
- Optional workflow scaffolds are explicit flags:
  `--with-ci-workflow` and `--with-self-heal-workflow`. They generate manual
  workflows and are also available through the composite Action inputs.
- Audit scoring now prevents domains with any failed check from rounding to
  `5/5`.
- Walking Labs review imported generated-harness quality gates, manifest drift
  coverage, initializer baseline-commit reminders, structural-score caveats,
  release evidence, and rollback controls. Architecture scanners, memory index
  checks, memory topic cleanup, and agent-specific permission config validation
  remain deferred project-specific opt-ins.
- Local sibling harness comparison imported root-agnostic init execution,
  PowerShell native fail-fast handling, optional `--no-env`/`-NoEnv`
  credential-free verification, broader advisory pin signals for containers,
  Python requirements, package manifests, and npm lockfiles, entropy
  promotion/evidence/stop rules, completion bars, isolated release-artifact
  smoke-test guidance, and root scratch-report ignore patterns. App telemetry
  headers, model routing rules, public wiki mapping, file-size budgets,
  pre-commit lockfile hooks, and credential-backup test wrappers remain
  deferred project-specific opt-ins.
- Current local-harness comparison batch passes 84 tests, compile, strict live
  pin check, JSON validation, diff hygiene, self-audit `100/100`, POSIX
  `--no-env` verification, PowerShell `-NoEnv` verification, and scratch-report
  ignore checks.
- The project is now named HarnessForge in tracked repo surfaces. Runtime code
  lives under `src/harnessforge/`, the primary CLI is `harnessforge`, generated
  Action examples use `cboyd0319/harnessforge`, and live workflows call
  `python -m harnessforge`. Current rename verification passes 84 tests, POSIX
  and PowerShell entrypoints, compile, pin check, metadata validation,
  stale-name and local-path scans, editable install smoke, diff hygiene, and
  self-audit `100/100`.
- Current OWASP/security and CI-cost-control batch passes focused tests, full
  unit discovery with 76 tests, compile, pin check, JSON validation, diff
  hygiene, self-audit `100/100`, and both POSIX and PowerShell entrypoints.
- The fixed research allowlist now tracks 106 sources with the same known Red
  Hat 403 failure. Current refresh produced no adversarial metadata signals.
- Research refresh now also withholds invisible Unicode and Markdown/HTML
  exfiltration markers from durable fetched metadata.
- Harness docs/templates now preserve intentionally vulnerable training, demo,
  or fixture code unless remediation is explicitly in scope.
- Material AI/RAG/agent, tool, external-service, auth, secret, data-flow, or
  deployment changes now require boundary/threat-model evidence and focused
  abuse-case checks.
- Push/PR CI now runs the Ubuntu 22.04 Python 3.13.14 path by default with
  superseded-run cancellation. macOS and Windows remote platform checks are
  manual `workflow_dispatch` jobs for release or risk-based confirmation.
- Current agentic-security source and metadata hardening slice passes focused
  refresh/audit tests, full unit discovery with 73 tests, compile, pin check,
  JSON validation, diff hygiene, self-audit `100/100`, and both POSIX and
  PowerShell entrypoints. The source ledger now tracks 88 fixed allowlist
  sources with the same known Red Hat 403 failure.
- Research refresh now withholds fetched title/heading metadata that resembles
  prompt injection, indirect prompt injection, credential exfiltration, or
  sensitive-file access, and records signal IDs instead of durable raw text.
- Audit now requires the harness to document prompt-injection and
  data-poisoning boundaries as untrusted-content risks.
- Current self-heal automation and local-path policy slice passes focused tests,
  full unit discovery with 72 tests, compile, pin check, diff hygiene,
  self-audit `100/100`, and both POSIX and PowerShell entrypoints.
- The scheduled research/self-heal workflow now runs at 12:00 UTC. Research
  refresh remains a fixed `research-sources.json` allowlist metadata refresh;
  it does not search for latest research or auto-promote fetched text.
- Audit now fails durable harness docs/state that contain machine-local
  absolute paths unless the caller uses the explicit local override.
- Current full local POSIX and PowerShell verification passes with 60 tests, pin
  check, and self-audit `100/100` after the personal AGT current snapshot
  slice; POSIX also passes when launched with `PYTHONPATH=<non-repo-path>` in prior
  verification.
- Research metadata refresh currently tracks 76 sources with one recorded Red
  Hat 403 fetch failure.
- Root Action manifest regression coverage now checks quoted description values
  containing colons.
- Root, template, and generated `AGENTS.md` files now have the required five
  section headings.
- Current hardening pass added PEP 639 `license-files`, `PYTHONSAFEPATH=1` for
  the composite Action, root-manifest symlink escape protection in detection,
  broader local home-path redaction, target-contained Action report paths, and
  slash-separated Action report outputs.
- Research refresh now rejects non-HTTPS URLs, embedded credentials, localhost,
  and literal non-public IP targets before fetching.
- Hosted CI run `27489182164` exposed a Windows-only report output separator
  regression after commit `18efcb8`. The local fix normalizes Action report
  outputs to forward slashes; verify the latest hosted CI status after push.
- Hosted CI run `27489310186` passed on `main` for Ubuntu 22.04, macOS 15, and
  Windows 2025 across Python 3.13.14 and 3.14.6.
- Current focused checks pass: `PYTHONPATH=src:. python3 -m unittest
  tests.test_pins tests.test_refresh_research`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, and live research refresh with 49 sources
  and one Red Hat 403.
- Isolated generated-harness smoke confirms generated research source files now
  contain 49 sources.
- Root `init.sh` now prepends `src` to an existing `PYTHONPATH`, matching the
  already-correct PowerShell entrypoint behavior.
- Current focused entrypoint check passes: `PYTHONPATH=src:. python3 -m
  unittest tests.test_local_entrypoints`.
- Hosted CI run `27490215814` passed on `main` for commit `fda509a` across
  Ubuntu 22.04, macOS 15, and Windows 2025 on Python 3.13.14 and 3.14.6.
- Current ease/security slice makes bare CLI invocation a usage error,
  normalizes generated `python3` commands through the selected interpreter, and
  resolves relative research-source redirects before validating the target.
- Current focused checks pass: `PYTHONPATH=src:. python3 -m unittest
  tests.test_cli tests.test_generate_audit tests.test_refresh_research`.
- Current unit suite passes with 50 tests.
- Current POSIX and PowerShell entrypoints pass with 50 tests, pin check, and
  self-audit `100/100`.
- Current GitHub Action output hardening writes `$GITHUB_OUTPUT` values with
  delimiter blocks instead of flattening line breaks.
- Current focused Action check passes: `PYTHONPATH=src:. python3 -m unittest
  tests.test_github_action`.
- Current full unit suite and POSIX/PowerShell entrypoints pass with 50 tests,
  pin check, and self-audit `100/100` after delimiter-output hardening.
- CI now uses the explicit `windows-2025-vs2026` label after hosted CI warned
  that `windows-2025` requests are being redirected to that image by June 15,
  2026.
- Research refresh now connects HTTPS fetch sockets to the validated public DNS
  result while preserving the original host for TLS verification, closing the
  DNS-rebinding transport gap after URL and redirect validation.
- Current focused refresh check passes: `PYTHONPATH=src:. python3 -m unittest
  tests.test_refresh_research`.
- Current full local POSIX and PowerShell verification passes with 52 tests,
  pin check, and self-audit `100/100` after research-refresh transport
  hardening.
- Live research refresh checked 49 sources through pinned public-DNS transport;
  the known Red Hat 403 remains recorded.
- Cross-platform path containment now uses shared path-text handling for POSIX
  and Windows absolute/rooted syntax. Action report paths reject rooted inputs,
  Windows-style relative report separators normalize to target-relative paths,
  and audit catches Windows-style absolute Markdown links and backslash
  traversal in manifest-required files.
- Current focused path check passes: `PYTHONPATH=src:. python3 -m unittest
  tests.test_github_action tests.test_generate_audit tests.test_detect`.
- Current full local POSIX and PowerShell verification passes with 54 tests,
  pin check, and self-audit `100/100` after cross-platform path-containment
  hardening.
- Resolved a staging gap in `.github/workflows/harness-self-heal.yml`. The
  self-heal PR step now stages generated root harness files along with
  `docs/harness` and source templates, preventing empty commits or incomplete
  pull requests when safe updates touch root files.
- Current focused self-heal staging check passes: `PYTHONPATH=src:. python3 -m
  unittest tests.test_pins`.
- Current full local POSIX and PowerShell verification passes with 55 tests,
  pin check, and self-audit `100/100` after the final ease/security review
  fixes.
- Re-ran a deeper read-only comparison against `agent-governance-toolkit`.
  Accepted contribution policy, PR template, stronger security scope,
  `.gitignore` hygiene, and Action `min-score` validation. Deferred external
  workflow gates, SBOM/provenance, Scorecard, fuzzing, and CODEOWNERS until the
  release path and maintainer model justify them.
- Personally reviewed the current `microsoft/agent-governance-toolkit`
  `origin/main` snapshot for the requested paths, without Antigravity
  delegation. The local clone was stale, so the review used a temporary archive
  of current `origin/main`. Accepted additional repo-fit items: multiline
  workflow fail-fast enforcement, local Markdown anchor validation with fenced
  code blocks ignored, forbidden `setup.py`/`build.rs` build-hook detection,
  example and security-sensitive contribution rules, and benchmark claim
  limits. Deferred AGT compliance suites, incident-response structure,
  secret-scanning, SBOM, Scorecard, CodeQL, dependency-review, and release
  workflows for the release and maintainer-model decision.
- Current focused AGT-derived checks pass: `PYTHONPATH=src:. python3 -m
  unittest tests.test_generate_audit tests.test_pins` with 22 tests,
  `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`, `git diff
  --check`, and self-audit.
- Current full AGT-derived checks pass: `./init.sh` and `pwsh -NoProfile -File
  ./init.ps1`, each with doctor, compile, 60 tests, pin check, and self-audit
  `100/100`.
- Additional monorepo research covered official package-manager, language,
  build-system, GitHub Actions, and Terraform docs; supplied local
  `bazel-monorepo` and `awesome-monorepo` examples; cloned public Harness IDP
  and vanilla GitHub Actions monorepo examples; and the supplied Medium,
  Atlassian, LinkedIn, and Lukas Masuch articles.
- Detection now separates workspace/layout markers, component manifests, and
  repo routing markers. It covers explicit workspace tools, inferred
  multi-component layouts, GitHub workflow path filters and
  `working-directory`, local Actions, devcontainers, Harness IDP folders,
  existing agent-instruction files, and Terraform roots/modules.
- Current focused monorepo checks pass: `PYTHONPATH=src:. python3 -m unittest
  tests.test_detect tests.test_generate_audit tests.test_refresh_research` with
  46 tests, compile, pin check, JSON validation, and research refresh.
- Current full monorepo checks pass: `./init.sh` and `pwsh -NoProfile -File
  ./init.ps1`, each with doctor, compile, 69 tests, pin check, and self-audit
  `100/100`.
- Research metadata refresh currently tracks 76 sources with one recorded Red
  Hat 403 fetch failure.
- Current dedicated harness-docs and AGENTS mining pass reviewed the local
  paper catalog plus Bluepeak-AI and JobSentinel harness references without
  AGY. Bluepeak-AI and JobSentinel root `AGENTS.md` files were reviewed; the
  paper catalog checkout had no root `AGENTS.md`. Accepted the generic restart
  experience as read-only `harnessforge session`, which summarizes git state,
  readiness, harness audit score, state-file presence, and next actions without
  writing files or running target checks.
- Current diff-aware verification planner slice added read-only
  `harnessforge plan --since <ref>`. It inspects tracked and untracked changed
  files with git, maps them to detected or explicit project verification
  checks, reports matched files, unmatched files, and reasons, and does not
  execute target commands. Current verification passes full unit discovery and
  POSIX/PowerShell entrypoints with 210 tests, compile, pin check, research
  source check, JSON validation, session and plan JSON smokes, changed-file
  local-path scan, diff hygiene, and self-audit `100/100`. Remaining
  high-value, non-default product ideas are benchmark/score commands only when
  backed by representative effectiveness evidence.

## Next Session

The next session should continue the robust-mode buildout, not return straight
to release prep. The latest slices added `verify --json` default plan mode,
config-precedence reporting, selective generated-owned update refresh,
Maven/Gradle dependency pin parsing, intentionally vulnerable training-path
pin-scan exclusions, nested JVM wrapper preference, container runtime
governance inventory, a no-network research source hygiene gate, a
machine-readable effectiveness evidence contract, source-reviewed platform
adapter metadata, explicit blueprint mode, explicit verification run mode, and
the Action verification bridge. `harnessforge blueprint` currently supports
list/show/apply, dry-run, force-only replacement, project-edit preservation,
JSON output, ownership metadata, and six built-in packs. `harnessforge verify
--run` executes planned checks explicitly, records structured JSON evidence,
and keeps normal verify plan mode read-only. The composite Action mirrors that
boundary with `command: verify`, `verify-run`, `verify-command`,
`verify-timeout-seconds`, `json-report`, and `verify-verdict`. Generated target
harness docs now explain how to capture, store, and review explicit verify-run
evidence in `verification-matrix.md`, `evidence-log.md`, and
`release-controls.md`, while keeping runnable check evidence separate from
structural audit score and real-agent effectiveness. Local CLI verify now also
supports `--json-report <target-relative-path>` so users can persist verify
JSON without shell redirection. CLI and Action report writers share
target-contained path validation in `src/harnessforge/reports.py`.
Readiness and sync now include advisory `verifyEvidence` inventory for
target-contained `docs/harness/evidence/verify*.json` reports. It surfaces the
latest report, schema validity, stale reports, failed or blocked verdicts, and
timed-out checks without turning stored evidence into a hard gate by default.
`inspect --readiness --require-verify-evidence` and
`sync --check --require-verify-evidence` now make that inventory an explicit
release gate. Gate mode blocks when stored evidence is missing, invalid, stale,
plan-mode, failed, blocked, timed out, or has error counts. Default readiness
and sync behavior remains advisory.
The composite Action now exposes the same preflight through `command: sync`.
Action sync is read-only, writes only requested target-contained JSON reports,
returns the CLI readiness exit code, and exposes `readiness-verdict` plus
`sync-exit-code` outputs. `require-verify-evidence: "true"` enables the same
stored verify evidence gate in CI. `sync-command` can provide non-executed
readiness command overrides when detection cannot infer a project check.
The optional generated CI workflow scaffold now uses that Action sync preflight
before audit. It remains manual-only, keeps `require-verify-evidence: "false"`
by default, records `docs/harness/evidence/sync-preflight.json`, treats warning
verdicts as advisory, and stops only on blocked readiness using bracket-safe
Action output syntax for `sync-exit-code`. Generated and root docs describe
that boundary, and CLI generation warnings call out the default policy.
The latest harness-docs and AGENTS mining supplement added `harnessforge
session`, a read-only restart snapshot that reports git state, readiness,
harness audit summary, state-file presence, and next actions without writing
files or running target checks. Bluepeak-AI and JobSentinel root `AGENTS.md`
files were reviewed; the supplied paper catalog checkout had no root
`AGENTS.md`.
The latest diff-aware planning slice added `harnessforge plan --since <ref>`,
a read-only changed-file planner. It combines `git diff --name-only` with
untracked files from `git ls-files --others --exclude-standard`, maps changed
files to detected or explicit checks, reports unmatched files, and leaves
execution to `verify --run`.
The latest sensor registry slice added generated
`docs/harness/sensor-registry.md` as a review-required artifact, manifest
required-file and snippet coverage, generated ownership metadata, generated
README/matrix routing, and live owner/source/purpose/retirement records for
recurring checks. It does not execute target commands or prove real-agent
effectiveness.
The latest source-record schema slice added generated
`docs/harness/source-record.schema.json` and review-required
`docs/harness/source-record-example.json`, manifest required-file and snippet
coverage, generated README routing, and live schema/example files. This gives
projects a structured provenance record shape while keeping project-curated
records separate from HarnessForge's fixed `research-sources.json` allowlist.
The latest large-codebase analysis and indexing slice is recorded in
`docs/harness/large-codebase-indexing-research.md` and implemented as read-only
`harnessforge index --target . --json`. It reports target-relative file
classes, language breakdown, manifests, components, entrypoints,
source-of-truth signals, review-required placeholders, no-command/no-write
execution metadata, file-scan limits, and component-inventory truncation.
Large repos can use `--max-files <N>` for deeper read-only scans while keeping
generated component inventories bounded. Boundaries: no networked indexing
service by default, no committed embeddings or private code summaries in
generated harnesses, no code excerpts, no machine-local paths, and any future
optional cache must be target-contained, reviewable, and safe to delete.
The latest local real-repo pass also fixed root Maven and Gradle command
inference for monorepo-classified repositories and docs/research repository
classification when non-code assets are present.
The follow-up real-repo quality pass fixed literal repo-relative path handling
for filenames with trailing spaces, added an `other` structural index class for
unclassified artifacts, and improved generated context for agent skill
catalogs, plugin manifests, and docs/catalog repositories. Remaining blocked
reference repos are blocked only because they do not expose a repo-owned
verification command.
The latest real-repo refinement pass fixed three narrower quality issues:
structural indexing ignores common OS metadata files, generated project context
now warns when component discovery reaches the bounded inventory limit, and
explicit CLI evidence/report paths are trimmed while literal repo-discovered
filenames remain preserved. The rendered-content sweep across 32 reference
repositories found no local-path leaks, no unrendered template tokens, no
generic context fallback, and no missing generated project context.
The latest generated-artifact quality pass added AGENTS project-context guidance
for detected GitHub workflow metadata, devcontainers, native C/C++, .NET, PHP,
Ruby, JavaScript or TypeScript assets without package-manager boundaries, and
existing root agent instruction files. The 32-repo generated-artifact scorer
now reports no local-path leaks, no unrendered template tokens, no generic
AGENTS context, no component-cap warning gaps, and no init dry-run failures.
The only remaining findings are review-required verification placeholders for
repositories without detected repo-owned validation commands.
The follow-up artifact-noise pass reduced repeated `REVIEW REQUIRED` markers in
generated sensor registries. Sensor rows now use concise pending placeholders
for project-specific purpose, owner, retirement condition, and review cadence.
Across 32 reference repositories, the generated-artifact scorer reports no
remaining findings, max total review markers dropped from 106 to 30, and sensor
registries have at most two review markers only when the repo has the
intentional no-command placeholder.
`scripts/refresh_research.py --check` validates duplicate source IDs and URLs,
required fields, placeholder text, canonical URL shape, arXiv `/abs/` URLs,
lock-file consistency, and local-path leakage before any metadata fetch. Root
POSIX and PowerShell entrypoints now run that gate after pin checks.
`effectiveness-evidence.schema.json` and
`effectiveness-evidence-example.json` define the local review shape for
harness-effectiveness claims: claim scope, baseline/candidate snapshots,
held-out task controls, replay type, feedback channels, runtime/workspace/
adapter contracts, candidate-sensitive metrics, worst-case quality, cost,
safety review, result artifacts, rollback, and human approval. This is local
release-prep guidance, not generated target-repo content.
Generated manifests now include `platformSourceReview` metadata with the
2026-06-15 review date, source IDs, source URLs, and a review-required flag
before changing platform floors, interpreter versions, runner labels, or CI
image assumptions. Generated change contracts now ask for current
primary-source evidence for platform-impacting changes. The primary-source
review checked Python version status, GitHub hosted runner labels, and the
GitHub runner-images Windows VS2026 migration notice.
Current robust-mode verification passes: focused generated workflow and CLI
warning tests, focused GitHub Action tests, focused generated verify-evidence
coverage, focused verify report-persistence tests, focused verify-evidence gate
tests, focused Action sync tests, focused session tests, focused sensor-registry
generator test, focused source-record generator test, focused index CLI tests,
focused effectiveness CLI and contract tests, full unit discovery and
POSIX/PowerShell entrypoints with 227 tests, compile, JSON/YAML validation, pin
check, research source check, rendered optional workflow audit and pin smoke,
session, plan, index, and effectiveness JSON smokes, expected-warning sync JSON
smoke, self-audit `100/100`, changed-file local-path scan, and diff hygiene.
Latest docs consistency pass also reran focused Action/generator/pin tests with
87 tests, pin check, self-audit `100/100`, stale-wording and local-path scans,
diff hygiene, and both local entrypoints with 227 tests each.
README split verification passed focused CLI/audit tests with 118 tests,
self-audit `100/100`, local-path scan, and diff hygiene. The audit known-file
list now includes `docs/installation.md`, `docs/usage.md`, and
`docs/capabilities.md`.
Generated first-agent guidance verification passed focused generator tests with
50 tests, full unit discovery with 228 tests, JSON validation, pin check,
durable local-path scan, diff hygiene, self-audit `100/100`, and both local
entrypoints with 228 tests each.
Full docs update pass is complete: `docs/harness/README.md`,
`docs/capabilities.md`, `docs/usage.md`, and `docs/harness/manifest.json` now
surface the first-agent task and the split top-level docs consistently.
`sync --check`
returns the expected warning for local workflow and instruction review surfaces
without blockers or generated drift.
The robust-mode backlog items for generated workflow sync preflight, sensor
registry, source-record schema support, large-codebase indexing research, and
the first structural index command are closed. The final score/benchmark slice
is closed as read-only `harnessforge effectiveness --target . --json`, which
assesses stored representative evidence and blocks unsupported performance
claims instead of running benchmarks or creating synthetic scores.
Existing eval guidance comes from the Harness Forge, Meta-Harness, Code as
Agent Harness catalog, and arXiv harness-eval reviews; those sources are mined
only for product ideas and are not copied into generated target-repo defaults.
The deeper Code as Agent Harness catalog pass added more eval-contract detail:
surface-layer naming, feedback-channel separation, multi-agent role/topology
and convergence requirements, adaptive promotion loops, domain-harness
ownership boundaries, and source-ledger hygiene. Keep these as local eval
guidance unless a later release decision turns a narrow piece into generated
starter guidance.
Accepted roadmap ideas are now captured in `docs/roadmap.md` and linked from
the root README. The roadmap includes unified reporting, compact repo maps,
SBOM-aware indexing with default detection and optional generation adapters,
first-agent task lifecycle tracking, a public open-source quality corpus,
major `--enhance-existing` quality improvements, interactive quickstart/init
UX, optional index adapters, Action summary polish, release evidence
automation, evidence-gated maturity levels, and expanded policy presets.
`docs/roadmap.md` is also part of the live harness: it is required by the
manifest, included in audit known files, listed in the component inventory,
routed from harness operations, and registered as a recurring sensor with review
cadence.
Generated target harnesses now include review-required
`docs/harness/roadmap.md`. Generated startup instructions, harness operations,
progress scaffolding, component inventory, sensor registry, and manifest
metadata route to it. Roadmap items must classify impact across local harness,
generated harness, CLI/runtime, existing project files, GitHub Action, optional
workflow scaffolds, tests/fixtures, release/package, research/source ledger,
security/privacy, platform contracts, and docs/UX before implementation.
Task-list doc patterns were reviewed from JobSentinel, Bluepeak, Persona,
RunHaven, and learn-harness-engineering resources. Adopted portable patterns
into local and generated roadmap guidance: compact active status,
active/completed/archive buckets, explicit status lifecycle, execution gates,
owner/evidence/retirement fields, technical-debt separation,
candidate-vs-commitment boundaries, generated-evidence promotion rules,
failure-mode maps, and a pre-release health lane.
Source weighting is now explicit: learn-harness-engineering resources are a
canonical higher-weight harness-pattern source for generic startup, task-list,
quality-score, and initializer behavior. Sibling repos remain field examples.
Target-repo files, commands, platform contracts, and maintainer decisions still
control project-specific overrides.
The canonical public source location is
`https://github.com/walkinglabs/learn-harness-engineering`; the local checkout
is only a review aid and should not be treated as the durable source in repo
docs.
The refreshed Walking Labs English lecture corpus was re-read directly and
treated as canonical generic harness guidance. Accepted portable ideas were
added to `docs/roadmap.md`, `docs/harness/sources.md`, live harness docs, and
generated templates: fresh-session tests, instruction lifecycle metadata,
dedicated initialization, evidence-gated feature state, completion evidence
ladders, agent-oriented repair messages, runtime plus process observability,
clean-state dimensions, benchmark/task evidence, and harness simplification.
Generated-content coverage was tightened in `tests/test_generate_audit.py`.
Focused verification passed with 52 generated/audit tests, compile, research
source check, manifest and feature JSON validation, self-audit `100/100`, and
diff hygiene.
Minimal-change and Karpathy-style instruction guidance has now been promoted
as portable harness discipline. Local and generated instructions,
`--enhance-existing` addenda, change contracts, roadmaps, operating-model docs,
quality docs, evaluator rubrics, source ledger, public capabilities/usage docs,
manifest snippets, and generated-content tests now enforce smallest-correct
change behavior: surface assumptions, avoid speculative scope, prefer existing
behavior and dependencies before new code, keep edits traceable, record
simplification ceilings, and verify non-trivial logic. Generated target repos
receive generic guidance only; do not add local path references, local tool
mandates, or project-branded instruction names.
Verification for this latest pass passed full unit discovery with 230 tests,
compile, feature and manifest JSON validation, research source check, pin
check, self-audit `100/100`, diff hygiene, and the durable local-path scan.
Walking Labs Lecture 02 five-subsystem guidance has also been promoted into the
local and generated harness: root instructions now name instructions, tools,
environment, state, and feedback as required subsystems; harness README docs
include feedback-first repair, least-privilege tool access, self-describing
environment state, progress tracking, controlled-variable exclusion tests with
failure attribution, and recurring harness-debt audits; quality docs now track
subsystem health. Focused generator/audit tests passed with 52 tests.
Effective-agent boundary guidance has now been promoted too: the model is the
LLM, while the effective coding agent is model plus harness. Local and generated
instructions, harness README docs, component inventory docs, capabilities docs,
source ledger, manifest snippets, and tests now treat system prompts,
instruction files, shell/file tools, git access, filesystem scope, startup
scripts, verification commands, stop hooks, lint/sensor checks, workflow
permissions, and evaluator loops as harness pieces that change effective agent
behavior. Focused generator/audit tests passed with 52 tests.
Product boundaries have now been tightened again after the RunHaven
self-healing leak. Generated target harnesses must not include
`docs/harness/self-healing.md`, `.github/workflows/harness-self-heal.yml`,
`with-self-heal-workflow`, scheduled research refresh, sibling HarnessForge
checkout commands, local path preferences, or repo-local AGY/Antigravity
mandates. HarnessForge repo-local self-healing remains only in this repository.
Audit scoring now checks the current quality contract: generated-file
ownership metadata, platform metadata, first-agent lifecycle, roadmap and
sensor lifecycle, verify/effectiveness evidence guidance, stale sibling
checkout avoidance, and generated-vs-local self-healing boundaries. The
offline `harnessforge corpus` command is implemented and green for pinned
public-repo-shaped fixtures.
RunHaven was rechecked with the corrected rules. Its generated self-healing doc
was deleted, manifest references were removed, active docs were generalized to
reviewed maintenance/automation wording, generated-file metadata was added, and
HarnessForge audit now returns `100/100`. `harnessforge report` is warning-only
for expected workflow/governance review surfaces.
Harness Maintenance Optimization is accepted in `docs/roadmap.md`: reduce
routine harness-doc fan-out by defining authoritative fact owners, change-to-doc
routing, generated summaries, and audit/report drift checks for stale duplicated
facts.
The first local optimization slice is now implemented:
`docs/harness/authoritative-facts.md` owns fact-owner routing, change-to-doc
routing, fan-out budgets, exceptions, and future audit/report expectations.
Harness operations and the sensor registry route to it. Self-audit requires the
map for the HarnessForge product repo.
The cross-boundary optimization slice is also implemented. Generated target
harnesses now include review-required `docs/harness/authoritative-facts.md`,
`harnessforge report` exposes docs fan-out routing status, and the corpus gate
checks the new generated map for unrendered template tokens and local paths.
Focused generator/CLI/corpus tests passed with 132 tests; full unit discovery
passed with 243 tests; self-audit stayed `100/100`; corpus JSON gate passed at
13 fixtures with minimum score `100`; local report smoke showed map `present`
and 12/12 covered surfaces; generated-target smoke showed map `pending_review`
and 12/12 covered surfaces.
Latest verification passed full unit discovery with 243 tests, compile, pin
check, research source check, manifest and feature JSON validation, self-audit
`100/100`, public corpus JSON gate, report smoke, generated-target docs fan-out
smoke, local-path scan, and diff hygiene.
Push local commits only at an explicit batch/release boundary or user request.
Release prep is intentionally deferred. Continue accepted roadmap work before
release gates, package publishing, or Action tag decisions. The pre-release
buildout now includes the golden public-repo fixture corpus, first-agent task
lifecycle evidence, report expansion, instruction-quality and signal-to-noise
reporting, compact repo maps and SBOM detection or adapter design, Action
summary polish, `release-check`, harness maturity levels, expanded policy
presets, and interactive quickstart/init UX. Return to release prep only after
those items are completed or explicitly deferred with owner, evidence, and risk
recorded.
