# Harness Operations

Status: live

This repo uses its own harness as product evidence. The harness makes the CLI
work restartable, scoped, verifiable, and portable across Python 3.13+, macOS
15+, Windows 11+, and Ubuntu 22.04+.

## Goal

Make HarnessForge a practical default for adding agent-ready operating
surfaces to any repository while staying honest about what the tool can prove.
The CLI can score structure. Real effectiveness still requires representative
agent sessions.

## Practical Harness Map

| Domain | Artifact | Purpose |
| --- | --- | --- |
| Instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | Startup path, hard requirements, verification, and platform routing |
| Tools | `harnessforge`, `action.yml`, `init.sh`, `init.ps1`, `scripts/check_pins.py` | Creation, audit, update, CI action, local checks, and pin enforcement |
| Environment | `pyproject.toml`, CI matrix, `component-inventory.md`, `dependency-change-policy.md` | Python, OS, package, component, and Action support contract |
| State | `feature_list.json`, `progress.md`, `evidence-log.md` | Current objective, evidence, and restart state |
| Feedback | tests, self-audit, CI, `first-agent-task.md`, `verification-matrix.md`, `sensor-registry.md`, `evaluator-rubric.md`, `verify-json-contract.md`, `effectiveness-eval-contract.md`, research refresh | First-agent harness improvement, deterministic quality checks, sensor ownership, machine-readable verification output, benchmark-claim boundaries, and source drift signal |
| Research | `sources.md`, `research-sources.json`, `source-record.schema.json`, `source-record-example.json` | Fixed research allowlist, source provenance, and project-owned source records |
| Scope | `docs/harness/change-contract.md`, `security-boundary-map.md`, `feature-privacy-labels.json` | Acceptance, rollback, security, and data-flow discipline |
| Lifecycle | `session-handoff.md`, `clean-state-checklist.md`, `quality-document.md`, `release-controls.md`, `self-healing.md`, entropy control | Restart, release readiness, recurring maintenance, and reviewed automation |

## Operating Loop

1. Read `AGENTS.md`.
2. Use `first-agent-task.md` when a newly generated harness needs its first
   repo-specific improvement pass.
3. Check `feature_list.json`, `progress.md`, and `session-handoff.md`.
4. Check `component-inventory.md` when a task touches nested project boundaries.
5. Use `change-contract.md` for non-trivial behavior or template changes.
6. Implement the smallest coherent slice.
7. Review `sensor-registry.md` when adding, deleting, or promoting checks.
8. Run `./init.sh` or the narrowest relevant subset.
9. Run `python scripts/check_pins.py --root .` for dependency, Action, or
   workflow changes.
10. Run `python scripts/refresh_research.py --root . --check` for research
   source ledger or source-doc changes.
11. Use `clean-state-checklist.md` before ending non-trivial sessions.
12. Update state and handoff files when durable facts change.

## Assessment And Updates

Use:

```bash
harnessforge quickstart --target .
harnessforge index --target . --json
harnessforge index --target . --max-files 20000 --json
harnessforge effectiveness --target . --json
harnessforge session --target .
harnessforge plan --target . --since HEAD
harnessforge audit --target .
harnessforge update --target .
harnessforge sync --check --target . --json
harnessforge verify --target . --json
```

`quickstart` is a read-only guided first-run view. It composes detection,
readiness, dry-run generation planning, preserved-file reporting, review
placeholder reporting, and next commands without writing files.

`index --json` is a read-only structural repo map. It reports file class,
language, manifest, component, source-of-truth, entrypoint, generated, vendor,
workflow, and review-required signals without command execution, writes, local
absolute paths, code excerpts, embeddings, or network access. The default file
scan limit is 4,000 files; pass `--max-files` for deeper large-repo analysis.
Component inventories remain bounded and report truncation so omitted
boundaries can be reviewed and added manually.

`effectiveness --json` is a read-only assessor for stored real-agent or
benchmark evidence. It scans target-contained
`docs/harness/evidence/effectiveness*.json` reports, or an explicit
target-relative `--evidence` path, and reports whether evidence is reviewable,
inconclusive, not better, or blocked without running benchmarks or turning
structural scores into performance claims.

`session` is a read-only restart snapshot. It reports git state when available,
detected stack, readiness verdict, harness audit score when a harness surface is
present, state-file presence, and next actions without running target commands.

`plan` is a read-only diff-aware verification planner. It uses `git diff` to
map changed files to detected or explicit project verification checks, but it
does not run those checks.

`update` reports recommended safe corrections unless `--apply` is passed.
Existing files are skipped unless `--force` is passed.

`verify --json` defaults to read-only plan mode and is documented in
`verify-json-contract.md`, with schema and example artifacts beside it. It
reports detected or explicit checks without running target repository commands.
Use `verify --json --run` only when project checks should execute; run mode
records exit codes, durations, capped stdout and stderr previews, and timing
metadata. Use `--json-report <target-relative-path>` to persist the payload
without shell redirection.

Project-owned source records use `source-record.schema.json` and
`source-record-example.json`. Keep them separate from the fixed
`research-sources.json` allowlist.

Readiness also includes advisory workflow and work-item inventory. Treat
detected setup, teardown, remediation, push, pull-request, CI polling, and
credential surfaces as review inputs before agent automation relies on them.
It also includes advisory context-budget data for instruction file size and
duplicated router text.
Governance inventory reports MCP configs, agent settings, agent skills, agent
plugin manifests, installer scripts, hooks, devcontainers, sandbox configs,
agent setup workflows, and environment files as review surfaces before agents
receive tool or runner access.
Verify evidence inventory reports target-contained
`docs/harness/evidence/verify*.json` files, latest verdicts, invalid schemas,
failed or blocked outcomes, timed-out checks, and stale reports as advisory
readiness signals.
Use `--require-verify-evidence` with `inspect --readiness` or `sync --check`
when release preflight should block unless stored verify evidence is valid,
fresh, run-mode, passed, and free of failed, blocked, timed-out, or error
summary counts.

Effectiveness inventory reports visible eval specs, benchmark files, scorer
scripts, result logs, and frontier files as review surfaces before anyone
claims a harness improves agent performance. It is a static inventory only.
Use `effectiveness-eval-contract.md` for the evidence boundary, with
`effectiveness-evidence.schema.json` and
`effectiveness-evidence-example.json` for the machine-readable claim shape.

The GitHub Action in `action.yml` exposes the same behavior to other
repositories. Keep it wired to the Python library instead of duplicating logic
in shell.
The Action also exposes `command: sync` as a read-only readiness preflight with
the same exit codes as the CLI and optional `require-verify-evidence` gating.
The optional generated CI workflow scaffold uses that sync preflight before
audit, keeps verify-evidence gating off by default, treats warning verdicts as
advisory, and stops only when readiness is blocked.

Run `./init.sh --no-env` or `.\init.ps1 -NoEnv` when checks should run without
common AI, cloud, or GitHub credentials in the process environment.

The scheduled self-healing workflow refreshes `research-inbox.md`, applies safe
missing-file harness updates, verifies the repo, and opens a pull request when
there is a reviewable change.

That scheduled workflow is HarnessForge-maintainer automation for this
repository. It is separate from the published composite Action and from the
manual workflow scaffolds generated into target repositories.

## When To Add Harness

Add harness when a repeated failure, hidden setup step, source-of-truth conflict,
platform concern, or verification gap can be turned into a small durable guide
or sensor. Do not add ceremony for taste alone.
