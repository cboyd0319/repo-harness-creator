# AGENTS.md

## Project overview

HarnessForge is a Python 3.13+ CLI and composite GitHub Action for creating,
assessing, and safely updating AI coding-agent harnesses in arbitrary repos.

Core harness contract: instructions, tools, environment, state, and feedback.
Changing instruction, tool, filesystem, git, startup, verification, hook, lint,
or evaluator surfaces changes the effective agent.

Startup path:

1. Confirm the working directory.
2. Read this file, `current-state.md`, and `feature_list.json`.
3. For harness-maintenance work, use `.agents/skills/harness/SKILL.md`.
4. Read `README.md` only for public docs, install/usage, CLI behavior, or
   product-positioning changes.
5. Read `docs/harness/README.md` and
   `docs/harness/authoritative-facts.md` for harness-doc, generated-output,
   scoring, report, or maintenance-policy changes.
6. Read `docs/roadmap.md` before selecting, deferring, or reshaping backlog,
   release-prep, or product-scope work.
7. Check `docs/harness/boundaries/component-inventory.md` before changing
   component boundaries, generated files, or verification routing.

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
PYTHONPATH=src:. python3 scripts/refresh_research.py --root . --check
```

Run the research check when research ledgers or source docs change. Run the
refresh command without `--check` only when fetching research metadata. Run
the pin check when dependencies, workflows, Action metadata, or packaging
configuration change.

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
- HarnessForge has not been deployed and has no external users. Prefer the
  clean product contract over backward compatibility until a maintainer sets a
  release boundary.
- Keep platform-specific instruction routers short; point to canonical repo
  instructions instead of duplicating durable rules.
- Keep generated artifacts portable. Do not commit machine-specific or
  user-specific absolute paths unless explicitly requested and evidenced.
- If a repo contains intentionally vulnerable training, demo, or fixture code,
  preserve it unless the user explicitly requests remediation for that scope.
- Follow `CONTRIBUTING.md`. Use signed-off commits for review commits.
- Keep this file as a map. Put long-running policy, research, and operations
  detail in `docs/harness/`.

### Implementation Discipline

Before writing code, stop at the first rung that solves the request:

1. Do not build if no change, deletion, docs, config, or existing behavior is
   enough.
2. Use the standard library before custom code.
3. Use native platform features before new libraries.
4. Use existing project dependencies before adding dependencies.
5. Prefer one clear local change over a new abstraction.
6. Only then write the minimum code that satisfies the contract.

Rules:

- State assumptions and tradeoffs before coding when ambiguous.
- Do not add speculative features, configurability, abstractions, workflows, or
  dependencies.
- Keep changed lines traceable to the objective; avoid drive-by cleanup.
- If an intentional simplification has a known ceiling, record the ceiling and
  upgrade path.
- Do not cut validation at trust boundaries, data-loss prevention, security,
  accessibility, platform parity, or explicit requirements.
- Non-trivial logic needs one focused runnable check.

## Testing instructions

- Use the smallest reliable check that proves the changed surface.
- Prefer local linting, tests, pin checks, and audit before remote CI.
- Add focused tests for CLI behavior, filesystem writes, scoring, Action
  behavior, research refresh, and cross-platform paths.
- For behavior changes, prefer a separate test-design step when practical.
  Reject stubbed, assertion-free, or shortcut tests, and confirm new tests fail
  before implementation when that failure is reliable and cheap to reproduce.
- Verify generated files work for POSIX and Windows paths.
- Do not claim authoritative product quality from structural checks alone. Real
  agent effectiveness still needs representative task runs.
- Definition Of Done: behavior implemented, focused verification ran,
  generated files/docs match the CLI, self-audit passes, and skipped
  OS-specific checks are recorded with risk.
- End of Session: do not recreate separate root `progress.md` or
  `session-handoff.md`; use `current-state.md` for current objective and
  restart context. Do not update `feature_list.json`, `current-state.md`, and
  the evidence log as a routine bundle.
  `feature_list.json` changes only for feature state or major durable product
  evidence. `current-state.md` changes only when the active objective,
  verified state, blockers, touched surfaces, or next step materially changes.
  `docs/harness/evidence/evidence-log.md` changes only for meaningful
  verification evidence. Use `docs/harness/state/clean-state-checklist.md`
  before ending non-trivial work.

## Security considerations

- People run this code on personal machines and private repos. Default to the
  safest easy behavior; when ease and security conflict, security wins and the
  error must explain the safe next step.
- Never overwrite target repository files unless the user passes `--force`.
- Reject unsafe generated paths, traversal, absolute instruction filenames, and
  symlink escapes outside the target repository.
- Redact common home paths from durable output; treat committed absolute local
  paths as audit failures unless explicitly requested.
- Use latest stable supported packages with hard pins. Direct dependencies use
  exact versions; external GitHub Actions use full-length commit SHAs with
  version comments.
- Do not add network access to normal local harness generation. Network access
  belongs in explicit research-refresh or CI setup paths.
- Do not commit secrets, tokens, credentials, private repo data, or long raw
  command output.
