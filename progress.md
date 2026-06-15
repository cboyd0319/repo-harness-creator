# Progress

Last Updated: 2026-06-15 UTC

## Current Objective

Build the first package-quality implementation of HarnessForge as a
Python 3.13+ cross-platform CLI, reusable GitHub Action, and self-harnessed
maintenance loop.

## Current State

- Repository started with only `README.md` and `LICENSE`.
- Research reviewed local Bluepeak-AI, JobSentinel, and
  learn-harness-engineering harness references.
- Runtime direction is Python standard library only.
- Implemented Python package, CLI, reusable composite GitHub Action,
  cross-platform templates, self-harness docs, tests, and CI matrix.
- Completed a second adversarial source pass against JobSentinel sources and
  the Walking Labs English course. Added stricter audit checks, local Markdown
  link validation, bottleneck scoring, richer feature state, clean-state,
  evaluator, and quality artifacts.
- Completed a deeper local-source pass against Bluepeak-AI, JobSentinel,
  persona, and pi-harness. Added dependency pin policy, SHA-pinned Actions,
  pin enforcement, security boundary mapping, privacy labels, self-healing
  research refresh, component inventory, and personal-machine path hardening.
- Reconciled the source ledger against JobSentinel `docs/harness/sources.md`
  and refreshed 32 machine-readable research sources.
- Completed a README-design research pass across GitHub Docs, The Turing Way,
  OpenSSF Scorecard, and widely used open-source README examples. Reworked the
  root README as the project landing page and expanded the tracked research
  source ledger to 44 sources.
- Fixed the root composite Action manifest after hosted CI rejected an unquoted
  description value containing a colon. Added a local regression test for that
  manifest shape.
- Reformatted root and generated `AGENTS.md` content around the required
  project overview, build/test commands, code style, testing, and security
  sections, with harness-specific startup and handoff notes inside those
  sections.
- Completed a current best-practice hardening pass. Added PEP 639
  `license-files` metadata, set `PYTHONSAFEPATH=1` in the composite Action,
  ignored root manifest symlinks that resolve outside target repositories, and
  expanded local home-path redaction. GitHub Action report paths now must be
  target-relative and resolve inside the target repository, with slash-separated
  target-relative report outputs on every runner.
- Tightened research refresh to match the documented public-source boundary:
  non-HTTPS URLs, embedded credentials, localhost, and literal non-public IP
  targets are rejected before any fetch.
- Refreshed the research ledger to 49 sources, adding Python packaging, Python
  command-line, Python URL fetching, GitHub checkout, and OWASP SSRF guidance.
  The Red Hat public page returned HTTP 403 and is recorded in the lock file.
- Hosted CI run `27489182164` passed on Ubuntu and macOS but exposed a Windows
  output separator regression in Action report outputs. The local fix now
  normalizes those outputs to forward slashes before writing `GITHUB_OUTPUT`.
- Hosted CI run `27489310186` passed on `main` for Ubuntu 22.04, macOS 15, and
  Windows 2025 across Python 3.13.14 and 3.14.6.
- Continued the ease/security re-review against current GitHub Actions, Python,
  Python Packaging, and OWASP guidance. The current pass tightens research
  refresh URL validation for DNS resolutions and redirects, and disables
  persisted checkout credentials in the read-only CI workflow and examples.
- Fixed the root POSIX verification entrypoint so it prepends `src` even when a
  user already has `PYTHONPATH` set. The PowerShell entrypoint already had the
  equivalent path-prepend behavior.
- Hosted CI run `27490215814` passed on `main` for commit `fda509a` across
  Ubuntu 22.04, macOS 15, and Windows 2025 on Python 3.13.14 and 3.14.6.
- Continued the ease/security review with an AGY-assisted current-source pass.
  Fixed three concrete usability and refresh issues: bare CLI invocation now
  returns a usage error, generated scripts normalize `python3` commands through
  the selected interpreter, and research refresh validates relative redirects
  after resolving them against the source URL.
- Continued the GitHub Action output hardening pass against current GitHub
  workflow-command docs. Action outputs now use `$GITHUB_OUTPUT` delimiter
  blocks instead of flattening line breaks, so multiline output values remain a
  single declared output instead of becoming ambiguous environment-file lines.
- Responded to the hosted CI notice that `windows-2025` requests are being
  redirected to `windows-2025-vs2026` by June 15, 2026. The CI matrix now uses
  the explicit `windows-2025-vs2026` runner label, matching current GitHub
  runner docs and removing ambiguity about the Windows image under test.
- Closed the research-refresh DNS-rebinding transport gap. Refresh now connects
  HTTPS fetch sockets to the validated public DNS result while preserving the
  original host for TLS verification, and still revalidates redirects before
  following them.
- Closed the cross-platform path-containment helper gap. Action report paths,
  manifest-required files, and local Markdown link checks now recognize POSIX
  and Windows absolute/rooted path syntax consistently; Windows-style relative
  report separators are normalized to target-relative paths.
- Updated the scheduled self-healing workflow so it stages generated root
  harness files along with `docs/harness` and source templates, preventing
  unstaged root updates from causing empty commits or incomplete pull requests.
- Re-ran a deeper read-only comparison against `agent-governance-toolkit`.
  Accepted the small, durable pieces that fit this repo now: contribution
  policy, PR template, stronger security scope, `.gitignore` hygiene, and
  GitHub Action `min-score` validation. Deferred external workflow gates,
  SBOM/provenance, Scorecard, fuzzing, and CODEOWNERS until the release path
  and maintainer model justify the extra automation.
- Personally reviewed the current `microsoft/agent-governance-toolkit`
  `origin/main` snapshot for the requested `.github`, `scripts`, `examples`,
  security, compliance, policy, package, operation, benchmark, and Action
  paths. The local AGT clone was stale, so the review used a temporary archive
  of current `origin/main`. Accepted additional repo-fit items: multiline
  workflow fail-fast enforcement, local Markdown anchor validation with fenced
  code blocks ignored, forbidden `setup.py`/`build.rs` build-hook detection,
  example and security-sensitive contribution rules, and benchmark claim
  limits. Deferred AGT compliance suites, incident-response structure,
  secret-scanning, SBOM, Scorecard, CodeQL, dependency-review, and release
  workflows as too much automation before the release and maintainer model
  require them.
- Completed additional monorepo and repo-local harness research against official
  package-manager, language, build-system, GitHub Actions, and Terraform docs,
  plus the supplied Bazel, vanilla GitHub Actions, Harness IDP, awesome-monorepo,
  Medium, Atlassian, LinkedIn, and Lukas Masuch examples. Detection now
  separates workspace/layout markers, component manifests, and repo routing
  markers. It covers JavaScript workspaces and orchestrators, uv/Cargo/Go,
  Gradle/Maven/.NET, Bazel/Pants/Buck, inferred multi-component layouts,
  workflow path filters and `working-directory`, local Actions, devcontainers,
  Harness IDP folders, existing agent-instruction files, and Terraform roots
  and modules.
- Hardened the scheduled research and self-heal boundary. The workflow now runs
  at 12:00 UTC, the docs/templates state that research refresh reads only the
  fixed allowlist in `research-sources.json`, and fetched titles/headings/hashes
  are treated as untrusted review metadata rather than instructions.
- Added default audit enforcement for durable local absolute paths. Loaded
  harness docs and state fail audit when they contain machine-local absolute
  paths unless the caller uses an explicit local audit override. The generated
  harness templates carry the same repo-relative-path policy.
- Completed a deeper agentic-security research pass against OWASP GenAI,
  OWASP Agentic Applications, OWASP Agentic Skills, Microsoft AGT prompt
  injection fixtures, Endor's AI coding-agent benchmark, Lakera data-poisoning
  guidance, and the supplied Practical DevSecOps and Rogue Security summaries.
  The fixed research allowlist now tracks 88 sources.
- Hardened research refresh against poisoned source metadata. Titles/headings
  that resemble prompt injection, indirect prompt injection, credential
  exfiltration, or sensitive-file access are withheld from durable output and
  recorded as review signals instead.
- Added an audit requirement that generated and live harnesses document
  prompt-injection and data-poisoning boundaries as untrusted-content risks.
- Personally reviewed the requested OWASP CheatSheetSeries, SecurityShepherd,
  SAMM, and pytm sources for HarnessForge fit. Accepted narrow controls:
  tool/retrieval output remains untrusted, invisible Unicode and Markdown/HTML
  exfiltration markers are withheld from research metadata, intentionally
  vulnerable training/demo fixtures are preserved unless remediation is in
  scope, and material AI/RAG/agent, tool, auth, secret, data-flow, or deployment
  changes must update boundary/threat-model evidence.
- Tightened remote CI cost posture. Push/PR CI now runs the Ubuntu 22.04 Python
  3.13.14 path by default with superseded-run cancellation; macOS and Windows
  platform checks remain available through manual `workflow_dispatch`.
- Completed a deeper Walking Labs resources, projects, and harness-creator
  skill review. Accepted the parts that fit this repo now: generated advisory
  pin checker, generated release controls, optional manual CI/self-heal
  workflow scaffolds, generated-harness `100/100` quality gate, manifest drift
  coverage for shared control surfaces, initializer baseline-commit reminders,
  and structural-score caveats. Deferred generic architecture scanners, memory
  index cap checks, memory topic cleanup, and agent-specific tool-permission
  config validation as project-specific opt-ins.
- Fixed audit scoring so a domain only receives `5/5` when every check in that
  domain passes. This prevents a single failed security or scope check from
  rounding to a perfect score.
- Rechecked harnesses from macos-container-agents, Bluepeak-AI, persona,
  pi-harness, WormsWMD-macOS-Fix, unifi-configs, JobSentinel, and cboyd0319.
  Accepted generic controls that fit this project and generated harnesses now:
  root-agnostic local entrypoints, PowerShell native exit-code enforcement,
  optional `--no-env`/`-NoEnv` credential-free verification, broader advisory
  pin checks for containers, Python requirements, package manifests, and npm
  lockfiles, entropy promotion/evidence/stop rules, explicit completion bars,
  isolated release-artifact smoke-test guidance, and root scratch-report ignore
  patterns. Deferred app telemetry headers, model routing rules, public wiki
  mapping, file-size budgets, pre-commit lockfile hooks, and credential-backup
  test wrappers as project-specific opt-ins.
- Renamed the project to HarnessForge across the repo. Runtime code now lives
  under `src/harnessforge/`, the primary
  console script is now `harnessforge`, the composite Action and docs now point
  at `cboyd0319/harnessforge`, generated optional CI scaffolding uses
  `.github/workflows/harnessforge.yml`, and live workflows invoke
  `python -m harnessforge`.
- Completed a local best-practices, memory, and MIT sibling HarnessForge review.
  Accepted compact Claude, Gemini, and Copilot instruction routers; local agent
  override ignores; verification-command trust controls; and a rule that
  platform auto-memory remains personal state until stable facts are promoted
  into reviewed harness docs. Deferred the sibling project's dependency-heavy
  blueprint, MCP, settings, and global-config machinery.
- Completed a deep pass on OpenAI's Codex guide, "Building an AI-Native
  Engineering Team." Accepted the durable controls that fit this repo and
  generated harnesses: Delegate/Review/Own ownership boundaries across the
  SDLC, test-integrity review for agent-written tests, high-signal review
  criteria, and official source provenance in the fixed research allowlist.
- Added a reviewed `pins.toml` ledger and ledger-backed pin enforcement.
  `scripts/check_pins.py` and generated advisory pin checkers now parse
  `pins.toml` with `tomllib` when it is present, and tie Python pins,
  `package.json` direct versions, `package-lock.json` integrity values,
  Containerfile base image tags and digests, and profile image tags back to the
  ledger. Generated harnesses keep `pins.toml` optional.
- Rechecked all repo script surfaces and the local memory/best-practices docs.
  Accepted focused improvements: the product audit now respects a target repo's
  declared runtime/runner boundary, so macOS-only targets are not forced to
  restore PowerShell or document unrelated OS floors; this repo's root
  entrypoints now compile `scripts/` as product code; PowerShell entrypoints
  prefer `python3` before `python` when `PYTHON` is unset; Python dependencies
  with extras are accepted as exact pins tied to the base `pins.toml` package
  entry; and non-version strings such as `==latest` are rejected.
- Added explicit boundary documentation and regression coverage for the three
  HarnessForge surfaces: this repo's live harness, generated target harness
  artifacts, and the published GitHub Action. Generated harness defaults remain
  cross-platform; target-specific platform narrowing must be declared by the
  target repo; Action runs are input-driven and target-contained.
- Cleaned up stale quality snapshot text and the last old internal Action
  delimiter prefix. The quality document now reflects the current 92-test local
  suite, self-audit `100/100`, manual platform workflow release checkpoint, and
  recurring self-heal PR review boundary. Action output delimiter names now use
  the HarnessForge prefix.
- Started release prep locally. POSIX and PowerShell release gates pass with
  92 tests, pin check, and self-audit `100/100`; an isolated wheel build/install
  smoke for `harnessforge-0.1.0-py3-none-any.whl` generated and audited a fresh
  target harness at `100/100`. Wheel SHA-256:
  `34134b559fafe823c5f9b9b5f041eaf387b226ca9300b8b1abdfdc1f997e657e`.
- Clarified the generated/local boundary for agent tooling. Generated
  `GEMINI.md` keeps the intended Gemini/Antigravity loader router, but generated
  instruction entrypoints now have regression coverage against repo-local
  AGY/Antigravity research-tool mandates. Live and generated boundary maps state
  that generated harnesses must not inherit HarnessForge's local agent/tooling
  mandates.
- Completed a deep generated-content quality exercise against VexShield and
  Bazel reference repositories using read-only inspection, manual ideal harness
  sketches, and temporary shadow generation. Detection now keeps root markers
  before large docs trees, recognizes C/C++ and Starlark, treats root Cargo as
  Rust-first even with Bazel markers, adds Cargo fmt/clippy/workspace checks,
  adds nested component verification commands, skips fixture/vendor/docs
  command inference, detects hidden Claude/Gemini instruction surfaces, and
  avoids treating tool-only root Python config as a project verification
  command. Generated and enhanced instruction files now include detected
  project context and concrete Bazel boundary signals. Existing instruction
  files are preserved by default; `--enhance-existing` appends reviewed
  addenda without replacing project text. Missing verification now produces a
  failing review-required placeholder instead of a successful echo.
- Completed the next reference-repo quality exercise against
  agent-governance-toolkit, apple-container, Bluepeak-AI, JobSentinel,
  nhl-betting-analytics, persona, RunHaven, rustguard, and
  WormsWMD-macOS-Fix. Accepted generic fixes: docs-heavy multi-component repos
  now detect as monorepos, Swift Package Manager repos detect as `swift`, shell
  projects can use repo-local validation scripts, Makefile commands are based
  on declared targets, nested uv Python projects can route pytest to a single
  repo-level `scripts/tests` tree, and generated context now calls out Swift,
  Python, shell, Terraform, container image, and Tauri surfaces. Shadow audits
  now report remaining quality issues as project-owned stale manifests, local
  absolute scratch paths, or existing content drift instead of silently
  rewriting target repos.
- Completed a deeper generated-surface review across every template, a rendered
  default harness, a rendered custom-agent harness, optional workflow scaffolds,
  and the published Action docs. Live HarnessForge self-heal/research workflow
  behavior is now explicitly separate from generated optional workflow scaffolds
  and the input-driven composite Action. Generated self-heal scaffolds stay
  manual by default, do not inherit scheduled research refresh, stage generated
  router files, and preserve custom `--agent-file` values. Audit now follows
  the manifest-declared canonical instruction file, so custom-agent generated
  harnesses audit at `100/100`.
- Added generated-file ownership metadata, drift reporting, and explicit
  platform-contract generation options. Generated manifests now record generator
  identity, platform contract, generated-file ownership, template SHA-256, and
  content SHA-256 metadata. `harnessforge update --drift-report` reports
  missing, modified, unchanged, and template-drift status without writing files.
  CLI init/update and the composite Action now accept `--platform-contract` for
  cross-platform, macOS-only, Windows-only, or Linux-only target contracts.
  Platform-specific generation omits unsupported local entrypoint scripts, and
  optional self-heal scaffolds verify through the generated entrypoint for that
  contract. Optional workflow warnings are louder at generation time, Python
  detection now adds Ruff and mypy defaults from config, and generated review
  placeholders are marked `REVIEW REQUIRED`.
- Completed a deeper local reference-repo compatibility pass across 25 sibling
  repositories under the local GitHub checkout parent, with direct read-only
  detection/audit/dry-run checks, temporary generated-harness smoke tests, and a
  read-only AGY supplement. Accepted concrete fixes for scenario coverage:
  explicit platform-contract audit precedence with old-manifest fallback,
  docs-only and monorepo environment profiles, root Maven/Gemfile manifest
  priority, docs-site `validate.sh` detection, Poetry/Pipenv Python command
  prefixes, nested package-manager labels, skipped-file ownership/hash metadata
  that avoids immediate drift, clearer preserved-file onboarding warnings,
  generated/live pin-check allowances for Rust `build.rs`, and Docker
  multi-stage alias handling. Default init still preserves existing instruction
  files; the supported easy path for such repos is now explicitly surfaced as
  `--agent-file HARNESSFORGE_AGENTS.md`.
- Completed additional HarnessForge-adjacent research against local `awman`,
  `aspec`, and `maki`, plus public HarnessForge-like and harness-engineering
  sources. Accepted generic improvements: structured project spec detection,
  Just task-runner detection, architecture-lint routing without duplicate
  commands, generated-doc drift context, read-only `harnessforge inspect` with
  JSON output, and Python-project priority over docs-site classification.
  Deferred blueprints, MCP setup, memory schemas, large generated skill trees,
  LLM-assisted init, and extra agent adapter files until they are explicit
  opt-ins with current source evidence.
- Completed the remaining-ideas research pass without AGY. The ranked backlog
  is now in `docs/harness/remaining-ideas-research.md`. Highest-value next
  ideas are read-only readiness reporting, source-of-truth spec sync checks, a
  project verification JSON contract separate from harness audit, a `sync
  --check` drift alias, workflow/work-item inventory, context-budget and
  duplication audit signals, permission/governance inventory, guided first-run
  UX, explicit blueprint mode, and measured real-agent evals. Rejected defaults
  remain large skill/memory/platform config trees, LLM-assisted init,
  autonomous push/PR workflows, and copying ASPEC/AWMAN/Maki templates into
  target repos.
- Implemented read-only `harnessforge inspect --readiness` and
  `--readiness --json`. The report returns a stable verdict plus warnings,
  blockers, next actions, detected source-of-truth docs, runnable checks,
  generated drift, and review-required governance surfaces without running
  target repository commands or writing files.
- Reviewed additional spec-driven-development sources: the GitHub Spec Kit
  launch article, the supplied local Spec Kit checkout, Fowler's SDD tools
  article, and specdriven.ai. Accepted ideas for the next source-of-truth
  audit: detect `.specify` systems, active feature metadata, spec lifecycle
  conventions, global context versus feature-scoped specs, unresolved
  clarification markers, incomplete requirement checklists, missing plan/task
  artifacts, and weak spec-to-task traceability. Rejected default installation
  of Spec Kit, `.specify`, agent slash commands, presets, extensions,
  catalogs, or workflow engines into arbitrary target repos.
- Implemented source-of-truth spec sync detection across `.specify`, active
  Spec Kit-style feature metadata, `specs/` feature artifacts, `aspec/`,
  work-item templates, and repo workflow definition surfaces. Readiness now
  reports unresolved clarification markers, incomplete requirement checklists,
  missing plan/task artifacts, weak FR/SC traceability, tasks without file
  paths, and workflow surfaces requiring review. Audit now fails instruction
  files that do not route agents to detected source-of-truth specs.
- Implemented `harnessforge sync --check` as a read-only, CI-oriented preflight
  that wraps readiness, generated-file drift, source-of-truth spec routing,
  and review-required governance surfaces. Exit codes are `0` for ready, `1`
  for warning, and `2` for blocked.
- Reworked the main README to lead with the product value, explain why the
  project is different, and organize usage around inspect, readiness, sync,
  generation boundaries, generated files, audit, update/drift, GitHub Action
  use, security, and verification.
- Added the design-only `verify --json` contract: a markdown contract, JSON
  schema, and example payload under `docs/harness/`. The contract separates
  project verification reporting from harness scoring and keeps default mode
  plan-only with no target command execution.
- Added read-only workflow and work-item inventory to readiness. The inventory
  reports `.github/workflows/`, `aspec/workflows/`, and `workflows/` TOML/YAML
  files, visible setup/teardown/remediation/push/pull-request/CI-polling/
  credential surfaces, work-item templates, and concrete work-item files
  without generating or adopting ASPEC/AWMAN workflow formats.
- Added advisory context-budget and duplicate-instruction detection to
  readiness. The `contextBudget` payload reports instruction-file line and
  character counts plus repeated instruction-block pairs across `AGENTS.md`,
  `CLAUDE.md`, `GEMINI.md`, and Copilot instructions.
- Added advisory permission/governance inventory to readiness. The
  `governanceInventory` payload reports MCP configs, agent settings,
  hooks, devcontainers, sandbox configs, agent setup workflows, and environment
  files or templates as review surfaces without reading or exposing secret
  values.
- Added read-only guided first-run UX with `harnessforge quickstart`. The
  command composes detected project context, readiness, dry-run generation
  planning, preserved-file reporting, generated review placeholders,
  review-required surfaces, and next commands without writing files.
- Mined the local Harness Forge sibling repo and the user-supplied
  Meta-Harness paper PDF without AGY. Accepted transferable ideas around
  candidate-sensitive harness evals, full-history queryable logs,
  frozen-replay avoidance, do-no-harm quality floors, held-out validation,
  worst-case quality tracking, validation-before-expensive-eval, and explicit
  skill/plugin/installer governance surfaces. Extended `governanceInventory`
  to report agent skills, agent plugin manifests, and root installer scripts
  as advisory review-required surfaces.

## Recommended Next Step

The P1 backlog from the remaining-ideas research pass is implemented. Continue
release prep by deciding whether any P2 item is required before a public Action
release, with measured real-agent evals and source-verified platform adapters
as the strongest remaining candidates.
Push local commits only at an explicit batch/release boundary or user request.
Remaining product decisions before a first public Action release: whether to
add component-directed monorepo verification commands, path/package exclusions
for intentionally vulnerable training repos, Maven/Gradle dependency pin
parsing, and selective update semantics for generated-owned files. Then run
the manual macOS/Windows platform CI check and decide whether to cut a `v1`
Action tag and which release-time SBOM/provenance controls should become
blocking.

## Verification Evidence

- `PYTHONPATH=src:. python3 -m unittest tests.test_cli` passed with 24 tests,
  `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  152 tests, and `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed after adding `sync --check`.
- `PYTHONPATH=src:. python3 -m harnessforge sync --check --target . --json`
  returned warning exit code `1`, as expected for this repo because existing
  local instruction files require review; no generated drift or blockers were
  reported.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`,
  `python3 -m json.tool feature_list.json >/dev/null`, `PYTHONPATH=src:.
  python3 -m harnessforge audit --target . --min-score 85`, and `git diff
  --check` passed after the README reorganization and `sync --check` slice.
  Self-audit stayed `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_verify_contract` passed
  after adding the `verify --json` contract, schema, and example payload.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  154 tests, `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed with self-audit `100/100`, and `git diff --check` passed after the
  `verify --json` contract slice.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  155 tests, `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed with self-audit `100/100`, and `PYTHONPATH=src:. python3 -m
  harnessforge sync --check --target . --json` returned expected warning exit
  code `1` after adding workflow/work-item inventory. The warning now includes
  this repo's two GitHub workflow definitions, plus existing local instruction
  review items; no blockers or generated drift were reported.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  156 tests, `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed with self-audit `100/100`, and `PYTHONPATH=src:. python3 -m
  harnessforge sync --check --target . --json` returned expected warning exit
  code `1` after adding context-budget readiness. This repo has no
  context-budget findings; warning state still comes from workflow and existing
  local instruction review items.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  157 tests, `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed with self-audit `100/100`, and `PYTHONPATH=src:. python3 -m
  harnessforge sync --check --target . --json` returned expected warning exit
  code `1` after adding governance inventory. This repo has no governance
  inventory items; warning state still comes from workflow and existing local
  instruction review items.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  160 tests, `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  passed with self-audit `100/100`, and `PYTHONPATH=src:. python3 -m
  harnessforge quickstart --target .` passed after adding guided first-run UX.
- `PYTHONPATH=src:. python3 -m unittest tests.test_cli.CliTests.test_inspect_readiness_reports_governance_inventory`
  passed after extending governance inventory for agent skills, plugin
  manifests, and installer scripts. A read-only readiness smoke against
  the local Harness Forge sibling repo now reports warning with
  `.claude-plugin/marketplace.json`, `skills/meta-harness/SKILL.md`, and
  `install.sh` in `governanceInventory` instead of incorrectly reporting
  clean ready.
- A paper-catalog and arXiv harness-eval mining pass added a proposed
  `effectiveness-eval-contract.md` and read-only `effectivenessInventory`
  readiness output. The imported boundary is local and advisory: detect eval
  assets, require candidate-sensitive and held-out evidence before claims, and
  keep synthesized or evolved harness loops out of default generated content.
- Current effectiveness-eval checks pass: focused readiness and contract tests,
  full unit discovery with 162 tests, compile, pin check, JSON validation,
  local-path scan, diff hygiene, self-audit `100/100`, quickstart smoke, and
  `sync --check` with expected warning exit code `1`.
- The user-supplied Meta-Harness PDF was unavailable to local text extractors,
  so the same paper was reviewed via arXiv HTML. `docs/harness/verify-json-contract.md`
  now records that benchmark/eval claims need candidate-sensitive metrics,
  held-out or contamination controls, worst-case quality, do-no-harm floors,
  and frozen-replay disclosure.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  148 tests, and `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed after adding source-of-truth spec sync detection.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`,
  `PYTHONPATH=src:. python3 -m harnessforge inspect --target . --readiness
  --json`, and `git diff --check` passed after source-of-truth spec sync
  detection. Self-audit stayed `100/100`; readiness reported warning-only
  existing local instruction-file review items and no blockers.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  143 tests, and `PYTHONPATH=src:. python3 -m compileall src tests scripts`
  passed after adding read-only inspect readiness reporting.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`,
  `git diff --check`, and
  `PYTHONPATH=src:. python3 -m harnessforge inspect --target . --readiness
  --json` passed. Self-audit stayed `100/100`; readiness reported warning-only
  review items for existing local instruction files and no blockers.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`
  and `git diff --check` passed after adding the remaining-ideas research
  artifact and updating handoff state.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  138 tests after adding generic structured-spec, Just, architecture-lint,
  generated-doc context, `inspect`, and Python-package/docs-site detection
  changes.
- `PYTHONPATH=src:. python3 -m compileall src tests scripts`,
  `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`,
  and `git diff --check` passed; self-audit stayed `100/100`.
- Temporary shadow generation against local `awman`, `aspec`, and `maki`
  confirmed improved command/context quality without copying their local
  formats into generated output. Inspecting a temporary public HarnessForge-like
  clone confirmed root Python projects with docs sites detect as Python projects,
  not docs-only repositories.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  116 tests after the reference-repo compatibility pass. Compile, pin check,
  JSON parsing, self-audit `100/100`, `git diff --check`, rendered
  compatibility smokes, and temporary reference-repo detection/generation
  matrices passed.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  103 tests after adding generated-file ownership metadata, drift reporting,
  platform-contract options, louder optional-workflow warnings, Ruff/mypy
  Python defaults, review-required placeholders, and platform-specific
  self-heal verification.
- `PYTHONPATH=src:. python3 -m compileall src tests scripts`,
  `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`, JSON parsing,
  `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85`,
  `git diff --check`, and rendered target smokes passed; self-audit stayed
  `100/100`.
- Earlier targeted checks for the same slice passed with 12 focused tests, then
  77 nearby generator, Action, CLI, pin, and detection tests. Rendered target
  smokes confirmed default optional workflows and macOS-only generated targets
  audit at `100/100`; drift smoke confirmed modified generated files are
  reported without writing updates.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_github_action tests.test_refresh_research tests.test_pins` passed
  with 70 focused tests after adding generated workflow/Action boundary
  assertions, generated self-heal staging coverage, custom `--agent-file`
  self-heal coverage, and Action-doc boundary assertions.
- Rendered default and custom-agent target smokes passed. The default generated
  target with both optional workflows audited at `100/100`; the custom
  `--agent-file PROJECT_AGENTS.md` target audited at `100/100`; generated scans
  found no local-commit wording, `Local production harness patterns`,
  AGY/Antigravity research mandates, schedules, cron triggers, or
  `refresh_research.py` inheritance in generated targets.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  97 tests. `PYTHONPATH=src:. python3 -m compileall src tests scripts`,
  `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`, JSON/template
  parsing, `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85`, and `git diff --check` passed; self-audit stayed `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_refresh_research` passed with 44 focused tests after adding the
  generated instruction-entrypoint guard for repo-local AGY/Antigravity research
  mandates.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with
  93 tests. `python3 -m compileall src tests`, generated-template mandate scan,
  `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`, `PYTHONPATH=src:.
  python3 -m harnessforge audit --target . --min-score 85`, and `git diff
  --check` passed; self-audit stayed `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5: doctor, compile,
  92 tests, pin check, and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5: doctor, compile, 92 tests, pin check, and self-audit `100/100`.
- Isolated release smoke passed from a temporary directory outside the repo:
  built `harnessforge-0.1.0-py3-none-any.whl`, installed it in a fresh venv,
  confirmed `harnessforge --version`, generated a target harness, audited it at
  `100/100`, and recorded wheel SHA-256
  `34134b559fafe823c5f9b9b5f041eaf387b226ca9300b8b1abdfdc1f997e657e`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action`, `python3 -m
  compileall src/harnessforge/github_action.py`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `PYTHONPATH=src:. python3 -m harnessforge
  audit --target . --min-score 85`, stale-string scan, and `git diff --check`
  passed after stale quality snapshot and Action delimiter cleanup.
- Personally scanned the requested OWASP CheatSheetSeries, SecurityShepherd,
  SAMM, and pytm materials without delegating the review. The accepted controls
  were limited to source-backed harness policy, audit checks, fixed allowlist
  entries, and CI cost controls.
- `PYTHONPATH=src:. python3 -m unittest tests.test_pins
  tests.test_generate_audit` passed with 36 focused tests after adding
  ledger-backed pin checks.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_github_action tests.test_local_entrypoints tests.test_pins` passed
  with 50 focused tests after the script/boundary pass.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 91
  tests after the script/boundary pass, then 92 tests after tightening Python
  exact-version requirement parsing.
- `python3 -m compileall scripts src tests`, `bash -n init.sh`, PowerShell AST
  parse of `init.ps1`, JSON/TOML metadata parse, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `git diff --check`, and `PYTHONPATH=src:.
  python3 -m harnessforge audit --target . --min-score 85` passed after the
  script/boundary pass; self-audit stayed `100/100`.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target
  /path/to/RunHaven --min-score 85` passed with `100/100`, confirming a
  declared macOS-only target is checked for its runtime boundary without being
  forced to satisfy PowerShell checks.
- `./init.sh` and `pwsh -NoProfile -File ./init.ps1` passed after the
  script/boundary pass: doctor, compile, 92 unit tests, pin check, and
  self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 87
  tests after the pins-ledger batch.
- `python3 -m compileall scripts src tests`, `python3` `tomllib` parse of
  `pins.toml`, `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`,
  `git diff --check`, and `PYTHONPATH=src:. python3 -m harnessforge audit
  --target . --min-score 85` passed; self-audit stayed `100/100`.
- `./init.sh` and `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1
  with Python 3.14.5 after the pins-ledger batch: doctor, compile, 87 unit
  tests, pin check, and self-audit `100/100`.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed
  106 fixed-allowlist sources with the same single known Red Hat 403 failure.
  No current source metadata triggered adversarial review signals.
- `PYTHONPATH=src:. python3 -m unittest tests.test_refresh_research
  tests.test_pins tests.test_generate_audit` passed with 44 focused tests after
  adding invisible-Unicode/Markdown-exfiltration metadata withholding, OWASP
  source entries, fixture/threat-model controls, and CI-cost workflow tests.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 76
  tests. JSON validation for research sources, source template, and manifest
  passed.
- `python3 -m compileall src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `git diff --check`, and
  `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85` passed; self-audit stayed `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the
  OWASP/security and CI-cost-control batch: doctor, compile, 76 unit tests, pin
  check, and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the OWASP/security and CI-cost-control batch: doctor, compile,
  76 unit tests, pin check, and self-audit `100/100`.
- Walking Labs resources/projects/harness-creator review completed with an AGY
  read-only supplement and direct local file inspection. Imported controls are
  generated pin checking, release controls, optional workflow scaffolds,
  generated-harness quality gate, manifest drift tests, and initializer
  baseline-commit reminders.
- `PYTHONPATH=src:. python3 -m unittest tests.test_cli tests.test_github_action
  tests.test_generate_audit tests.test_pins` passed with 45 focused tests after
  generated pin checker, optional workflow scaffolds, release controls, and
  manifest drift coverage.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 81 tests.
- `python3 -m compileall src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `git diff --check`, and
  `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85` passed; self-audit stayed `100/100`.
- Local sibling harness comparison completed with a read-only AGY supplement and
  direct file review. Imported controls are root-agnostic init execution,
  PowerShell native fail-fast handling, optional credential-free verification,
  broader advisory pin signals, entropy promotion/evidence/stop rules,
  completion bars, isolated release-artifact smoke-test guidance, and root
  scratch-report ignore patterns.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_pins` passed with 33 focused tests after the local-harness
  comparison changes.
- `python3 -m compileall scripts src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, and JSON validation for
  `feature_list.json` and `docs/harness/manifest.json` passed after the
  local-harness comparison changes.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 84
  tests after the local-harness comparison changes. Compile, pin check,
  self-audit `100/100`, JSON validation, and `git diff --check` passed.
- Local best-practices and memory docs plus the MIT sibling HarnessForge project
  were reviewed directly with a read-only AGY supplement. Imported controls are
  short platform routers, local override ignores, verification-command trust
  wording, and personal-state treatment for platform auto-memory.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_cli` passed with 31 focused tests after adding generated Claude,
  Gemini, and Copilot routers.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 85 tests.
  `python3 -m compileall scripts src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `PYTHONPATH=src:. python3 -m harnessforge
  audit --target . --min-score 85`, JSON validation, and `git diff --check`
  passed. The local-path scan found only the intentional file-scheme refresh
  rejection test fixture.
- `./init.sh` and `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1
  with Python 3.14.5 after the platform-router batch: doctor, compile, 85 unit
  tests, pin check, and self-audit `100/100`.
- The official OpenAI Codex AI-native engineering guide was reviewed from the
  provided local copy and official source URL. Imported controls are
  Delegate/Review/Own SDLC boundaries, agent-generated test integrity, and
  high-signal review guidance.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed
  107 fixed-allowlist sources with the same known Red Hat 403 failure.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_refresh_research` passed with 42 focused tests after adding the
  Codex SDLC controls and source entry.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 85 tests.
  `python3 -m compileall scripts src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `PYTHONPATH=src:. python3 -m harnessforge
  audit --target . --min-score 85`, JSON validation, and `git diff --check`
  passed. The local-path scan found only the intentional file-scheme refresh
  rejection test fixture.
- `./init.sh` and `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1
  with Python 3.14.5 after the Codex SDLC controls batch: doctor, compile, 85
  unit tests, pin check, and self-audit `100/100`.
- `harnessforge/init.sh --no-env` and `harnessforge/init.ps1
  -NoEnv` passed from the parent directory with seeded AI API-key environment
  variables, proving root-agnostic execution and credential-clearing paths for
  POSIX and PowerShell.
- `git check-ignore -v TEST_REPORT.md TEST_PLAN.md TEST_SUMMARY.md` confirmed
  root scratch-report ignore patterns are active.
- HarnessForge rename checks passed: focused CLI/Action/generator/pin tests
  passed with 48 tests, full unit discovery passed with 84 tests, compile
  passed, POSIX and PowerShell entrypoints passed, pin check passed,
  metadata/JSON validation passed, stale-name and local-path scans passed,
  editable install smoke passed, diff hygiene passed, and self-audit stayed
  `100/100`.
- Required read-only `agy` research pass completed against this repo plus the
  local AGT prompt-injection benchmark and OWASP Agentic Skills repo. Findings
  were personally checked against local files and public OWASP/user-provided
  sources before implementation.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed
  88 sources with the same single known Red Hat 403 failure recorded. No
  current source metadata triggered adversarial review signals.
- `PYTHONPATH=src:. python3 -m unittest tests.test_refresh_research
  tests.test_generate_audit` passed with 36 focused tests after adding
  adversarial-metadata withholding and the prompt-injection/data-poisoning
  audit boundary.
- JSON validation for research sources, source template, manifest, and lock
  files passed. `git diff --check` and self-audit passed; self-audit stayed
  `100/100`.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 73
  tests after the agentic-security source and metadata hardening slice.
- `python3 -m compileall src tests scripts` and `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .` passed.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the
  agentic-security source and metadata hardening slice: doctor, compile, 73
  unit tests, pin check, and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the agentic-security source and metadata hardening slice:
  doctor, compile, 73 unit tests, pin check, and self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_cli
  tests.test_generate_audit tests.test_pins` passed with 31 focused tests after
  self-heal schedule, fixed-allowlist research, and local absolute path audit
  hardening.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 72
  tests.
- `python3 -m compileall src tests scripts`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, `git diff --check`, and
  `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85` passed; self-audit stayed `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the self-heal
  automation and local-path policy slice: doctor, compile, 72 unit tests, pin
  check, and self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the self-heal automation and local-path policy slice: doctor,
  compile, 72 unit tests, pin check, and self-audit `100/100`.
- Personal review of the current `microsoft/agent-governance-toolkit`
  `origin/main` snapshot completed without Antigravity delegation; local clone
  lag was handled by reviewing a temporary archive of `origin/main`.
- Additional monorepo research completed with the earlier read-only `agy` pass,
  direct inspection of the supplied local `bazel-monorepo` and
  `awesome-monorepo` references, cloned public examples from
  `harness-idp-sandbox/harness-monorepo` and
  `gamgi/github-actions-vanilla-monorepo-example`, and browser review of the
  supplied monorepo and repo-local harness articles.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed
  76 sources with the same single known Red Hat 403 failure recorded.
- `PYTHONPATH=src:. python3 -m unittest tests.test_detect
  tests.test_generate_audit tests.test_refresh_research` passed with 46
  focused tests after workspace/layout, routing-marker, Terraform component,
  generated inventory, and source-ledger updates.
- `python3 -m compileall src tests`, `PYTHONPATH=src:. python3
  scripts/check_pins.py --root .`, and JSON validation for feature, manifest,
  source, lock, and template files passed after the monorepo slice.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the monorepo
  detection slice: doctor, compile, 69 unit tests, pin check, and self-audit
  `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the monorepo detection slice: doctor, compile, 69 unit tests,
  pin check, and self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit
  tests.test_pins` passed with 22 focused tests after workflow fail-fast,
  local Markdown anchor, fenced-code link, and build-hook checks.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .`, `git diff
  --check`, and `PYTHONPATH=src:. python3 -m harnessforge audit
  --target . --min-score 85` passed; self-audit stayed `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the personal AGT
  current snapshot slice: doctor, compile, 60 unit tests, pin check, and
  self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the personal AGT current snapshot slice: doctor, compile, 60
  unit tests, pin check, and self-audit `100/100`.
- Read-only `agy` deep comparison against `agent-governance-toolkit` completed;
  accepted contribution policy, PR template, stronger security scope,
  `.gitignore` hygiene, and Action `min-score` validation while deferring
  heavier workflow gates.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action
  tests.test_generate_audit tests.test_pins` passed with 25 focused tests after
  the deeper AGT-derived change slice.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed after the
  Action metadata wording update.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the deeper
  AGT-derived changes: doctor, compile, 56 unit tests, pin check, self-audit
  `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the deeper AGT-derived changes: doctor, compile, 56 unit tests,
  pin check, self-audit `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5: doctor, compile,
  46 unit tests, pin check, self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5: doctor, compile, 46 unit tests, pin check, self-audit `100/100`.
- Isolated virtualenv package install passed; `harnessforge --version` returned
  `0.1.0`, generated target init included component and research starter files,
  generated 32 research source records, and installed CLI audit passed.
- Isolated generated-harness smoke passed with 49 research source records.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 46
  tests.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` passed with
  5 focused Action tests after report output normalization.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85` passed with self-audit `100/100`.
- `python3 scripts/refresh_research.py --root .` refreshed 49 sources with one
  recorded 403 fetch failure from Red Hat.
- `git diff --check` passed.
- Hosted CI run `27489310186` passed on `main` after the report output fix.
- `PYTHONPATH=src:. python3 -m unittest tests.test_pins
  tests.test_refresh_research` passed with 16 focused tests.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed after the
  read-only CI checkout change.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed 49
  sources with one recorded 403 fetch failure from Red Hat under the stricter
  DNS and redirect validation.
- Isolated generated-harness smoke passed with 49 research source records after
  adding the new security guidance sources.
- `PYTHONPATH=src:. python3 -m unittest tests.test_local_entrypoints` failed
  before the POSIX entrypoint fix and passed after it.
- `PYTHONPATH=<non-repo-path> ./init.sh` passed on macOS 26.5.1 with Python 3.14.5:
  doctor, compile, 47 unit tests, pin check, self-audit `100/100`.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the final state
  updates: doctor, compile, 47 unit tests, pin check, self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after the final state updates: doctor, compile, 47 unit tests, pin
  check, self-audit `100/100`.
- Hosted CI run `27490215814` passed on `main` for commit `fda509a` across
  Ubuntu 22.04, macOS 15, and Windows 2025 on Python 3.13.14 and 3.14.6.
- `PYTHONPATH=src:. python3 -m unittest tests.test_cli
  tests.test_generate_audit tests.test_refresh_research` passed with 32 focused
  tests after the CLI, generated command, and relative redirect fixes.
- `PYTHONPATH=src:. python3 -m unittest tests.test_refresh_research` passed
  with 16 focused tests after research-refresh transport hardening.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 52
  tests after research-refresh transport hardening.
- `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` refreshed 49
  sources through pinned public-DNS transport with one recorded 403 fetch
  failure from Red Hat.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after
  research-refresh transport hardening: doctor, compile, 52 unit tests, pin
  check, self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after research-refresh transport hardening: doctor, compile, 52 unit
  tests, pin check, self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action
  tests.test_generate_audit tests.test_detect` passed with 25 focused tests
  after cross-platform path-containment hardening.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 54
  tests after cross-platform path-containment hardening.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed after the
  Action metadata wording update.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after
  cross-platform path-containment hardening: doctor, compile, 54 unit tests,
  pin check, self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after cross-platform path-containment hardening: doctor, compile, 54
  unit tests, pin check, self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_pins` passed with 4 focused
  tests after self-heal staging hardening.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 55
  tests after self-heal staging hardening.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed after the
  self-heal workflow change.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after self-heal
  staging hardening: doctor, compile, 55 unit tests, pin check, self-audit
  `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after self-heal staging hardening: doctor, compile, 55 unit tests, pin
  check, self-audit `100/100`.
- Read-only `agy` comparison against `agent-governance-toolkit` completed; the
  accepted changes were limited to `.gitignore` hygiene and `SECURITY.md`.
- `git check-ignore -v ...` confirmed macOS artifacts, local credential
  patterns, and harness report outputs are ignored.
- `git diff --check` passed after the `.gitignore` and `SECURITY.md` update.
- `PYTHONPATH=src:. python3 -m harnessforge audit --target .
  --min-score 85` passed with self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 50
  tests after the current ease/security fix slice.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after the current
  state updates: doctor, compile, 50 unit tests, pin check, self-audit
  `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python 3.14.5
  after the current state updates: doctor, compile, 50 unit tests, pin check,
  self-audit `100/100`.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` passed with
  5 focused Action tests after delimiter-output hardening.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 50
  tests after delimiter-output hardening.
- `./init.sh` passed on macOS 26.5.1 with Python 3.14.5 after
  delimiter-output hardening: doctor, compile, 50 unit tests, pin check,
  self-audit `100/100`.
- `pwsh -NoProfile -File ./init.ps1` passed on macOS 26.5.1 with Python
  3.14.5 after delimiter-output hardening: doctor, compile, 50 unit tests, pin
  check, self-audit `100/100`.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed after
  switching the CI matrix to `windows-2025-vs2026`.
- `git diff --check` passed after switching the CI matrix to
  `windows-2025-vs2026`.
