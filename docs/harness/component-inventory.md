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
- `src/harnessforge/effectiveness.py`: read-only effectiveness evidence
  assessor used by the CLI to validate stored benchmark or real-agent evidence
  without running benchmarks or producing unsupported performance scores.
- `src/harnessforge/report.py`: read-only unified report composer used by the
  CLI and composite Action. It combines readiness, audit, drift, index,
  verify evidence, effectiveness evidence, first-agent status, and platform
  contract without running target commands.
- `docs/harness/sensor-registry.md`: review-required ownership, source,
  purpose, and retirement record for checks and recurring gates.
- `docs/harness/source-record.schema.json`: generated schema for project-owned
  source provenance records, separate from the fixed research allowlist.
- `docs/harness/source-record-example.json`: review-required starter record for
  project-owned source provenance.
- `docs/harness/large-codebase-indexing-research.md`: repo-local research note
  for large existing repo analysis and future `harnessforge index` design.
- `docs/harness/first-agent-task.md`: generated first-agent harness improvement
  task that asks the first agent in a newly harnessed repo to deepen component,
  verification, source-of-truth, evidence, and security guidance.
- `src/harnessforge/sync.py`: shared read-only sync preflight payload and exit
  code helpers used by both the CLI and composite Action.
