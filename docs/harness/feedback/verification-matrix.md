# Verification Matrix

Use the smallest check set that proves the changed behavior.
Prefer local checks during active development. Remote CI is for reviewed
branches, release/batch checkpoints, platform-specific confirmation, and cases
where local checks cannot cover the risk.
Use `sensor-registry.md` to confirm owner, source, purpose, and retirement
conditions before promoting a check into a recurring gate.
The default push/PR CI path runs Ubuntu 22.04 with Python 3.13.14; macOS and
Windows remote checks are manual `workflow_dispatch` platform checks.

Use an evidence ladder for completion:

1. Static checks: formatting, lint, type, compile, schema, docs links.
2. Runtime/startup checks: app, service, package, CLI, or tool starts and runs.
3. System/user-flow checks: integration, end-to-end, benchmark slice, screenshot,
   trace, or other full-pipeline evidence when behavior crosses components.

Skipping a required layer means the change is not complete. Record the reason,
risk, and next best evidence when a layer cannot run.

| Change Type | Required Checks |
| --- | --- |
| CLI parser or command output | Focused unit tests plus `python -m harnessforge --help` |
| Repository index reports | Focused index CLI tests, JSON parse smoke, local-path scan, and self-audit |
| Effectiveness evidence assessment | Focused effectiveness CLI tests, JSON parse smoke, local-path scan, and self-audit |
| Unified harness reports | Focused report CLI and Action tests, JSON and Markdown parse/read smoke, local-path scan, and self-audit |
| Verification execution | Focused verify run-mode tests for pass, fail, blocked, timeout, JSON output, and plan-mode no-run behavior |
| GitHub Action verify bridge | Focused Action tests for verify plan/run/fail/blocked, Action metadata checks, docs boundary checks, and JSON report smoke |
| Generator or templates | Generator tests, temporary repo integration test, self-audit |
| Blueprint packs or blueprint writes | Focused blueprint CLI tests, JSON parse smoke, temporary repo dry-run/apply smoke, and self-audit |
| Component detection or monorepo routing | Detector tests, generated manifest test, and self-audit |
| Scoring rules | Positive and negative audit tests |
| JSON report contract docs | Contract fixture tests, JSON parse, self-audit, and link review |
| Platform handling | Doctor tests or CI on the affected OS |
| Docs only | Self-audit and link/source review when URLs changed |
| Agent-generated tests | Review test intent before implementation, reject stubbed or assertion-free tests, and confirm new tests fail before the fix when practical |
| Packaging metadata | Editable install or entrypoint smoke test |
| Dependencies, tool versions, or workflow Actions | `python scripts/check_pins.py --root .`, primary-source version evidence, install smoke, and affected tests |
| AI/RAG/agent tools, external data flow, auth, secrets, or deployment boundary | Update security boundary/threat model evidence, run focused abuse-case tests, self-audit, and affected local tests |
| Training, demo, or intentionally vulnerable fixtures | Confirm owner/path and accepted risk, avoid automatic remediation unless in scope, and run targeted fixture tests |
| Self-healing or research refresh | `python scripts/refresh_research.py --root . --check`, `python scripts/refresh_research.py --root .` when refreshing metadata, `python scripts/check_pins.py --root .`, unit tests, and self-audit |

## Full Local Check

```bash
./init.sh
```

Windows:

```powershell
.\init.ps1
```

## Verification Evidence Reports

Use repo-owned commands as the default verification path. Use
`harnessforge verify --target . --json` for a read-only plan. Use
`harnessforge verify --target . --json --run` only when project checks should
execute.

Use `harnessforge plan --target . --since HEAD` to map changed files to a
read-only verification plan before choosing which project checks to run. It
uses `git diff` and does not execute target commands.

Use `harnessforge report --target .` when a reviewer needs one read-only
snapshot that composes readiness, audit, drift, index, verify evidence,
effectiveness evidence, first-agent lifecycle evidence, and platform contract.
Persist JSON or Markdown with target-relative `--json-report` or
`--markdown-report` paths when the report is release or handoff evidence.

To store runnable evidence without shell redirection:

```bash
harnessforge verify --target . --run --json-report docs/harness/evidence/verify-<date>.json
```

When recording runnable evidence:

- Store the JSON report under a target-relative report path such as
  `docs/harness/evidence/verify-<date>.json`.
- Review every check with `failed`, `timed_out`, or `blocked` status before
  claiming success.
- Treat stdout and stderr previews as diagnostics. Redact secrets and keep long
  raw logs out of durable docs.
- Prefer agent-oriented failure messages for custom sensors: what failed, why
  the boundary matters, and where to repair.
- The verify report proves configured project checks were planned or run. It
  does not prove real-agent effectiveness, and it is optional unless the repo
  owner adopts HarnessForge or its Action as a gate.
- The verify report proves configured project checks were planned or run. It
  does not replace `harnessforge audit --target .` for structural harness score
  and does not prove real-agent effectiveness.

## When Checks Cannot Run

Record the command, reason, risk, and next best check in `current-state.md`
when the current restart state changes.

If remote CI is intentionally skipped to control cost, record the local checks
that replaced it and the remaining platform risk.
