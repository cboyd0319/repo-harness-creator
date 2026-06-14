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
- `python -m repo_harness_creator audit --target . --min-score 85`

## Rollback

Revert the specific source, template, or docs change. Do not reset unrelated
user work.
