# Evidence Log

Use this for compact current evidence. Keep raw logs out of this file.

| Date | Scope | Command Or Review | Result | Notes |
| --- | --- | --- | --- | --- |
| 2026-06-14 | Root hardening pass | Current-source review against Python Packaging User Guide, Python command-line docs, and GitHub Actions secure-use docs | pass | Added `license-files`, `PYTHONSAFEPATH=1`, root-manifest symlink escape protection, broader home-path redaction, public-HTTPS-only research refresh, and target-contained Action report paths. |
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
