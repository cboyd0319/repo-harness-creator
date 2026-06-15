# Session Handoff

Last Updated: 2026-06-15 UTC

## Current Objective

Set up HarnessForge as a credible, cross-platform harness creation and
assessment tool, including the deep local-source pass, secure pinning,
self-healing, component-boundary improvements, a high-quality public README,
and the required AGENTS instruction format.

## Files

- `src/harnessforge/`
- `tests/`
- `docs/harness/`
- `action.yml`
- `docs/action.md`
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
- `scripts/refresh_research.py`
- `src/harnessforge/audit.py`
- `src/harnessforge/cli.py`
- `src/harnessforge/detect.py`
- `src/harnessforge/generate.py`
- `src/harnessforge/github_action.py`
- `src/harnessforge/models.py`
- `src/harnessforge/readiness.py`
- `src/harnessforge/spec_system.py`
- `src/harnessforge/update.py`
- `src/harnessforge/templates/claude.md.tmpl`
- `src/harnessforge/templates/gemini.md.tmpl`
- `src/harnessforge/templates/copilot-instructions.md.tmpl`
- `src/harnessforge/templates/component-inventory.md.tmpl`
- `src/harnessforge/templates/research-sources.json.tmpl`
- `tests/test_detect.py`
- `tests/test_generate_audit.py`
- `tests/test_pins.py`
- `docs/harness/evaluator-rubric.md`
- `docs/harness/sources.md`
- `docs/harness/reference-mining-notes.md`
- `docs/harness/remaining-ideas-research.md`
- `.gitignore`

## Blockers

- No known blockers.
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
  design-only `verify --json` contract docs, schema, example, and fixture
  tests. Implemented the first P1 item: read-only workflow and work-item
  inventory in readiness. Implemented the second P1 item: context-budget and
  duplicate-instruction detection in readiness. Implemented the third P1 item:
  permission/governance inventory in readiness. Implemented the final P1 item:
  guided first-run UX with `harnessforge quickstart`. The P1 backlog from this
  research pass is implemented.
  P2 candidates: opt-in blueprints, real-agent evals, source-verified platform
  adapters, and sandbox/container readiness. Rejected defaults remain large
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
  instructions, personal tool mandates, large skill trees, blueprints, MCP
  setup, or extra agent adapters by default. Current verification passes full
  unit discovery with 160 tests, compile, pin check, self-audit `100/100`,
  diff hygiene, a read-only readiness smoke, and `sync --check` smoke against
  this repo. Readiness and sync check are warning-only because existing local
  instruction files and the two repo-local GitHub workflow definitions need
  review; there are no readiness blockers.
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
- Current sync preflight implementation is a CLI-only read path. It does not
  add mutation semantics, run target checks, or change generator output.
- The main README has been reorganized to make the project easier to understand
  from the outside: value proposition first, then at-a-glance outcomes,
  differentiators, boundaries, quickstart, readiness/sync, generated files,
  audit/update, Action use, security, and verification.
- Current `verify --json` work is design-only. It adds
  `docs/harness/verify-json-contract.md`, `verify-json.schema.json`, and
  `verify-json-example.json`, plus contract fixture tests. It does not add a
  CLI command or command execution semantics.
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

## Next Session

The P1 backlog from the remaining-ideas research pass is implemented. Continue
release prep by deciding whether any P2 item is required before a public Action
release. The strongest remaining P2 item is measured real-agent or
harness-quality eval guidance, now informed by the Harness Forge and
Meta-Harness paper review's frozen-replay, full-history log, validation, and
candidate-sensitive scorer guardrails.
Current in-progress release-prep slice adds local docs and readiness inventory
for that eval boundary: `effectiveness-eval-contract.md` defines the evidence
contract, and `effectivenessInventory` reports visible eval specs, scorer
scripts, result logs, and frontier artifacts as review surfaces. The
Code-as-harness paper catalog and additional arXiv pass are mined only for
product ideas; they are not being copied into generated target-repo defaults.
Current verification passes: focused readiness and contract tests, full unit
discovery with 162 tests, compile, pin check, JSON validation, local-path scan,
diff hygiene, self-audit `100/100`, quickstart smoke, and `sync --check` with
expected warning exit code `1`.
Push local commits only at an explicit batch/release boundary or user request.
Remaining product decisions before public release: component-directed monorepo
verification commands, path/package exclusions for intentionally vulnerable
training repos, Maven/Gradle dependency pin parsing, selective update semantics
for generated-owned files, manual macOS/Windows platform CI, `v1` Action tag,
and release-time SBOM/provenance gates.
