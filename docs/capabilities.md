# Capabilities

HarnessForge creates and checks repository-owned harnesses for AI coding
agents. This page explains what it can do, what it generates, and where it
draws the line.

Use this with [Usage](usage.md) for command syntax and
[Installation](installation.md) for setup.

## Quick Map

| Need | HarnessForge provides |
| --- | --- |
| Understand a repo before writing | `quickstart`, `inspect`, `index`, readiness checks, and source-of-truth detection |
| Generate an initial harness | Agent instructions, state files, verification docs, repo skill wiring, and a manifest |
| Improve existing instructions | `enhance` review plans and optional `--enhance-existing` addenda |
| Check harness health | `audit`, `sync --check`, drift detection, report output, and maturity evidence |
| Prepare release evidence | `release-check` from existing evidence without publishing artifacts |
| Keep generated content honest | Offline corpus fixtures, including a RunHaven-shaped reviewed-harness fixture |

## Core Capabilities

### Repository Understanding

HarnessForge detects repository shape before it writes anything:

- Stacks, package managers, monorepo markers, workflows, verification commands,
  source-of-truth docs, Spec Kit-style SDD surfaces, ASPEC-style folders, work
  item templates, existing harness files, SBOM evidence, and workflow control
  surfaces.
- Structural index signals such as file class, language, manifest,
  component, entrypoint, generated, vendor, workflow, review-required,
  source-of-truth, and compact `repoMap` data.
- Existing SPDX and CycloneDX-style SBOM files as evidence. HarnessForge does
  not generate SBOMs during normal flows.

`quickstart` gives a read-only first-run summary with detected context,
readiness, preserved files, planned generated files, review placeholders, and
next commands. JSON output can capture reproducible decisions for automated or
interactive-ready flows.

### Harness Generation

The default generated harness is compact and repo-owned. It includes:

- Agent entrypoints and short platform routers.
- Project state, local verification scripts, security boundaries, evidence
  docs, lifecycle docs, a target-owned `authoritative-facts.md`, and a
  manifest.
- A zero-install `.agents/skills/harness/SKILL.md` so future agents can
  improve the repo harness even when HarnessForge is not installed.
- A review-required first-agent task for deeper component boundaries,
  verification routing, source-of-truth guidance, evidence sensors, and
  security notes.

Generated guidance treats a harness as five core subsystems.
Core subsystems: instructions, state, verification, scope, and lifecycle.

| Subsystem | What it covers |
| --- | --- |
| Instructions | Startup files, repo purpose, hard constraints, and links to detail |
| State | Current work, backlog, blockers, handoff, and durable decisions |
| Verification | Runnable checks, evidence, sensors, rubrics, and evaluator loops |
| Scope | Ownership boundaries, allowed changes, non-goals, and done criteria |
| Lifecycle | Startup, handoff, cleanup, restart, and review state |

Tools, environment metadata, reports, workflows, and policy docs are support surfaces.
They should exist only when they make the core subsystems easier to follow,
verify, or maintain.

Changes to instructions, tools, filesystem scope, git access, startup scripts,
verification commands, hooks, lint or sensor checks, workflow permissions, or
evaluator loops are treated as effective-agent changes.

### Existing Instruction Review

HarnessForge preserves existing files by default. For repositories that already
have instruction files, it can:

- Append a reviewed HarnessForge quality addendum with `--enhance-existing`.
- Produce a read-only `harnessforge enhance --json` review plan.
- Parse existing sections and report canonical coverage gaps.
- Propose review-required cleanup for duplicate guidance, local absolute
  paths, user-specific tool mandates, and verification conflicts.
- Add smallest-correct-change discipline for assumptions, scope,
  dependencies, and verification.

### Audit, Report, And Release Evidence

HarnessForge can assess a harness without running target project commands:

- `audit` reports structural failures and actionable repair guidance.
- `update --drift-report` and `sync --check` report generated-file drift.
- `report` composes readiness, audit, generated drift, index summary, verify
  evidence, effectiveness evidence, first-agent task status, platform contract,
  instruction quality, docs fan-out, policy presets, SBOM adapter status,
  feature state, observability, optional index adapters, review work,
  structured review surfaces, skill wiring, and evidence-gated maturity into
  read-only JSON or Markdown.
- `release-check` assembles release readiness gates from existing report
  evidence without tagging, pushing, uploading, publishing artifacts, or
  running target commands.
- `verify --evidence-summary` writes compact verify evidence without stdout or
  stderr previews.
- `finalize-review` can retire the first-agent task, update
  `first-agent-review.json`, refresh manifest metadata, and record accepted
  advisory high-risk surfaces only through explicit apply mode.
- `migrate-state` can plan and apply migration from legacy root `progress.md`
  and `session-handoff.md` files into `current-state.md`. Apply mode preserves
  legacy files and requires confirmation.

### Opt-In Extensions

HarnessForge also provides explicit opt-in paths:

- Blueprint mode for richer project operating models, including agentic apps,
  open-source libraries, internal services, monorepos, CLI/dev tools,
  spec-driven projects, web services, data/ML, security-sensitive repos,
  infrastructure/IaC, mobile/desktop apps, docs/research repos, legacy
  migrations, education/training repos, and workflow automation.
- An offline public-repo fixture corpus for generated-content quality and
  detection regression checks without cloning public repositories. The corpus
  includes a RunHaven-shaped reviewed-harness fixture.
- A public-corpus refresh script that validates fixture metadata offline by
  default and checks remote heads only with `--verify-remote`.
- A composite GitHub Action for `audit`, `init`, `update`, `sync`, `verify`,
  `report`, `release-check`, `finalize-review`, `migrate-state`, and `doctor`
  workflows.

## Default Boundaries

HarnessForge intentionally avoids several behaviors unless the repo owner opts
in:

- It does not overwrite existing project files unless `--force` is supplied.
- It does not generate user-specific research mandates, local tool
  preferences, MCP configs, memory trees, or platform permission files.
- It does not install Spec Kit, `.specify`, slash commands, presets,
  extensions, catalogs, ASPEC, AWMAN, Maki, or workflow engines into target
  repositories.
- It does not apply blueprint guidance during normal `init`; blueprints are
  explicit opt-ins and land in a separate review area.
- It does not generate target-repo self-healing, setup, teardown, push, or PR
  automation. The only optional generated workflow scaffold is the manual
  HarnessForge CI scaffold.
- It does not run target repository commands during `inspect`, `index`,
  `effectiveness`, `session`, `report`, `release-check`, `finalize-review`,
  `migrate-state`, `sync --check`, `audit`, `update --drift-report`, or default
  `verify`. Use `verify --run` when command execution is explicitly wanted.
- It validates repo-local harness skill wiring when a harness is present, but
  the generated skill remains project-owned guidance unless the repo owner
  adopts HarnessForge checks as a gate.
- It does not clone public repositories or use network access during the
  offline `corpus` quality gate.
- It does not generate SBOMs during normal flows. Existing SPDX and
  CycloneDX-style SBOMs are detected as evidence; generation or project-owned
  SBOM imports require a future explicit adapter path.
- It does not treat structural scores as proof of real task performance.

## Generated Files

The default generated harness includes:

| Area | Key files |
| --- | --- |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` |
| Repo skill | `.agents/skills/harness/SKILL.md` |
| Project state | `feature_list.json`, `current-state.md` |
| Local checks | `init.sh`, `init.ps1`, `scripts/check_pins.py` |
| Harness root | `docs/harness/README.md`, `authoritative-facts.md`, `manifest.json` |
| Boundaries | `docs/harness/boundaries/component-inventory.md`, `change-contract.md`, `security-boundary-map.md`, `feature-privacy-labels.json` |
| Feedback | `docs/harness/feedback/verification-matrix.md`, `sensor-registry.md`, `quality-document.md`, `evaluator-rubric.md` |
| State and lifecycle | `docs/harness/state/first-agent-task.md`, `roadmap.md`, `entropy-control.md`, `clean-state-checklist.md` |
| Evidence | `docs/harness/evidence/evidence-log.md` |
| Research | `docs/harness/research/README.md`, `sources.md`, `research-inbox.md`, `source-record.schema.json`, `source-record-example.json` |
| Release | `docs/harness/release/release-controls.md` |

Each generated file is recorded in `docs/harness/manifest.json` with ownership
metadata and hashes. Project-owned existing files are tracked separately so
drift reporting can distinguish generated changes from preserved local content.

See [harness/manifest.json](harness/manifest.json) for this repo's current
generated inventory and required-file contract.

## Security Model

People may run HarnessForge on personal machines and private repositories, so
safe defaults matter. See [../SECURITY.md](../SECURITY.md) for vulnerability
reporting, scope, and severity guidance.

| Control | Behavior |
| --- | --- |
| Writes | Existing files are preserved unless `--force` is supplied. Destructive, overwrite-capable, apply-mode, or command-executing operations warn and require confirmation; non-interactive runs must pass `--yes`. |
| Dependencies | Normal local commands use the Python standard library and do not install runtime dependencies. |
| Paths | Destination paths are preflighted. Absolute instruction paths, traversal, unsafe instruction filenames, symlink escapes, and outside-repo manifest targets are rejected or ignored. |
| Discovery | Symlinked directories are skipped, and audit reads known files only when they resolve inside the target repository. |
| Privacy | Local home paths and common secret-like key/value output are redacted from durable output. |
| GitHub Action | Report paths must be target-relative, stay inside the repository, use forward-slash output paths, and write multi-line values through GitHub environment-file delimiter blocks. The Action sets `PYTHONSAFEPATH=1` so caller repository files cannot shadow the Action library at Python startup. |
| Training or fixture code | Intentionally vulnerable training, demo, or fixture code is preserved unless remediation is explicitly in scope. |
| High-risk changes | Material AI/RAG/agent, tool, external-service, auth, secret, data-flow, deployment, or workflow-permission changes require boundary or threat-model evidence plus focused checks. |

Network access is not part of routine local harness generation. It is limited
to explicit research-refresh workflows and normal GitHub Actions setup
behavior. Research refresh uses only the checked-in allowlist in
`docs/harness/research/research-sources.json`; it does not search the web,
discover latest research, or follow unreviewed source expansion. It accepts
default-port HTTPS public-source URLs only and rejects local files,
credentials, localhost, private-address targets, private DNS resolutions, and
unsafe redirects.

## Effectiveness Boundary

HarnessForge can score structure and stored evidence. It cannot prove that a
specific agent will complete a specific task correctly.

The `effectiveness` command reviews target-contained real-agent or benchmark
evidence. It does not run benchmarks, synthesize a score from missing evidence,
or promote an evolved or benchmark-winning harness change without reviewable
evidence.

Static readiness can find evaluation surfaces. It cannot validate them. Keep
structural harness quality separate from measured agent effectiveness.

See
[harness/feedback/effectiveness-eval-contract.md](harness/feedback/effectiveness-eval-contract.md).

## Repo-Local Self-Healing

This repository has its own local maintenance workflow definitions. Those
definitions are repo-local and are not the generated harness for other
repositories.

The self-heal workflow is parked during alpha/pre-release at
[../.github/workflows/harness-self-heal.yml.disabled](../.github/workflows/harness-self-heal.yml.disabled)
to avoid scheduled runner cost. If maintainers later restore the `.yml` suffix,
it refreshes research metadata, applies only safe harness updates, runs
verification, and opens a pull request when changes are detected. It does not
silently mutate `main`.

Fetched titles, headings, and hashes are treated as untrusted metadata for
human review, not executable instructions. Metadata that resembles prompt
injection, indirect prompt injection, data poisoning, credential-exfiltration
instructions, invisible Unicode, or Markdown/HTML exfiltration markers is
withheld from durable output and recorded as review signals.

Research sources are tracked in:

- [harness/research/sources.md](harness/research/sources.md)
- [harness/research/research-sources.json](harness/research/research-sources.json)
- [harness/research/research-sources.lock.json](harness/research/research-sources.lock.json)
- [harness/research/research-inbox.md](harness/research/research-inbox.md)

Project-owned source records use
[harness/research/source-record.schema.json](harness/research/source-record.schema.json)
and
[harness/research/source-record-example.json](harness/research/source-record-example.json).
They are for curated project provenance and stay separate from the fixed
HarnessForge research allowlist.
