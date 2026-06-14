# Agent Operating Model

Agents in this repo should work as maintainers of a CLI product.

## Start

- Read `AGENTS.md`, `README.md`, and this harness directory.
- Identify the current objective from `feature_list.json` and `progress.md`.
- Choose verification before editing.

## During Work

- Keep runtime dependencies at zero unless there is a clear product reason.
- Preserve cross-platform behavior in code and generated scripts.
- Treat generated templates as user-facing API.
- Keep output redacted when it may contain local absolute paths.

## Finish

- Run focused tests and the self-audit.
- Update docs and handoff when behavior or risk changes.
