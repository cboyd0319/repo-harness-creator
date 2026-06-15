# HarnessForge

<p align="center">
  <img src="docs/assets/logo.png" alt="HarnessForge logo" width="180">
</p>

[![CI](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Give AI coding agents a real repo harness, not just another prompt.

HarnessForge creates the operating layer an agent needs before it can work well
inside a repository: concise instructions, detected project context,
verification commands, durable state, source-of-truth routing, security
boundaries, and handoff rules. It turns agent readiness from scattered tribal
knowledge into a reviewable product surface that lives with the code.

The important design choice is the boundary. HarnessForge generates portable
harness infrastructure, detects repo-local systems, and routes agents toward the
right source of truth. It does not copy one repo's personal preferences, local
research habits, or workflow engines into another project.

This repository ships two related surfaces:

- `harnessforge`, a Python CLI for local generation, inspection, audit, and
  maintenance.
- `cboyd0319/harnessforge`, a composite GitHub Action that runs the same
  library code in CI.

## Start Here

| Need | Go to |
| --- | --- |
| Install the CLI or verify this repo | [Installation](docs/installation.md) |
| Run HarnessForge against a repository | [Usage](docs/usage.md) |
| Understand what it creates and does not create | [Capabilities](docs/capabilities.md) |
| See accepted improvements and build order | [Roadmap](docs/roadmap.md) |
| Use the composite GitHub Action | [GitHub Action](docs/action.md) |
| Understand this repo's own harness | [Harness operations](docs/harness/README.md) |
| Report a vulnerability | [Security](SECURITY.md) |
| Contribute changes | [Contributing](CONTRIBUTING.md) |

## At A Glance

| Need | HarnessForge answer |
| --- | --- |
| Help agents orient in a repo | Generate compact instruction routers and durable project state |
| Avoid overwriting local work | Preserve existing files by default and track generated ownership |
| Know whether a repo is ready | Run read-only readiness and sync preflight checks |
| Review harness health in one place | Compose readiness, audit, drift, index, and evidence into one report |
| Keep generated harnesses honest | Audit structure, drift, security boundaries, and lifecycle controls |
| Respect existing spec systems | Detect `.specify`, `specs/`, `aspec/`, work-item templates, and workflow surfaces |
| Build deeper project operating models | Apply optional blueprints for agentic apps, SDD, web services, data/ML, security, and automation |
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

## Why It Is Different

- It treats agent readiness as repository infrastructure, not a one-off prompt.
- It separates generated harness files from repo-local instructions and
  preferences.
- It improves existing instruction surfaces without taking ownership away from
  the project.
- It detects source-of-truth systems before generating guidance, including
  Spec Kit-style SDD, ASPEC-style folders, work items, and workflow definitions.
- It gives humans and CI the same read-only readiness signal through
  `sync --check`.
- It can produce one unified read-only report for review or release evidence
  without running target commands.
- It keeps the default runtime boring: Python standard library, explicit file
  writes, pinned build tooling, and no network access for normal generation.

## Quick Start

Install from a clone:

```bash
git clone https://github.com/cboyd0319/harnessforge.git
cd harnessforge
python -m pip install --editable .
harnessforge --help
```

Run the guided first-run summary before writing anything:

```bash
harnessforge quickstart --target /path/to/repo
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

Create one review artifact:

```bash
harnessforge report --target /path/to/repo --markdown-report docs/harness/evidence/report.md
```

See [Usage](docs/usage.md) for readiness checks, repo indexing, verification
plans, unified reports, explicit verify runs, `harnessforge update` drift
workflows, blueprints, and CI preflight.

## Core Surfaces

| Surface | Purpose |
| --- | --- |
| `quickstart` | Guided first run without writing files |
| `inspect` | Repository detection and static readiness |
| `index` | Read-only structural map for large existing repos |
| `session` | Restart snapshot with git, readiness, audit, and state-file status |
| `report` | Unified read-only harness status report with optional JSON and Markdown outputs |
| `plan` | Diff-aware verification planning without command execution |
| `sync --check` | CI-oriented readiness preflight with stable exit codes |
| `verify` | Planned project checks by default, explicit execution with `--run` |
| `blueprint` | Optional review-required operating-model overlays |
| `init` | Create missing harness artifacts |
| `audit` | Score an existing repo harness |
| `update` | Plan or apply safe missing-file corrections and report drift |
| `doctor` | Check local runtime support |

Run `harnessforge <command> --help` for command-specific options.

## Default Boundaries

- Existing files are preserved unless `--force` is supplied.
- Normal generation does not install dependencies, search the web, run target
  project commands, or create autonomous workflows.
- User-specific research mandates, local tool preferences, MCP configs, memory
  trees, and platform permission files are not generated into target repos.
- Optional blueprints and workflow scaffolds are explicit opt-ins.
- Structural audit scores are not treated as real-agent performance evidence.

See [Capabilities](docs/capabilities.md) for the full generated-file inventory,
security model, and repo-local maintenance boundaries.

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
tests, pin checks, research source checks, and a self-audit. More focused
verification commands are in [Installation](docs/installation.md).

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/harnessforge/` | CLI, generator, auditor, updater, indexer, readiness checks, Action entry point |
| `src/harnessforge/templates/` | Files copied into target repositories |
| `docs/` | User docs, Action docs, and this repo's own harness |
| `tests/` | Unit and regression tests |
| `scripts/check_pins.py` | Hard-pin policy check |
| `scripts/refresh_research.py` | No-network research ledger check and explicit metadata refresh |
| `action.yml` | Composite GitHub Action metadata |

## License

MIT. See [LICENSE](LICENSE).
