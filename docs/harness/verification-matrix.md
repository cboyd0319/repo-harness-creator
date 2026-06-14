# Verification Matrix

Use the smallest check set that proves the changed behavior.

| Change Type | Required Checks |
| --- | --- |
| CLI parser or command output | Focused unit tests plus `python -m repo_harness_creator --help` |
| Generator or templates | Generator tests, temporary repo integration test, self-audit |
| Component detection or monorepo routing | Detector tests, generated manifest test, and self-audit |
| Scoring rules | Positive and negative audit tests |
| Platform handling | Doctor tests or CI on the affected OS |
| Docs only | Self-audit and link/source review when URLs changed |
| Packaging metadata | Editable install or entrypoint smoke test |
| Dependencies, tool versions, or workflow Actions | `python scripts/check_pins.py --root .`, primary-source version evidence, install smoke, and affected tests |
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
