# Component Inventory

Generated: 2026-06-14

This file records the project boundaries the harness knows about. It is an
inventory, not permission to mutate nested projects.

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

## Manual Additions

No manual component additions yet.
