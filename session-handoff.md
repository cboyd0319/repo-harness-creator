# Session Handoff

Last Updated: 2026-06-14 UTC

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
- `scripts/refresh_research.py`
- `src/harnessforge/audit.py`
- `src/harnessforge/detect.py`
- `src/harnessforge/generate.py`
- `src/harnessforge/models.py`
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
- `.gitignore`

## Blockers

- No known blockers.
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

Review the local OWASP/security, CI-cost-control, generated-harness alignment,
local sibling harness comparison, HarnessForge rename, and platform-router
commits. Push only at an explicit batch/release boundary or user request. Before
a public Action release, run the manual macOS/Windows platform CI check if
hosted platform confirmation is needed, then decide whether to cut a `v1`
Action tag and which release-time SBOM/provenance controls should become
blocking.
