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
| Feedback | tests, self-audit, CI, `evaluator-rubric.md`, `verify-json-contract.md`, `effectiveness-eval-contract.md`, research refresh | Deterministic quality checks, planned machine-readable verification output, benchmark-claim boundaries, and source drift signal |
| Scope | `docs/harness/change-contract.md`, `security-boundary-map.md`, `feature-privacy-labels.json` | Acceptance, rollback, security, and data-flow discipline |
| Lifecycle | `session-handoff.md`, `clean-state-checklist.md`, `quality-document.md`, `release-controls.md`, `self-healing.md`, entropy control | Restart, release readiness, recurring maintenance, and reviewed automation |

## Operating Loop

1. Read `AGENTS.md`.
2. Check `feature_list.json`, `progress.md`, and `session-handoff.md`.
3. Check `component-inventory.md` when a task touches nested project boundaries.
4. Use `change-contract.md` for non-trivial behavior or template changes.
5. Implement the smallest coherent slice.
6. Run `./init.sh` or the narrowest relevant subset.
7. Run `python scripts/check_pins.py --root .` for dependency, Action, or
   workflow changes.
8. Run `python scripts/refresh_research.py --root . --check` for research
   source ledger or source-doc changes.
9. Use `clean-state-checklist.md` before ending non-trivial sessions.
10. Update state and handoff files when durable facts change.

## Assessment And Updates

Use:

```bash
harnessforge quickstart --target .
harnessforge audit --target .
harnessforge update --target .
harnessforge sync --check --target . --json
```

`quickstart` is a read-only guided first-run view. It composes detection,
readiness, dry-run generation planning, preserved-file reporting, review
placeholder reporting, and next commands without writing files.

`update` reports recommended safe corrections unless `--apply` is passed.
Existing files are skipped unless `--force` is passed.

The planned `verify --json` contract is documented in
`verify-json-contract.md`, with schema and example artifacts beside it. The
contract is plan-only until explicit command execution is implemented.

Readiness also includes advisory workflow and work-item inventory. Treat
detected setup, teardown, remediation, push, pull-request, CI polling, and
credential surfaces as review inputs before agent automation relies on them.
It also includes advisory context-budget data for instruction file size and
duplicated router text.
Governance inventory reports MCP configs, agent settings, agent skills, agent
plugin manifests, installer scripts, hooks, devcontainers, sandbox configs,
agent setup workflows, and environment files as review surfaces before agents
receive tool or runner access.

Effectiveness inventory reports visible eval specs, benchmark files, scorer
scripts, result logs, and frontier files as review surfaces before anyone
claims a harness improves agent performance. It is a static inventory only.
Use `effectiveness-eval-contract.md` for the evidence boundary, with
`effectiveness-evidence.schema.json` and
`effectiveness-evidence-example.json` for the machine-readable claim shape.

The GitHub Action in `action.yml` exposes the same behavior to other
repositories. Keep it wired to the Python library instead of duplicating logic
in shell.

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
