# HarnessForge

<p align="center">
  <img src="docs/assets/logo.png" alt="HarnessForge logo" width="180">
</p>

[![CI](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cboyd0319/harnessforge/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> [!CAUTION]
> # ALPHA / PRE-RELEASE PROJECT
>
> HarnessForge has not been deployed and has no external users yet. CLI
> contracts, generated file layouts, report schemas, GitHub Action behavior,
> and docs may change without backward-compatibility guarantees until
> maintainers declare an explicit release boundary.

Give AI coding agents a real repo harness, not just another prompt.

## What This Is

HarnessForge is a Python 3.13+ CLI and composite GitHub Action for creating,
assessing, and safely updating AI coding-agent harnesses in existing
repositories.

A good harness is the operating layer around the model: instructions, tools,
environment, state, and feedback. HarnessForge turns that layer into files a
repo can review, version, test, and improve. It generates compact agent
instructions, detects project context, routes agents to source-of-truth docs,
records durable state, declares verification commands, and captures security
and workflow boundaries.

This repo ships two related surfaces:

- `harnessforge`, the local CLI for generation, inspection, audit, reporting,
  release evidence, and maintenance.
- `cboyd0319/harnessforge`, a composite GitHub Action that runs the same Python
  library in CI.

## Why You Want It

AI coding agents often fail because they start with too little repo context,
unclear verification, stale docs, and no durable handoff path. The result is
expensive context burn, repeated rediscovery, accidental edits to the wrong
files, and reviews that have to reconstruct what the agent thought it was
doing.

HarnessForge gives a repo an explicit agent operating model:

- New agents get a clear startup route instead of hunting through random docs.
- Existing `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot instructions can
  be reviewed and improved without taking ownership away from the project.
- Verification commands, state files, evidence docs, and first-agent review
  tasks live with the code instead of in chat history.
- Large or unfamiliar repos get structural indexing, source-of-truth routing,
  workflow inventory, and review-required surface detection before writes.
- Maintainers can inspect harness drift, readiness, maturity, and release
  evidence with read-only commands before trusting generated changes.

## What Makes It Cool

- It treats agent readiness as real repository infrastructure, not prompt
  decoration.
- It keeps product boundaries explicit: this repo's local harness, generated
  target harnesses, and the GitHub Action are separate surfaces.
- It respects existing project systems. It detects specs, work items, ASPEC
  style folders, workflow definitions, verification commands, SBOM evidence,
  and source-of-truth docs before generating guidance.
- It creates a zero-install repo skill at `.agents/skills/harness/SKILL.md`, so
  future agents can improve the harness using repo-owned guidance even when
  HarnessForge is not installed.
- It adds a first-agent harness improvement task so the first agent session can
  deepen the generated harness with repo-specific knowledge.
- It can produce one `harnessforge report` artifact with readiness, audit,
  generated drift, repo map, instruction quality, review work, verify evidence,
  effectiveness evidence, policy recommendations, skill wiring, and maturity.
- It can prepare release evidence with `harnessforge release-check` without
  publishing, tagging, uploading, pushing, or running target project commands.
- It has an offline public-repo `corpus` quality gate that tests generated
  content against realistic fixture shapes without cloning public repos.
- The GitHub Action gives CI the same core library behavior as the local CLI
  instead of duplicating product logic in workflow shell.
- It keeps safety boring by default: explicit writes, no networked generation,
  no autonomous target workflows, and structural scores kept separate from
  real-agent performance claims.

## Product Boundary

HarnessForge generates portable harness infrastructure, detects repo-local
systems, and routes agents toward the right source of truth. It does not copy
one repo's personal preferences, local research habits, self-healing workflow,
MCP setup, memory tree, or platform permission files into another project.

Generated target repos should treat HarnessForge as an optional owner tool
after initial generation unless the repo owner explicitly adopts the CLI or
GitHub Action as a maintenance gate.

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

## Status

HarnessForge is usable for local harness generation, existing-instruction
review, structural assessment, reporting, and release evidence assembly. It is
still pre-`v1`.

The core loop is already useful: inspect a repo, preview a harness, create
missing files, audit the result, and keep drift visible over time. The audit
score is structural. It checks whether a harness is coherent, portable,
reviewable, and wired to useful feedback loops. It does not prove that a
specific agent will complete a specific project task correctly. Real agent
effectiveness still needs representative task runs and human review.

## Quick Start

Install from a clone, then run `harnessforge --help`. See
[Installation](docs/installation.md) for exact setup commands.

Run the guided first-run summary before writing anything:

```bash
harnessforge quickstart --target /path/to/repo
```

Preview generated files:

```bash
harnessforge init --target /path/to/repo --dry-run
```

Review existing instruction files without writing:

```bash
harnessforge enhance --target /path/to/repo
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

Prepare release evidence:

```bash
harnessforge release-check --target /path/to/repo --markdown-report docs/harness/evidence/release-check.md
```

Plan legacy state consolidation:

```bash
harnessforge migrate-state --target /path/to/repo
```

See [Usage](docs/usage.md) for readiness checks, repo indexing,
existing-instruction review, verification plans, unified reports, explicit
verify runs, `harnessforge update` drift workflows, blueprints, and CI
preflight.

## Core Surfaces

| Surface | Purpose |
| --- | --- |
| `quickstart` | Guided first run without writing files |
| `inspect` | Repository detection and static readiness |
| `index` | Read-only structural map for large existing repos |
| `session` | Restart snapshot with git, readiness, audit, and state-file status |
| `report` | Unified read-only harness status and maturity report with optional JSON and Markdown outputs |
| `release-check` | Read-only release readiness and maturity gate over existing harness evidence |
| `finalize-review` | Explicit first-agent review finalization and high-risk acceptance evidence |
| `migrate-state` | Dry-run or explicitly apply migration from split root state files into `current-state.md` |
| `enhance` | Review existing instruction files without writing files |
| `plan` | Diff-aware verification planning without command execution |
| `sync --check` | CI-oriented readiness preflight with stable exit codes |
| `verify` | Planned project checks by default, explicit execution with `--run` |
| `blueprint` | Optional review-required operating-model overlays |
| `corpus` | Offline public-repo fixture quality gate for generated content |
| `init` | Create missing harness artifacts |
| `audit` | Score an existing repo harness |
| `update` | Plan or apply safe missing-file corrections and report drift |
| `doctor` | Check local runtime support |

Run `harnessforge <command> --help` for command-specific options.

## Default Boundaries

- Existing files are preserved unless `--force` is supplied.
- Destructive, overwrite-capable, apply-mode, or command-executing CLI
  operations warn and require confirmation. In non-interactive runs, pass
  `--yes` intentionally.
- Normal generation does not install dependencies, search the web, run target
  project commands, or create autonomous workflows.
- User-specific research mandates, local tool preferences, MCP configs, memory
  trees, and platform permission files are not generated into target repos.
- Optional blueprints and the generated CI workflow scaffold are explicit
  opt-ins.
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
