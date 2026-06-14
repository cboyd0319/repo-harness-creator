# AGENTS.md

Repo harness creator is a Python 3.13+ CLI for creating, assessing, and safely
updating AI coding-agent harnesses in arbitrary repositories.

## Startup

1. Confirm the working directory.
2. Read this file, `README.md`, and `docs/harness/README.md`.
3. Check `feature_list.json`, `progress.md`, and `session-handoff.md`.
4. Run `./init.sh` on macOS/Linux or `.\init.ps1` on Windows before claiming
   the repo is healthy.
5. Use `docs/harness/clean-state-checklist.md` before ending non-trivial work.

## Hard Requirements

- Runtime code stays Python standard library only unless a dependency removes
  clear complexity and is explicitly justified.
- People run this code on personal machines. Default to the most secure and
  easiest behavior for every edge case. When those conflict, security wins and
  the error message must explain the safe next step.
- Support Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+.
- Use latest stable supported packages and hard pins. Direct dependencies use
  exact versions; external GitHub Actions use full-length commit SHAs with
  version comments.
- Use `pathlib`, explicit encodings, and argument-list subprocess calls.
- Never overwrite target repository files unless the user passes `--force`.
- Generated artifacts must avoid machine-specific absolute local paths.
- The root instruction file stays a map. Durable detail belongs in
  `docs/harness/`.
- Feature state must include behavior, verification, status, and evidence
  fields. Do not mark a feature `passing` without verification evidence.

## Work Rules

- Prefer the smallest correct change.
- Preserve user changes and dirty work.
- Treat generated templates, scoring rules, and docs as product code.
- Check `docs/harness/component-inventory.md` before changing nested project
  boundaries or component-specific verification.
- Add focused tests for CLI behavior, filesystem writes, scoring, and
  cross-platform path handling.
- Run `python scripts/check_pins.py --root .` when dependencies, workflows, or
  Action metadata change.
- Do not claim authoritative quality from structural checks alone. Real agent
  effectiveness still needs representative task runs.

## Verification

```bash
./init.sh
```

The script runs:

- `python -m repo_harness_creator doctor`
- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- `python -m repo_harness_creator audit --target . --min-score 85`

## Definition Of Done

- Behavior is implemented and covered by focused tests.
- Generated files work on POSIX and Windows paths.
- Docs and templates match the implemented CLI.
- The self-audit stays at or above the configured threshold.
- `docs/harness/clean-state-checklist.md` would pass for the session.
- Any skipped OS-specific live check is named in the handoff.

## End Of Session

Update `progress.md` and `session-handoff.md` when work changes the current
state, blockers, verification evidence, or next step. Use
`docs/harness/evaluator-rubric.md` for non-trivial output review.
