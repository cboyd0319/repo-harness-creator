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

## Next Session

Continue the ease/security re-review against the remaining lower-priority
findings, then decide whether the first release should cut a `v1` Action tag
before broader public use.
