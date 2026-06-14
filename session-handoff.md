# Session Handoff

Last Updated: 2026-06-14 UTC

## Current Objective

Set up repo-harness-creator as a credible, cross-platform harness creation and
assessment tool, including the deep local-source pass, secure pinning,
self-healing, component-boundary improvements, a high-quality public README,
and the required AGENTS instruction format.

## Files

- `src/repo_harness_creator/`
- `tests/`
- `docs/harness/`
- `action.yml`
- `docs/action.md`
- `README.md`
- `AGENTS.md`
- `init.sh`
- `init.ps1`
- `tests/test_local_entrypoints.py`
- `scripts/refresh_research.py`
- `feature_list.json`
- `.github/workflows/ci.yml`
- `.github/workflows/harness-self-heal.yml`
- `scripts/check_pins.py`
- `scripts/refresh_research.py`

## Blockers

- No known blockers.
- Current full local POSIX and PowerShell verification passes with 50 tests, pin
  check, and self-audit `100/100`; POSIX also passes when launched with
  `PYTHONPATH=/tmp`.
- Research metadata refresh currently tracks 49 sources with one recorded Red
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

## Next Session

Decide whether the first release should cut a `v1` Action tag before broader
public use.
