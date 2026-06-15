# HarnessForge

<p align="center">
  <img src="docs/assets/logo.png" alt="HarnessForge logo" width="180">
</p>

[![CI](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Give AI coding agents a real repo harness, not just another prompt.

HarnessForge creates the operating layer an agent needs before it can work well
inside a repository: concise instructions, detected project context, verification
commands, durable state, source-of-truth routing, security boundaries, and
handoff rules. It turns agent readiness from scattered tribal knowledge into a
reviewable product surface that lives with the code.

The important design choice is the boundary. HarnessForge generates portable
harness infrastructure, detects repo-local systems, and routes agents toward the
right source of truth. It does not copy one repo's personal preferences, local
research habits, or workflow engines into another project.

This repository ships two related surfaces:

- `harnessforge`, a Python CLI for local generation, inspection, audit, and
  maintenance.
- `cboyd0319/harnessforge`, a composite GitHub Action that runs the same
  library code in CI.

## At A Glance

| Need | HarnessForge answer |
| --- | --- |
| Help agents orient in a repo | Generate compact instruction routers and durable project state |
| Avoid overwriting local work | Preserve existing files by default and track generated ownership |
| Know whether a repo is ready | Run read-only readiness and sync preflight checks |
| Keep generated harnesses honest | Audit structure, drift, security boundaries, and lifecycle controls |
| Respect existing spec systems | Detect `.specify`, `specs/`, `aspec/`, work-item templates, and workflow surfaces |
| Run the same checks in CI | Use the composite GitHub Action backed by the same Python library |

## Status

HarnessForge is usable for local harness generation and structural assessment.
It is still pre-`v1`.

The core loop is already useful: inspect a repo, preview a harness, create
missing files, audit the result, and keep drift visible over time. The audit
score is structural. It checks whether a harness is coherent, portable,
reviewable, and wired to useful feedback loops. It does not prove that a
specific agent will complete a specific project task correctly. Real agent
effectiveness still needs representative task runs and human review.

## What Makes It Different

- It treats agent readiness as repository infrastructure, not a one-off prompt.
- It separates generated harness files from repo-local instructions and
  preferences.
- It improves existing instruction surfaces without taking ownership away from
  the project.
- It detects source-of-truth systems before generating guidance, including
  Spec Kit-style SDD, ASPEC-style folders, work items, and workflow definitions.
- It gives humans and CI the same read-only readiness signal through
  `sync --check`.
- It keeps the default runtime boring: Python standard library, explicit file
  writes, pinned build tooling, and no network access for normal generation.

## Core Capabilities

- Detects repository shape, stacks, package managers, verification commands,
  monorepo markers, source-of-truth docs, Spec Kit-style SDD surfaces,
  ASPEC-style folders, work-item templates, and workflow control surfaces.
- Provides a read-only guided first-run summary that explains detected context,
  readiness, preserved files, planned generated files, review placeholders, and
  next commands.
- Generates a compact harness with agent entrypoints, project state files,
  local verification scripts, security boundaries, evidence docs, lifecycle
  docs, and a manifest.
- Preserves existing files by default.
- Can append a reviewed HarnessForge quality addendum to existing instruction
  files with `--enhance-existing`.
- Audits harness structure and reports actionable failures.
- Reports generated-file drift and static readiness without running target
  project commands.
- Provides a composite GitHub Action for audit, init, update, and doctor
  workflows.

## Default Boundaries

- It does not overwrite existing project files unless `--force` is supplied.
- It does not generate user-specific research mandates, local tool
  preferences, MCP configs, memory trees, or platform permission files.
- It does not install Spec Kit, `.specify`, slash commands, presets,
  extensions, catalogs, ASPEC, AWMAN, Maki, or workflow engines into target
  repositories.
- It does not create autonomous push, PR, self-heal, setup, or teardown
  workflows unless optional workflow scaffolds are explicitly requested.
- It does not run target repository commands during `inspect`, `sync --check`,
  `audit`, or `update --drift-report`.
- It does not use structural scores as proof of real task performance.

## Platform Contract

| Surface | Contract |
| --- | --- |
| Python | 3.13 or newer |
| macOS | 15 or newer |
| Windows | Windows 11 or newer |
| Linux | Ubuntu 22.04 or newer as the explicit floor |
| Runtime dependencies | Python standard library only |
| Build backend | `setuptools==82.0.1`, hard pinned |
| Push/PR CI | Ubuntu 22.04 on Python 3.13.14 |
| Manual platform CI | macOS 15 and `windows-2025-vs2026` on Python 3.13.14 |

Other modern Linux distributions should work when Python 3.13+ is available.
They are not the stated support floor until covered by CI or equivalent
contract tests.

## Install

From a clone:

```bash
git clone https://github.com/cboyd0319/harnessforge.git
cd harnessforge
python -m pip install --editable .
harnessforge --help
```

For local development without installing:

```bash
PYTHONPATH=src python -m harnessforge --help
```

## Quick Start

The normal flow is guide, inspect as needed, preview, generate, audit:

Run the guided first-run summary before writing anything:

```bash
harnessforge quickstart --target /path/to/repo
```

It reports detected project context, readiness, source-of-truth systems,
preserved existing files, planned generated files, generated review
placeholders, and the safest next commands.

Inspect a repository before writing anything:

```bash
harnessforge inspect --target /path/to/repo
harnessforge inspect --target /path/to/repo --json
```

Run the read-only readiness report:

```bash
harnessforge inspect --target /path/to/repo --readiness
harnessforge inspect --target /path/to/repo --readiness --json
```

Run the CI-oriented sync preflight:

```bash
harnessforge sync --check --target /path/to/repo
harnessforge sync --check --target /path/to/repo --json
```

Preview generated files:

```bash
harnessforge init --target /path/to/repo --dry-run
```

Create missing harness files:

```bash
harnessforge init --target /path/to/repo
```

Audit the result:

```bash
harnessforge audit --target /path/to/repo --min-score 85
```

## Readiness And Sync

`inspect --readiness` and `sync --check` are static and read-only. They do not
run target repository commands and do not write files.

Readiness reports:

- `verdict`: `ready`, `warning`, or `blocked`
- `blockedReasons`
- `warnings`
- `nextActions`
- `sourceOfTruth`
- `runnableChecks`
- `generatedDrift`
- `reviewRequired`
- `workflowInventory`
- `workItemInventory`
- `contextBudget`
- `governanceInventory`

`sync --check` wraps the same readiness report in a CI-friendly command with
stable exit codes:

| Verdict | Exit code | Meaning |
| --- | ---: | --- |
| `ready` | 0 | No blockers, warnings, review-required surfaces, or generated drift were detected |
| `warning` | 1 | The repo can be inspected, but drift or review-required surfaces need human attention |
| `blocked` | 2 | HarnessForge could not identify a safe verification path or another blocking condition exists |

For spec-driven repos, readiness also reports static quality gaps such as
unresolved clarification markers, incomplete requirement checklists, missing
plan/task artifacts, weak FR/SC traceability, tasks without explicit file
paths, and workflow surfaces that need review.

Workflow inventory is advisory. It detects `.github/workflows/`,
`aspec/workflows/`, and `workflows/` TOML/YAML files, then reports visible
setup, teardown, remediation, push, pull-request, CI polling, and credential
surfaces. Work-item inventory reports templates and concrete work-item files
without adopting ASPEC or AWMAN formats as generated defaults.

Context budget is also advisory. It reports instruction-file size and repeated
instruction blocks across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot
instructions so teams can keep router files compact and avoid wasting agent
context on duplicated guidance.

Governance inventory is advisory as well. It reports MCP configs, agent
settings, hooks, devcontainers, sandbox configs, agent setup workflows, and
environment template or local env files as review surfaces without reading or
exposing secret values.

## Planned Verify JSON Contract

HarnessForge has a proposed `verify --json` report contract for project check
results. The contract is documented before command execution is implemented so
the schema, safety boundary, and CI semantics can be reviewed independently.

See [docs/harness/verify-json-contract.md](docs/harness/verify-json-contract.md),
[docs/harness/verify-json.schema.json](docs/harness/verify-json.schema.json),
and [docs/harness/verify-json-example.json](docs/harness/verify-json-example.json).

The intended default mode is plan-only: report detected checks and their
sources without running target repository commands. Future execution must be
explicit opt-in.

## Generation Boundary

`init` creates missing HarnessForge-owned files. It preserves existing project
files by default:

```bash
harnessforge init --target /path/to/repo
```

Use `--dry-run` first when reviewing a new target:

```bash
harnessforge init --target /path/to/repo --dry-run
```

Use `--enhance-existing` when an existing instruction file should keep its
project text but receive a reviewed HarnessForge quality addendum:

```bash
harnessforge init --target /path/to/repo --enhance-existing
```

Use `--force` only after reviewing the target diff:

```bash
harnessforge init --target /path/to/repo --force
```

Optional workflow scaffolds are off by default:

```bash
harnessforge init --target /path/to/repo --with-ci-workflow
harnessforge init --target /path/to/repo --with-self-heal-workflow
```

Those workflows use manual triggers and placeholder Action pins. Review their
permissions, triggers, branches, credential surfaces, and full-length commit
SHAs before relying on them.

## Generated Files

The default generated harness includes:

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

Each generated file is recorded in `docs/harness/manifest.json` with ownership
metadata and hashes. Project-owned existing files are tracked separately so
drift reporting can distinguish generated changes from preserved local content.

See [docs/harness/manifest.json](docs/harness/manifest.json) for this repo's
current generated inventory and required-file contract.

## Audit

```bash
harnessforge audit --target /path/to/repo
harnessforge audit --target /path/to/repo --json
harnessforge audit --target /path/to/repo --html harness-report.html
harnessforge audit --target /path/to/repo --min-score 85
```

The audit returns:

- an overall 0-100 score
- the bottleneck domain
- per-domain checks
- failed checks
- concrete recommendations

The score covers instructions, tools, environment, state, feedback, scope, and
lifecycle controls. Treat it as a harness quality signal, not as a substitute
for code review, security review, or real agent task evaluation.

## Update And Drift

Plan safe missing-file corrections without writing:

```bash
harnessforge update --target /path/to/repo
```

Apply safe missing-file corrections:

```bash
harnessforge update --target /path/to/repo --apply
```

Report generated-file drift:

```bash
harnessforge update --target /path/to/repo --drift-report
harnessforge update --target /path/to/repo --drift-report --json
```

`update --apply` creates missing generated artifacts. Existing files are left
alone unless `--force` is supplied.

## GitHub Action

Minimal audit workflow:

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

For production workflows, pin this Action and third-party Actions to reviewed
full-length commit SHAs. See [docs/action.md](docs/action.md) for every Action
input, output, and command mode.

## Command Reference

| Command | Purpose |
| --- | --- |
| `harnessforge quickstart` | Guide the first safe run without writing files |
| `harnessforge inspect` | Show detected project profile or readiness without writing files |
| `harnessforge sync --check` | Run a read-only CI preflight with readiness exit codes |
| `harnessforge init` | Create missing harness artifacts |
| `harnessforge audit` | Score an existing repo harness |
| `harnessforge update` | Plan or apply safe missing-file corrections, or report generated drift |
| `harnessforge doctor` | Check local runtime support |

Run `harnessforge <command> --help` for command-specific options.

## Security Model

People may run this tool on personal machines and private repositories, so the
default posture is intentionally restrictive. See [SECURITY.md](SECURITY.md)
for vulnerability reporting, scope, and severity guidance.

- Normal `init`, `inspect`, `sync --check`, `audit`, `update`, and `doctor`
  commands use the Python standard library and do not install runtime
  dependencies.
- Existing files are preserved unless `--force` is explicitly supplied.
- `--enhance-existing` appends reviewed instruction addenda without replacing
  existing project text.
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

## Self-Healing In This Repo

This repository has its own local maintenance workflows. Those workflows are
repo-local and are not the same thing as the generated harness for other
repositories.

The scheduled workflow in
[.github/workflows/harness-self-heal.yml](.github/workflows/harness-self-heal.yml)
refreshes research metadata, applies only safe harness updates, runs
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

Focused checks:

```bash
PYTHONPATH=src:. python -m unittest discover -s tests
PYTHONPATH=src:. python scripts/check_pins.py --root .
PYTHONPATH=src:. python -m harnessforge audit --target . --min-score 85
PYTHONPATH=src:. python -m harnessforge sync --check --target . --json
```

The final command currently returns warning exit code `1` in this repository
because local instruction files need review. That is expected and not a
readiness blocker.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/harnessforge/` | CLI, generator, auditor, updater, readiness checks, Action entry point |
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
