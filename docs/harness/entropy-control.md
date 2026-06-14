# Entropy Control

Harness debt is product debt for this repository.

## Regular Checks

- Run `repo-harness audit --target .` after template, scoring, or docs changes.
- Run `./init.sh` before claiming local readiness.
- Keep generated templates aligned with README examples.

## Cleanup Rules

- Remove stale instructions instead of adding exceptions.
- Keep `AGENTS.md` short enough to read at startup.
- Prefer one clear template over multiple near-duplicates.
- Delete disposable reports unless intentionally tracked.
