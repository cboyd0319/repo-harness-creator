# AGENTS.md

## Project overview

HarnessForge is a Python 3.13+ CLI and composite GitHub Action for
creating, assessing, and safely updating AI coding-agent harnesses in arbitrary
repositories.

Startup path:

1. Confirm the working directory.
2. Read this file, `README.md`, and `docs/harness/README.md`.
3. Read `feature_list.json`, `progress.md`, and `session-handoff.md`.
4. Check `docs/harness/component-inventory.md` before changing component
   boundaries, generated files, or verification routing.

This repo is itself a harnessed project. Keep root instructions short and place
durable detail in `docs/harness/`.

## Build and test commands

Full local verification on macOS or Linux:

```bash
./init.sh
```

Full local verification on Windows:

```powershell
.\init.ps1
```

Focused checks:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
PYTHONPATH=src:. python3 scripts/check_pins.py --root .
PYTHONPATH=src:. python3 -m harnessforge audit --target . --min-score 85
```

Run `python3 scripts/refresh_research.py --root .` only when refreshing the
research ledger. Run `python3 scripts/check_pins.py --root .` when dependencies,
workflow files, Action metadata, or packaging configuration change.

Prefer local verification and local commits during active work. Push only at an
explicit batch boundary, release point, or user request because remote CI has
real cost.

## Code style guidelines

- Runtime code stays Python standard library only unless a dependency removes
  clear complexity and is explicitly justified.
- Support Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+.
- Use `pathlib`, explicit encodings, and argument-list subprocess calls.
- Prefer the smallest correct change. Preserve user changes and dirty work.
- Treat generated templates, audit scoring, docs, and workflows as product
  code.
- Keep platform-specific instruction routers short. They should point to the
  canonical repo instructions instead of duplicating durable rules.
- Keep generated artifacts portable. Do not commit machine-specific or
  user-specific absolute local paths unless the user explicitly requests that
  exact path and durable evidence records why.
- If a repo contains intentionally vulnerable training, demo, or fixture code,
  preserve it unless the user explicitly requests remediation for that scope.
- Follow `CONTRIBUTING.md` for submitted work. Use signed-off commits for
  commits intended for review.
- Keep this file as a map. Move long-running policy, research, and operational
  detail into `docs/harness/`.

## Testing instructions

- Use the smallest reliable check that proves the changed surface.
- Prefer local linting, tests, pin checks, and audit before remote CI.
- Add focused tests for CLI behavior, filesystem writes, scoring, Action
  behavior, research refresh logic, and cross-platform path handling.
- Verify generated files work for POSIX and Windows paths.
- Do not claim authoritative product quality from structural checks alone. Real
  agent effectiveness still needs representative task runs.
- Definition Of Done: behavior is implemented, focused verification ran,
  generated files and docs match the CLI, self-audit stays above threshold, and
  skipped OS-specific checks are recorded with risk.
- End of Session: update `progress.md` and `session-handoff.md` when work
  changes durable state, blockers, verification evidence, or the next step. Use
  `docs/harness/clean-state-checklist.md` before ending non-trivial work.

## Security considerations

- People run this code on personal machines and private repositories. Default
  to the most secure and easiest behavior for every edge case. When those
  conflict, security wins and the error message must explain the safe next step.
- Never overwrite target repository files unless the user passes `--force`.
- Reject unsafe generated paths, traversal, absolute instruction filenames, and
  symlink escapes outside the target repository.
- Redact common local home paths from durable output, and treat committed
  absolute local paths as audit failures unless explicitly requested.
- Use latest stable supported packages with hard pins. Direct dependencies use
  exact versions; external GitHub Actions use full-length commit SHAs with
  version comments.
- Do not add network access to normal local harness generation. Network access
  belongs in explicit research-refresh or CI setup paths.
- Do not commit secrets, tokens, credentials, private repo data, or long raw
  command output.
