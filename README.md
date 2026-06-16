# HarnessForge

<p align="center">
  <img src="docs/assets/logo.png" alt="HarnessForge logo" width="180">
</p>

[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> [!CAUTION]
> # ALPHA / PRE-RELEASE PROJECT
>
> HarnessForge has not been deployed and has no external users yet. CLI
> contracts, generated file layouts, report schemas, GitHub Action behavior,
> and docs may change without backward-compatibility guarantees until
> maintainers declare an explicit release boundary. Automatic GitHub Actions
> workflows are disabled during alpha to avoid runner cost while commits are
> frequent.

Give AI coding agents a real repo harness, not just another prompt.

## What This Is

HarnessForge is a Python 3.13+ CLI and composite GitHub Action for creating,
assessing, and safely updating AI coding-agent harnesses in existing
repositories.

A good harness is the operating layer around the model: instructions, tools,
environment, state, and feedback. HarnessForge turns that layer into repo-owned
files an agent can read and a maintainer can review, version, test, and improve.

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
- Verification commands, state files, evidence docs, and first-agent review
  tasks live with the code instead of in chat history.
- Large or unfamiliar repos get structural indexing, source-of-truth routing,
  workflow inventory, and review-required surface detection before writes.
- Maintainers can inspect drift, readiness, maturity, and release evidence with
  read-only commands before trusting generated changes.

## What Makes It Cool

- It treats agent readiness as real repository infrastructure, not prompt
  decoration.
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

## Boundaries

This repo's local harness, generated target harnesses, optional generated
workflows, and the GitHub Action are separate product surfaces. HarnessForge
does not copy this repo's self-healing workflow, personal research preferences,
MCP setup, memory tree, local paths, or platform permission files into target
repos.

Existing files are preserved unless `--force` is supplied. Destructive,
overwrite-capable, apply-mode, or command-executing CLI operations warn and
require confirmation; in non-interactive runs, pass `--yes` intentionally.
Generated target repos should treat HarnessForge as an optional owner tool after
initial generation unless the repo owner explicitly adopts the CLI or GitHub
Action as a maintenance gate.

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

The audit score is structural. It checks whether a harness is coherent,
portable, reviewable, and wired to useful feedback loops. It does not prove that
a specific agent will complete a specific project task correctly.

## Quick Start

Install from a clone, then run `harnessforge --help`. See
[Installation](docs/installation.md) for exact setup commands.

Run the guided first-run summary before writing anything, then preview and
generate:

```bash
harnessforge quickstart --target /path/to/repo
harnessforge init --target /path/to/repo --dry-run
harnessforge init --target /path/to/repo
```

Audit and report:

```bash
harnessforge audit --target /path/to/repo --min-score 85
harnessforge report --target /path/to/repo --markdown-report docs/harness/evidence/report.md
```

Prepare release evidence:

```bash
harnessforge release-check --target /path/to/repo --markdown-report docs/harness/evidence/release-check.md
```

See [Usage](docs/usage.md) for `harnessforge update`, `finalize-review`,
`migrate-state`, `corpus`, existing-instruction review, maturity report output,
blueprints, CI preflight, and command-specific options.

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
tests, pin checks, research source checks, and a self-audit.

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
