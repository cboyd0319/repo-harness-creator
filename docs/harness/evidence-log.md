# Evidence Log

Use this for compact current evidence. Keep raw logs out of this file.

| Date | Scope | Command Or Review | Result | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-14 | GitHub Action output hardening | Current GitHub workflow-command docs plus local code review | pass | Replaced newline flattening with `$GITHUB_OUTPUT` delimiter blocks so multiline values remain one declared output. |
| 2026-06-14 | GitHub Action tests | `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` | pass | 5 focused tests after delimiter-output hardening. |
| 2026-06-14 | Local unit tests | `PYTHONPATH=src:. python3 -m unittest discover -s tests` | pass | 50 tests after delimiter-output hardening. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 50 tests, pin check, and self-audit `100/100` after delimiter-output hardening. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 50 tests, pin check, and self-audit `100/100` after delimiter-output hardening. |
| 2026-06-14 | Current ease/security review | AGY-assisted current-source pass plus local verification against Python argparse and GitHub Actions docs | pass | Accepted CLI missing-subcommand, generated `python3` normalization, and relative redirect findings; deferred broader/low-confidence findings for separate review. |
| 2026-06-14 | Focused behavior tests | `PYTHONPATH=src:. python3 -m unittest tests.test_cli tests.test_generate_audit tests.test_refresh_research` | pass | 32 tests covering bare CLI usage errors, generated `python3` interpreter normalization, and validated relative redirects. |
| 2026-06-14 | Local unit tests | `PYTHONPATH=src:. python3 -m unittest discover -s tests` | pass | 50 tests after the current ease/security fix slice. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 50 tests, pin check, and self-audit `100/100` after current state updates. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 50 tests, pin check, and self-audit `100/100` after current state updates. |
| 2026-06-14 | POSIX entrypoint regression | `PYTHONPATH=src:. python3 -m unittest tests.test_local_entrypoints` | pass | New regression failed before the fix and passed after `init.sh` began prepending `src` to existing `PYTHONPATH`. |
| 2026-06-14 | POSIX polluted environment | `PYTHONPATH=/tmp ./init.sh` | pass | Doctor, compile, 47 tests, pin check, and self-audit `100/100` passed with a pre-existing `PYTHONPATH`. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 47 tests, pin check, and self-audit `100/100` after final state updates. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 47 tests, pin check, and self-audit `100/100` after final state updates. |
| 2026-06-14 | Hosted CI | `gh run view 27490215814 --json status,conclusion,headSha,url` | pass | Commit `fda509a` passed CI across Ubuntu 22.04, macOS 15, and Windows 2025 on Python 3.13.14 and 3.14.6. |
| 2026-06-14 | Root hardening pass | Current-source review against Python Packaging User Guide, Python command-line docs, and GitHub Actions secure-use docs | pass | Added `license-files`, `PYTHONSAFEPATH=1`, root-manifest symlink escape protection, broader home-path redaction, public-HTTPS-only research refresh, and target-contained Action report paths. |
| 2026-06-14 | GitHub Action outputs | `gh run view 27489182164 --log-failed` | diagnosed | Windows tests failed because report outputs used backslashes; local fix normalizes report outputs to slash-separated target-relative paths. |
| 2026-06-14 | GitHub Action tests | `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` | pass | 5 focused tests after report output normalization. |
| 2026-06-14 | Hosted CI | `gh run view 27489310186 --json status,conclusion,headSha,url` | pass | Commit `b622cfb` passed CI across Ubuntu 22.04, macOS 15, and Windows 2025 for Python 3.13.14 and 3.14.6. |
| 2026-06-14 | Current-source review | GitHub Actions secure use, actions/checkout v6, Python `PYTHONSAFEPATH`, Python Packaging User Guide, OWASP SSRF guidance | pass | Accepted DNS/redirect research refresh hardening and read-only checkout credential opt-out; rejected stale license-metadata recommendation because current PyPA guidance uses `license = "MIT"` with `license-files`. |
| 2026-06-14 | Research refresh tests | `PYTHONPATH=src:. python3 -m unittest tests.test_refresh_research` | pass | 13 tests, including private DNS resolution and redirect-target rejection. |
| 2026-06-14 | Pin/workflow tests | `PYTHONPATH=src:. python3 -m unittest tests.test_pins tests.test_refresh_research` | pass | 16 focused tests after read-only CI checkout credential hardening. |
| 2026-06-14 | Research refresh | `PYTHONPATH=src:. python3 scripts/refresh_research.py --root .` | pass | 49 sources checked under DNS and redirect validation; one Red Hat 403 remains recorded. |
| 2026-06-14 | Generated harness smoke | isolated `repo_harness_creator init` into a temp target | pass | Generated research source file contains 49 sources after adding Python urllib, actions/checkout, and OWASP SSRF guidance. |
| 2026-06-14 | Local unit tests | `PYTHONPATH=src:. python3 -m unittest discover -s tests` | pass | 46 tests after research refresh DNS/redirect hardening and read-only CI checkout coverage. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 46 tests, pin check, self-audit `100/100`. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 46 tests, pin check, self-audit `100/100`. |
| 2026-06-14 | Local unit tests | `PYTHONPATH=src:. python3 -m unittest discover -s tests` | pass | 43 tests, including symlinked root manifests, Action `PYTHONSAFEPATH`, home-path redaction, research URL-boundary, and Action report-path regressions. |
| 2026-06-14 | Pin enforcement | `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` | pass | Package build pins and external Action SHAs validated after `action.yml` and `pyproject.toml` changes. |
| 2026-06-14 | Self-audit | `PYTHONPATH=src:. python3 -m repo_harness_creator audit --target . --min-score 85` | pass | Self-harness scored `100/100`. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 43 tests, pin check, self-audit. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 43 tests, pin check, self-audit. |
| 2026-06-14 | Research refresh | `python3 scripts/refresh_research.py --root .` | pass | 46 sources checked; OpenAI and Red Hat 403 failures recorded in the lock file. |
| 2026-06-14 | Generated harness smoke | isolated `repo_harness_creator init` into a temp target | pass | Generated `AGENTS.md`; generated research source file contains 46 sources. |
| 2026-06-14 | Diff hygiene | `git diff --check` | pass | No whitespace errors. |
| 2026-06-14 | Local unit tests | `PYTHONPATH=src:. python3 -m unittest discover -s tests` | pass | 38 tests after README-source parser, research-ledger, Action manifest, and AGENTS section-contract additions. |
| 2026-06-14 | Pin enforcement | `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` | pass | Package build pins and external Action SHAs validated. |
| 2026-06-14 | Self-audit | `PYTHONPATH=src:. python3 -m repo_harness_creator audit --target . --min-score 85` | pass | Self-harness scored `100/100`. |
| 2026-06-14 | Diff hygiene | `git diff --check` | pass | No whitespace errors. |
| 2026-06-14 | POSIX verification | `./init.sh` | pass | Doctor, compile, 38 tests, pin check, self-audit. |
| 2026-06-14 | PowerShell verification | `pwsh -NoProfile -File ./init.ps1` | pass | Doctor, compile, 38 tests, pin check, self-audit. |
| 2026-06-14 | GitHub Action manifest | `PYTHONPATH=src:. python3 -m unittest tests.test_github_action` | pass | Added regression coverage for quoted Action descriptions containing colons after hosted CI rejected the manifest. |
| 2026-06-14 | AGENTS section contract | `PYTHONPATH=src:. python3 -m unittest tests.test_generate_audit` | pass | Root, template, and generated `AGENTS.md` use the required five-section format. |
| 2026-06-14 | Package install smoke | isolated venv install, generated target init, and target audit | pass | Installed CLI returned version `0.1.0`; generated component inventory and 32-source research starter files were present. |
| 2026-06-14 | Generated harness smoke | `repo_harness_creator init` into isolated temp target | pass | Generated starter research source file contains 44 tracked sources. |
| 2026-06-14 | Source research | AGY plus local source pass | pass | Reviewed Bluepeak, JobSentinel, persona, pi-harness, Walking Labs, and JobSentinel source inventory. |
| 2026-06-14 | README research | GitHub Docs, The Turing Way, OpenSSF Scorecard, and exemplar README pass | pass | Root README rewritten as a project landing page with quick start, trust model, Action usage, verification, and source provenance. |
| 2026-06-14 | Research refresh | `python3 scripts/refresh_research.py --root .` | pass | 44 sources checked; one Red Hat 403 recorded in the lock file. |

Rules:

- Record command name, scope, result, and risk.
- Do not paste secrets, local absolute paths, or long command output.
- Prefer one current row per meaningful verification event.
