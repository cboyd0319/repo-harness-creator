# AGENTS.md

## Project overview

HarnessForge is a Python 3.13+ CLI and composite GitHub Action for
creating, assessing, and safely updating AI coding-agent harnesses in arbitrary
repositories.

Core harness contract: instructions, tools, environment, state, and feedback
are all required. Keep instructions map-like, tool access sufficient but least
privileged, environment facts self-describing, state current across sessions,
and verification commands explicit. Feedback usually has the best return, so
fix missing or weak checks before adding broader process.
Changing instruction, tool, filesystem, git, startup, verification, hook, lint,
or evaluator surfaces changes the effective agent. Treat those as harness
product changes.

Startup path:

1. Confirm the working directory.
2. Read this file, `progress.md`, `session-handoff.md`, and
   `feature_list.json`.
3. Read `README.md` only for public docs, install/usage, CLI behavior, or
   product-positioning changes.
4. Read `docs/harness/README.md` and
   `docs/harness/authoritative-facts.md` for harness-doc, generated-output,
   scoring, report, or maintenance-policy changes.
5. Read `docs/roadmap.md` before selecting, deferring, or reshaping backlog,
   release-prep, or product-scope work.
6. Check `docs/harness/boundaries/component-inventory.md` before changing
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

Run `python3 scripts/refresh_research.py --root . --check` when research
ledgers or source docs change. Run `python3 scripts/refresh_research.py --root
.` only when refreshing fetched research metadata. Run `python3
scripts/check_pins.py --root .` when dependencies, workflow files, Action
metadata, or packaging configuration change.

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
- HarnessForge has not been deployed and has no external users. Do not preserve
  backward compatibility with previous generated artifacts, CLI shapes, report
  schemas, manifests, docs layouts, or Action behavior unless a maintainer
  explicitly sets a release boundary. Prefer the clean product contract over
  migration shims.
- Keep platform-specific instruction routers short. They should point to the
  canonical repo instructions instead of duplicating durable rules.
- Keep generated artifacts portable. Do not commit machine-specific or
  user-specific absolute local paths unless the user explicitly requests that
  exact path and durable evidence records why.
- If a repo contains intentionally vulnerable training, demo, or fixture code,
  preserve it unless the user explicitly requests remediation for that scope.
- Follow `CONTRIBUTING.md`. Use signed-off commits for review commits.
- Keep this file as a map. Move long-running policy, research, and operational
  detail into `docs/harness/`.

### Implementation Discipline

Before writing code, stop at the first rung that solves the request:

1. Do not build if the goal can be met by no change, deletion, documentation,
   configuration, or existing behavior.
2. Use the standard library before custom code.
3. Use native platform features before new libraries.
4. Use existing project dependencies before adding dependencies.
5. Prefer one clear local change over a new abstraction.
6. Only then write the minimum code that satisfies the contract.

Rules:

- State assumptions and tradeoffs before coding when the request is ambiguous.
- Do not add speculative features, configurability, abstractions, workflows, or
  dependencies.
- Keep every changed line traceable to the current objective. Avoid drive-by
  refactors, style churn, and unrelated cleanup.
- If an intentional simplification has a known ceiling, record the ceiling and
  the upgrade path in nearby code, docs, or handoff notes.
- Do not cut input validation at trust boundaries, data-loss prevention,
  security, accessibility, platform parity, or explicit user requirements.
- Non-trivial logic needs one focused runnable check. Trivial one-line edits can
  rely on the existing relevant check.

## Testing instructions

- Use the smallest reliable check that proves the changed surface.
- Prefer local linting, tests, pin checks, and audit before remote CI.
- Add focused tests for CLI behavior, filesystem writes, scoring, Action
  behavior, research refresh logic, and cross-platform path handling.
- For behavior changes, prefer a separate test-design step when practical.
  Reject stubbed, assertion-free, or shortcut tests, and confirm new tests fail
  before implementation when that failure is reliable and cheap to reproduce.
- Verify generated files work for POSIX and Windows paths.
- Do not claim authoritative product quality from structural checks alone. Real
  agent effectiveness still needs representative task runs.
- Definition Of Done: behavior is implemented, focused verification ran,
  generated files and docs match the CLI, self-audit stays above threshold, and
  skipped OS-specific checks are recorded with risk.
- State file discipline: do not update `feature_list.json`, `progress.md`,
  `session-handoff.md`, and the evidence log as a routine bundle.
  `feature_list.json` changes only for feature state or major durable product
  evidence. `progress.md` changes only when the active objective, verified
  state, or next step materially changes. `session-handoff.md` changes only at
  a pause, handoff, context reset, or major restart boundary.
  `docs/harness/evidence/evidence-log.md` changes only for meaningful
  verification evidence. Use `docs/harness/state/clean-state-checklist.md`
  before ending non-trivial work.

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
