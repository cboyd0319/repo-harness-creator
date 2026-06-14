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

## Recommended Next Step

Continue the ease/security re-review against the remaining findings, especially
the research-refresh DNS-rebinding transport question and cross-platform path
containment helpers, then decide whether to cut a `v1` Action tag before
broader public use.

## Verification Evidence

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
- `PYTHONPATH=/tmp ./init.sh` passed on macOS 26.5.1 with Python 3.14.5:
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
