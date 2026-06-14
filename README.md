# HarnessForge

<p align="center">
  <img src="docs/assets/logo.png" alt="HarnessForge logo" width="180">
</p>

[![CI](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Create, audit, and maintain repo-owned harnesses for AI coding agents.

A harness is the operating layer that helps an agent understand a repository:
instructions, project state, verification commands, source evidence, security
boundaries, and handoff rules. HarnessForge gives teams a practical
way to add that layer to any project without turning one instruction file into
a long manual.

This repository is both:

- a Python CLI: `harnessforge`
- a reusable composite GitHub Action: `cboyd0319/harnessforge`

The goal is simple: make good agent behavior easier to get, easier to inspect,
and easier to keep current across macOS, Windows, and Linux.

## Current Status

This is an early implementation with a usable local CLI and Action. The audit is
structural: it checks that the harness exists, is coherent, and has the expected
operational surfaces. It does not prove that a specific agent will complete a
specific project task correctly without real task runs and review.

## Why Use It

- Start faster: generate the files agents need to orient in a repo.
- Stay safer: preserve existing files by default and reject unsafe generated
  paths.
- Keep state durable: create explicit progress, feature, evidence, and handoff
  surfaces.
- Verify consistently: install one local check path for humans, agents, and CI.
- Support common agent entry points: generated harnesses use `AGENTS.md`, and
  this repo also includes Claude, Gemini, and GitHub Copilot compatibility files
  that route back to the same operating model.
- Keep research visible: record source URLs, refresh metadata, and unresolved
  research items in the harness itself.

## Platform Contract

| Surface | Contract |
| --- | --- |
| Python | 3.13 or newer |
| macOS | 15 or newer |
| Windows | Windows 11 or newer |
| Linux | Ubuntu 22.04 or newer as the explicit floor |
| Runtime dependencies | Python standard library only |
| Build backend | `setuptools==82.0.1`, hard pinned |
| CI coverage | Push/PR: Ubuntu 22.04 on Python 3.13.14. Manual platform check: macOS 15 and `windows-2025-vs2026` on Python 3.13.14 |

Other modern Linux distributions should work when Python 3.13+ is available.
They are not the stated support floor until they are covered by CI or equivalent
contract tests.

## Install From A Clone

```bash
git clone https://github.com/cboyd0319/harnessforge.git
cd harnessforge
python -m pip install --editable .
harnessforge --help
```

## Create A Harness

Preview the files first:

```bash
harnessforge init --target /path/to/repo --dry-run
```

Write missing files:

```bash
harnessforge init --target /path/to/repo
```

Opt into reviewed workflow scaffolds only when wanted:

```bash
harnessforge init --target /path/to/repo --with-ci-workflow
harnessforge init --target /path/to/repo --with-self-heal-workflow
```

By default, `init` only writes missing generated files. It does not overwrite
existing project files. Use `--force` only when replacing generated harness
surfaces is intentional and reviewed.
Workflow scaffolds use manual triggers by default and must be reviewed and
pinned before relying on them.

The generated harness includes:

| Area | Key files |
| --- | --- |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` |
| Project state | `feature_list.json`, `progress.md`, `session-handoff.md` |
| Local checks | `init.sh`, `init.ps1`, `scripts/check_pins.py` |
| Harness docs | `docs/harness/README.md`, `verification-matrix.md`, `change-contract.md` |
| Security and privacy | `security-boundary-map.md`, `feature-privacy-labels.json` |
| Evidence and quality | `evidence-log.md`, `quality-document.md`, `release-controls.md`, `evaluator-rubric.md` |
| Research | `sources.md`, `research-sources.json`, `research-inbox.md` |
| Lifecycle | `self-healing.md`, `entropy-control.md`, `clean-state-checklist.md` |

See [docs/harness/manifest.json](docs/harness/manifest.json) for the complete
generated inventory and required-file contract.

## Audit A Harness

```bash
harnessforge audit --target /path/to/repo
harnessforge audit --target /path/to/repo --json
harnessforge audit --target /path/to/repo --html harness-report.html
harnessforge audit --target /path/to/repo --min-score 85
```

The audit returns:

- an overall 0-100 score
- the lowest-scoring harness domain
- failed checks
- concrete recommendations

The score covers structure, portability, source hygiene, state surfaces,
verification coverage, security boundaries, and lifecycle controls. Treat it as
a readiness signal, not a substitute for code review or real task evaluation.

## Apply Safe Corrections

```bash
harnessforge update --target /path/to/repo
harnessforge update --target /path/to/repo --apply
```

`update` is conservative. Without `--apply`, it reports what it would change.
With `--apply`, it creates missing generated artifacts. Existing files are left
alone unless `--force` is also provided.

## Use The GitHub Action

```yaml
name: Harness Audit

on:
  pull_request:
  push:

permissions:
  contents: read

jobs:
  harness:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6
        with:
          persist-credentials: false
      - uses: cboyd0319/harnessforge@<reviewed-commit-sha>
        with:
          command: audit
          min-score: "85"
          html-report: harness-report.html
          json-report: harness-report.json
```

For production workflows, pin this Action and other third-party Actions to a
reviewed full-length commit SHA. See [docs/action.md](docs/action.md) for every
input, output, and update mode.

## Command Reference

| Command | Purpose |
| --- | --- |
| `harnessforge init` | Create missing harness artifacts |
| `harnessforge audit` | Score an existing repo harness |
| `harnessforge update` | Plan or apply safe missing-file corrections |
| `harnessforge doctor` | Check local runtime support |

Run `harnessforge <command> --help` for command-specific options.

## Security Model

People may run this tool on personal machines and private repositories, so the
default posture is intentionally restrictive. See [SECURITY.md](SECURITY.md)
for vulnerability reporting, scope, and severity guidance.

- Normal `init`, `audit`, `update`, and `doctor` commands use the Python
  standard library and do not install runtime dependencies.
- Existing files are preserved unless `--force` is explicitly supplied.
- Generated destination paths are preflighted before writes.
- Absolute instruction paths, traversal, and unsafe instruction filenames are
  rejected.
- Symlinked directories are skipped during discovery.
- Root manifest symlinks that resolve outside the target repository are ignored
  during project detection.
- Audit reads known files only when they resolve inside the target repository.
- Local home paths are redacted from durable output.
- GitHub Action outputs use GitHub environment-file delimiter blocks instead
  of flattening line breaks before writing to `$GITHUB_OUTPUT`.
- GitHub Action report paths must be relative in both POSIX and Windows syntax
  and stay inside the target repository.
- GitHub Action report outputs use target-relative forward-slash paths on every
  runner.
- The composite Action sets `PYTHONSAFEPATH=1` so the caller repository's
  working directory cannot shadow the Action library at Python startup.
- Generated harnesses preserve intentionally vulnerable training, demo, or
  fixture code unless remediation is explicitly in scope.
- Material AI/RAG/agent, tool, external-service, auth, secret, data-flow, or
  deployment changes require updated boundary/threat model evidence and focused
  checks.

Network access is limited to explicit research-refresh workflows and normal
GitHub Actions setup behavior, not routine local harness generation. Research
refresh reads only the checked-in fixed allowlist in
`docs/harness/research-sources.json`; it does not search the web, discover
latest research, or follow unreviewed source expansion. It accepts default-port
HTTPS public-source URLs only; local files, credentials, localhost,
private-address targets, private DNS resolutions, and unsafe redirects are
rejected. Connections are opened to validated public DNS results while
preserving the original host for TLS verification.

## Self-Healing

This repo includes a scheduled self-healing workflow in
[.github/workflows/harness-self-heal.yml](.github/workflows/harness-self-heal.yml).
It refreshes research metadata, applies only safe harness updates, runs
verification, and opens a pull request when changes are detected. It does not
silently mutate `main`. Fetched titles, headings, and hashes are treated as
untrusted metadata for human review, not executable instructions. Metadata that
resembles prompt injection, indirect prompt injection, data poisoning,
credential-exfiltration instructions, invisible Unicode, or Markdown/HTML
exfiltration markers is withheld from durable output and recorded as review
signals.

Research sources are tracked in:

- [docs/harness/sources.md](docs/harness/sources.md)
- [docs/harness/research-sources.json](docs/harness/research-sources.json)
- [docs/harness/research-sources.lock.json](docs/harness/research-sources.lock.json)
- [docs/harness/research-inbox.md](docs/harness/research-inbox.md)

## Verify This Repository

On macOS or Linux:

```bash
./init.sh
```

On Windows:

```powershell
.\init.ps1
```

The local harness check runs the package doctor, bytecode compilation, unit
tests, pin checks, and a self-audit.

Prefer local checks and local commits during active work. Push only at an
explicit batch boundary, release point, or user request because remote CI has
real cost.

The default push/PR CI path runs Ubuntu 22.04 with Python 3.13.14. Use the
manual `workflow_dispatch` CI run for macOS and Windows platform confirmation
at release or risk-based checkpoints.

For focused checks:

```bash
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python scripts/check_pins.py --root .
PYTHONPATH=src python -m harnessforge audit --target . --min-score 85
```

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/harnessforge/` | CLI, generator, auditor, updater, Action entry point |
| `src/harnessforge/templates/` | Files copied into target repositories |
| `docs/harness/` | This repo's own harness and research ledger |
| `tests/` | Unit and regression tests |
| `scripts/check_pins.py` | Hard-pin policy check |
| `scripts/refresh_research.py` | Research metadata refresh |
| `action.yml` | Composite GitHub Action metadata |

## Contributing

Keep changes small, reviewed, and source-backed. See
[CONTRIBUTING.md](CONTRIBUTING.md) for PR expectations, sign-off guidance,
prior-art attribution, and AI-assisted contribution rules.

Before opening a pull request:

```bash
./init.sh
git diff --check
```

For dependency, workflow, platform, security, or harness-template changes, also
update the relevant evidence in [docs/harness/evidence-log.md](docs/harness/evidence-log.md)
and source records in [docs/harness/sources.md](docs/harness/sources.md).

## License

MIT. See [LICENSE](LICENSE).
