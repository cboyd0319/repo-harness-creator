# Installation

This document covers the local CLI install, platform contract, and repository
verification commands. See [Usage](usage.md) for normal CLI workflows.

## Platform Contract

| Surface | Contract |
| --- | --- |
| Python | 3.13 or newer |
| macOS | 15 or newer |
| Windows | Windows 11 or newer |
| Linux | Ubuntu 22.04 or newer as the explicit floor |
| Runtime dependencies | Python standard library only |
| Build backend | `setuptools==82.0.1`, hard pinned |
| Push/PR CI | Ubuntu 22.04 on Python 3.13.14 |
| Manual platform CI | macOS 15 and `windows-2025-vs2026` on Python 3.13.14 |

Other modern Linux distributions should work when Python 3.13+ is available.
They are not the stated support floor until covered by CI or equivalent
contract tests.

## Install From A Clone

```bash
git clone https://github.com/cboyd0319/harnessforge.git
cd harnessforge
python -m pip install --editable .
harnessforge --help
```

## Run Without Installing

For local development without installing the package:

```bash
PYTHONPATH=src python -m harnessforge --help
```

## Verify This Repository

On macOS or Linux:

```bash
./init.sh
```

On Windows:

```powershell
.\init.ps1
```

The local harness check runs the package doctor, bytecode compilation, unit
tests, pin checks, research source checks, and a self-audit.

Prefer local checks and local commits during active work. Automatic GitHub
Actions workflows are parked during alpha/pre-release to avoid runner cost
while commits are frequent.

The parked workflow definitions under `.github/workflows/*.disabled` keep the
reviewed CI and self-heal commands available for later release prep. Restore a
`.yml` suffix only when maintainers intentionally re-enable remote checks.

## Focused Checks

```bash
PYTHONPATH=src:. python -m unittest discover -s tests
PYTHONPATH=src:. python scripts/check_pins.py --root .
PYTHONPATH=src:. python scripts/refresh_research.py --root . --check
PYTHONPATH=src:. python -m harnessforge audit --target . --min-score 85
PYTHONPATH=src:. python -m harnessforge index --target . --json
PYTHONPATH=src:. python -m harnessforge report --target . --json
PYTHONPATH=src:. python -m harnessforge sync --check --target . --json
```

The final command currently returns warning exit code `1` in this repository
because local instruction files need review. That is expected and not a
readiness blocker.

Run `./init.sh --no-env` or `.\init.ps1 -NoEnv` when checks should run without
common AI, cloud, or GitHub credentials in the process environment.
