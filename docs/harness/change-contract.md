# Change Contract

Use this before non-trivial changes to CLI behavior, templates, scoring, or
platform support.

## Problem

What user problem or harness failure is being addressed?

## Scope

In scope:

- TBD

Non-goals:

- TBD

## Acceptance Criteria

- The user-facing command or generated artifact behaves as documented.
- Existing target files are preserved unless force behavior is explicit.
- Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+ remain supported.
- Focused tests cover the behavior.

## Verification

- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- `python -m harnessforge audit --target . --min-score 85`

## Rollback

Revert the specific source, template, or docs change. Do not reset unrelated
user work.

## Platform Impact

Declared platform contract: Python 3.13+, macOS 15+, Windows 11+, Ubuntu
22.04+, and best-effort support for other modern Linux distributions with
Python 3.13+.

Record whether the change affects that contract or any unsupported platform.
For platform floors, interpreter versions, runner labels, or CI image
assumptions, record source-backed evidence:

- Last HarnessForge platform source review: 2026-06-15.
- Before changing platform floors, interpreter versions, runner labels, or CI
  image assumptions, record current primary-source evidence and the review date
  in `docs/harness/evidence-log.md`.
- Recheck source IDs: python-devguide-versions,
  github-actions-hosted-runners, github-runner-images-windows-vs2026.
