# Progress

Last Updated: 2026-06-14 UTC

## Current Objective

Build the first package-quality implementation of repo-harness-creator as a
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
- Completed additional monorepo and repo-harness research against official
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

## Recommended Next Step

After push, watch hosted CI for the agentic-security source and metadata
hardening slice. Then decide whether to cut a `v1` Action tag before broader
public use, whether to keep both Python minors in CI or trim to Python 3.13
only, and whether deeper workspace graph parsing or release-time
SBOM/provenance should come next.

## Verification Evidence

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
  `PYTHONPATH=src:. python3 -m repo_harness_creator audit --target .
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
  supplied monorepo and repo-harness articles.
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
  --check`, and `PYTHONPATH=src:. python3 -m repo_harness_creator audit
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
- Isolated virtualenv package install passed; `repo-harness --version` returned
  `0.1.0`, generated target init included component and research starter files,
  generated 32 research source records, and installed CLI audit passed.
- Isolated generated-harness smoke passed with 49 research source records.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests` passed with 46
  tests.
- `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` passed with
  5 focused Action tests after report output normalization.
- `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` passed.
- `PYTHONPATH=src:. python3 -m repo_harness_creator audit --target .
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
- `PYTHONPATH=src:. python3 -m repo_harness_creator audit --target .
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
