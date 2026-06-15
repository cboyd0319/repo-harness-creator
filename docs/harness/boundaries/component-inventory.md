# Component Inventory

Generated: 2026-06-14

This file records the project boundaries the harness knows about. It is an
inventory, not permission to mutate nested projects.

## Effective Agent Boundary

The model is separate from the harness. The harness includes instruction files,
shell and file tools, git access, local filesystem scope, startup scripts,
verification commands, stop hooks, lint/sensor checks, workflow permissions,
and evaluator loops. Changing any of these changes the effective agent, so
route the change through `change-contract.md` and `verification-matrix.md`.

## Detected Workspace Markers

- No workspace or monorepo orchestration markers detected.

## Detected Routing Markers

- `.github/workflows`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `action.yml`
- `.github/copilot-instructions.md`

## Detected Components

- `. (pyproject.toml)`

## Routing Rules

- Treat `.` as the root project boundary unless a task explicitly names a nested
  component.
- When workspace markers or inferred layouts are present, treat the root config
  as the orchestration boundary and nested manifests as leaf package or module
  boundaries.
- Before editing a nested component, inspect that component's own manifests,
  tests, lockfiles, and instructions.
- Before changing CI, devcontainer, local-action, Harness IDP, or agent
  instruction behavior, inspect the detected routing markers and the matching
  component paths.
- Run the smallest scoped verification command that covers the changed
  component first, then run the root harness check when root behavior,
  dependency resolution, or shared policy can change.
- Do not assume the root package manager command verifies every workspace member
  unless the root scripts, workspace config, or CI make that explicit.
- Do not install dependencies, run package scripts, or write generated files in
  nested components unless the task needs it and the command is documented.
- Preserve platform parity for macOS 15+, Windows 11+, Ubuntu 22.04+, and Python
  3.13+ where the component uses Python.

## Project Assets

- `docs/assets/logo.png`: repository logo used by the root README and project
  presentation surfaces.
- `docs/installation.md`: user-facing install, platform contract, and local
  verification guide.
- `docs/usage.md`: user-facing CLI workflow guide.
- `docs/capabilities.md`: user-facing capability, generated-file, boundary,
  and security guide.
- `docs/roadmap.md`: accepted product roadmap and backlog boundary. Keep it in
  sync with `progress.md`, `session-handoff.md`, and the harness sensor
  registry when work is accepted, deferred, or completed.

## Product Boundary Inventory

Keep these surfaces separate before changing templates, Action inputs, workflow
files, or audit scoring.

## Pre-Release Compatibility Policy

HarnessForge has not been deployed and has no external users. Treat the current
work as pre-release product shaping.

- Do not keep compatibility shims, legacy generated layouts, old report
  schemas, stale manifest formats, or prior Action/CLI behavior only because
  they existed earlier in this repository.
- Prefer one clean current contract for generated target harnesses, CLI output,
  Action behavior, scoring, and docs.
- Preserve compatibility only when a maintainer explicitly declares a release
  boundary or when a local fixture/reference repo needs a temporary bridge for
  current evaluation. Temporary bridges must be named as temporary and removed
  when the current layout or contract is adopted.
- Existing HarnessForge repo-local docs may differ from generated target docs;
  that is a product-boundary distinction, not a backward-compatibility promise.

| Surface | HarnessForge Repo-Local | Generated Target Harness | Published GitHub Action |
| --- | --- | --- | --- |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot routing may describe this repo's exact release, research, and verification workflow. | Generated root instructions must stay portable, project-owned, and free of user-specific local tool mandates, sibling checkout paths, and HarnessForge maintenance preferences. | The Action does not read this repo's local agent instructions as policy for callers. |
| Harness docs | `docs/harness/` can contain HarnessForge-specific research, release, self-healing, evidence, and backlog docs. | Generated `docs/harness/` contains generic operating docs, first-agent task, roadmap, sensors, evidence, source records, platform metadata, and security boundaries. It must not include HarnessForge-only self-healing docs. | The Action may write generated docs only for `init` or applied `update` inside the caller's `target`. |
| Workflows | `.github/workflows/ci.yml` and `.github/workflows/harness-self-heal.yml` are HarnessForge maintainer automation. Self-healing is repo-local here. | The only optional generated workflow is the manual HarnessForge CI scaffold. Target generation must not create self-heal, setup, teardown, branch-push, or pull-request automation. | The composite Action is input-driven. It does not schedule jobs, refresh research, create branches, commit, push, or open pull requests. |
| Research refresh | `scripts/refresh_research.py`, `research-sources.lock.json`, and `research-inbox.md` support this repo's fixed-allowlist research maintenance. | Generated research files are project-owned review scaffolds. They may describe how to run a reviewed fixed-allowlist refresh, but no scheduled refresh is generated. | The Action does not refresh research. |
| Generated ownership and drift | This repo tracks product code, templates, and local harness docs as project-owned maintenance surfaces. | Generated target manifests must include ownership metadata, content hashes, template hashes, platform contract metadata, review-required placeholders, and drift report inputs. | Action reports should expose target-relative generated drift and never depend on this repo's working tree. |
| Platform contracts | This repo supports Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+ unless a component says otherwise. | Generated target harnesses record the selected `platformContract`, supported platforms, and primary-source review date. Unsupported platform scripts are omitted. | The Action passes the selected platform contract to generation and reporting, but does not broaden target support. |
| Assessment scoring | This repo's self-audit must enforce the current product boundary, including local-only self-healing, generated ownership metadata, platform contracts, first-agent lifecycle, verify/effectiveness evidence slots, and stale local-path command detection. | A generated target harness must not score as complete if it contains HarnessForge repo-local self-healing, sibling-checkout commands, missing generated-file metadata, missing platform metadata, or no first-agent/roadmap/sensor lifecycle. Structural score still does not prove real-agent effectiveness. | Action summaries and reports should surface the same audit/readiness/evidence boundaries without treating Action success as a real-agent performance claim. |
| Optional overlays | Product blueprints and internal roadmap docs can evolve in this repo. | Blueprints are explicit opt-ins and land in review-required areas separate from normal `init`. | The Action may invoke explicit commands only from inputs. |

## Manual Additions

- `src/harnessforge/blueprints.py`: optional blueprint registry and safe
  blueprint artifact writer. This is product code, not generated target-repo
  template content.
- `src/harnessforge/planner.py`: read-only diff-aware verification planner used
  by the CLI. It maps changed files to detected or explicit project checks and
  does not execute target commands.
- `src/harnessforge/indexer.py`: read-only structural repo indexer used by the
  CLI to summarize file classes, languages, manifests, components,
  source-of-truth signals, and review-required placeholders without writes.
- `src/harnessforge/public_repo_corpus.py`: offline public-repo fixture corpus
  used by `harnessforge corpus` to test detection and generated-content quality
  against pinned popular open-source repository shapes without network access.
- `src/harnessforge/effectiveness.py`: read-only effectiveness evidence
  assessor used by the CLI to validate stored benchmark or real-agent evidence
  without running benchmarks or producing unsupported performance scores.
- `src/harnessforge/report.py`: read-only unified report composer used by the
  CLI and composite Action. It combines readiness, audit, drift, index,
  verify evidence, effectiveness evidence, first-agent status, and platform
  contract without running target commands.
- `docs/harness/feedback/sensor-registry.md`: review-required ownership, source,
  purpose, and retirement record for checks and recurring gates.
- `docs/harness/research/source-record.schema.json`: generated schema for project-owned
  source provenance records, separate from the fixed research allowlist.
- `docs/harness/research/source-record-example.json`: review-required starter record for
  project-owned source provenance.
- `docs/harness/research/large-codebase-indexing-research.md`: repo-local research note
  for large existing repo analysis and future `harnessforge index` design.
- `docs/harness/state/first-agent-task.md`: generated first-agent harness improvement
  task that asks the first agent in a newly harnessed repo to deepen component,
  verification, source-of-truth, evidence, and security guidance.
- `src/harnessforge/sync.py`: shared read-only sync preflight payload and exit
  code helpers used by both the CLI and composite Action.
