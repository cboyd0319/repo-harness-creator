# Verification Matrix

Use the smallest check set that proves the changed behavior.
Prefer local checks during active development. Remote CI is for reviewed
branches, release/batch checkpoints, platform-specific confirmation, and cases
where local checks cannot cover the risk.
The default push/PR CI path runs Ubuntu 22.04 with Python 3.13.14; macOS and
Windows remote checks are manual `workflow_dispatch` platform checks.

| Change Type | Required Checks |
| --- | --- |
| CLI parser or command output | Focused unit tests plus `python -m harnessforge --help` |
| Generator or templates | Generator tests, temporary repo integration test, self-audit |
| Component detection or monorepo routing | Detector tests, generated manifest test, and self-audit |
| Scoring rules | Positive and negative audit tests |
| Platform handling | Doctor tests or CI on the affected OS |
| Docs only | Self-audit and link/source review when URLs changed |
| Agent-generated tests | Review test intent before implementation, reject stubbed or assertion-free tests, and confirm new tests fail before the fix when practical |
| Packaging metadata | Editable install or entrypoint smoke test |
| Dependencies, tool versions, or workflow Actions | `python scripts/check_pins.py --root .`, primary-source version evidence, install smoke, and affected tests |
| AI/RAG/agent tools, external data flow, auth, secrets, or deployment boundary | Update security boundary/threat model evidence, run focused abuse-case tests, self-audit, and affected local tests |
| Training, demo, or intentionally vulnerable fixtures | Confirm owner/path and accepted risk, avoid automatic remediation unless in scope, and run targeted fixture tests |
| Self-healing or research refresh | `python scripts/refresh_research.py --root .`, `python scripts/check_pins.py --root .`, unit tests, and self-audit |

## Full Local Check

```bash
./init.sh
```

Windows:

```powershell
.\init.ps1
```

## When Checks Cannot Run

Record the command, reason, risk, and next best check in `progress.md` or
`session-handoff.md`.

If remote CI is intentionally skipped to control cost, record the local checks
that replaced it and the remaining platform risk.
