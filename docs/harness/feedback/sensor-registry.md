# Sensor Registry

Status: live

This repo-local registry has been reviewed. Generated target registries start
with `REVIEW REQUIRED`; this local file uses reviewed entries. Update owner,
source, purpose, retirement condition, and review cadence whenever a check is
added, removed, renamed, or promoted into a release, sync, or self-heal gate.

This registry records the checks and signals HarnessForge uses for local
completion, release prep, and recurring maintenance. It is not a command
runner. Use `verification-matrix.md` to choose checks for a change and
`harnessforge verify --target . --run` only when command execution is intended.

## Registered Sensors

| Sensor | Source | Purpose | Owner | Retire When | Review Cadence |
| --- | --- | --- | --- | --- | --- |
| `PYTHONPATH=src:. python3 -m unittest discover -s tests` | `AGENTS.md`, `verification-matrix.md`, root entrypoints | Proves Python behavior covered by the unit suite. | HarnessForge maintainer | Replace when the test runner or package layout changes. | Every behavior or template slice |
| `PYTHONPATH=src:. python3 -m compileall src tests scripts` | Root entrypoints | Catches syntax/import parse failures across runtime, tests, and scripts. | HarnessForge maintainer | Replace if compile coverage moves into a stronger local gate. | Every non-doc slice |
| `PYTHONPATH=src:. python3 scripts/check_pins.py --root .` | Pin policy, root entrypoints | Verifies package, workflow, Action, and dependency pin policy. | HarnessForge maintainer | Replace if pin policy moves to a different reviewed checker. | Dependency, workflow, Action, or packaging changes |
| `PYTHONPATH=src:. python3 scripts/refresh_research.py --root . --check` | Research source policy, root entrypoints | Validates fixed research-source metadata without network refresh. | HarnessForge maintainer | Replace if source-ledger validation moves into product tests. | Research source or source-doc changes |
| `PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 100` | Generated harness manifest, self-audit policy | Checks live harness structure, snippets, drift-sensitive boundaries, and this repo's strict local score floor. | HarnessForge maintainer | Replace if audit scoring contract changes. | Every harness-affecting slice |
| `PYTHONPATH=src:. python3 -m harnessforge plan --target . --since HEAD --json` | Diff-aware planner contract | Confirms the read-only planner emits parseable JSON for the current diff. | HarnessForge maintainer | Replace if planner smoke moves into a dedicated integration gate. | Planner, detection, or routing changes |
| `PYTHONPATH=src:. python3 -m harnessforge session --target . --json` | Session snapshot contract | Confirms the read-only restart report emits parseable JSON. | HarnessForge maintainer | Replace if session output is folded into another restart contract. | Session, readiness, or state-file changes |
| Optional `PYTHONPATH=src:. python3 -m harnessforge report --target . --json` | Unified report contract | Confirms the read-only report composer emits parseable JSON without running target commands. | HarnessForge maintainer | Replace if report output is folded into release evidence automation. | Report, readiness, audit, index, evidence, or Action changes |
| `docs/roadmap.md` | README start-here table, `current-state.md` | Tracks accepted roadmap and backlog scope so product decisions do not live only in chat or research notes. | HarnessForge maintainer | Replace if roadmap state moves into a stronger issue tracker or generated planning contract. | Brainstorm acceptance, backlog reshaping, release-prep scope changes |
| `docs/harness/authoritative-facts.md` | Harness Maintenance Optimization | Routes fact ownership and docs updates so small changes do not require broad harness doc fan-out. | HarnessForge maintainer | Replace if report/audit can fully derive docs routing from structured metadata. | Before updating more than one durable doc or state file for routine changes |
| `./init.sh` | POSIX root entrypoint | Runs the local macOS/Linux verification contract. | HarnessForge maintainer | Replace if POSIX support or entrypoint policy changes. | End of non-trivial slices and release prep |
| `pwsh -NoProfile -File ./init.ps1` | Windows/PowerShell root entrypoint | Runs the Windows-compatible verification contract from PowerShell; current local macOS `pwsh` command execution is blocked before repo code by a host .NET assembly-load error. | HarnessForge maintainer | Replace if Windows support or entrypoint policy changes. | Release prep on a healthy PowerShell host or after local `pwsh` is repaired |

## Agent-Oriented Failure Feedback

For custom checks, prefer failure messages with:

- what failed;
- why the project boundary or invariant matters;
- where an agent should look first to repair it;
- which evidence should be recorded after the fix.

## Runtime Observability

When the project runs a service, job, or long-lived process, prefer structured
logs (machine-readable fields, not free text) at startup, error, and boundary
points, and carry a request or correlation id across components so a failure
traces to one run. Register the resulting startup, error, health, and trace
signals as sensors above so completion and debugging rely on observable state.

## Rules

- A sensor is a signal, not a guarantee. It does not prove real-agent effectiveness.
- Do not add a recurring gate without an owner, source, purpose, retirement
  condition, and review cadence.
- Keep source paths target-relative and portable.
- Remove sensors that no longer catch meaningful regressions or that duplicate
  a stronger reviewed gate.
