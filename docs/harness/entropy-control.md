# Entropy Control

Harness debt is product debt for this repository.

## Regular Checks

- Run `harnessforge audit --target .` after template, scoring, or docs changes.
- Run `./init.sh` before claiming local readiness.
- Keep generated templates aligned with README examples.

## Cleanup Rules

- Remove stale instructions instead of adding exceptions.
- Keep `AGENTS.md` short enough to read at startup.
- Prefer one clear template over multiple near-duplicates.
- Delete disposable reports unless intentionally tracked.

## Promotion Rules

Promote chat notes, scratch files, or ad hoc reports into durable harness docs
only when they prevent a repeated failure, record a decision that changes
implementation direction, make verification runnable, keep an operator workflow
recoverable, or preserve source evidence a maintainer will need.

## Evidence Rules

- Keep command names and pass/fail status in `progress.md`, active plans, or
  `docs/harness/evidence-log.md`.
- Keep screenshots and raw logs out of git unless visual or forensic proof is
  required and sanitized.
- Never preserve secrets, tokens, raw credentials, or workstation-local absolute
  paths in tracked text.

## Stop Conditions

Stop adding harness when a rule has no owner, no likely reuse, no verification
path, and no known failure mode. Remove it before it becomes cargo cult.
