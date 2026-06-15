# Change Contract

Use this before non-trivial changes to CLI behavior, templates, scoring, or
platform support.

## Problem

What user problem or harness failure is being addressed?

## Build Necessity Gate

Answer before editing:

- Can the request be satisfied by no change, deletion, documentation,
  configuration, existing behavior, the standard library, native platform
  features, or an existing dependency?
- What assumptions, interpretations, or tradeoffs need to be surfaced before
  coding?
- What is the smallest change that satisfies the acceptance criteria?
- What abstraction, configurability, workflow, dependency, or cleanup is
  explicitly out of scope?
- If an intentional simplification has a known ceiling, where will the ceiling
  and upgrade path be recorded?

## Scope

In scope:

- REVIEW REQUIRED: list included files, behavior, or components for the change.

Non-goals:

- REVIEW REQUIRED: list explicit non-goals and preserved boundaries.

## Acceptance Criteria

- The user-facing command or generated artifact behaves as documented.
- Existing target files are preserved unless force behavior is explicit.
- Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+ remain supported.
- Focused tests cover the behavior.

## Pre-Release Compatibility

HarnessForge is alpha/pre-release, undeployed, and has no external users. Do
not add migration shims or preserve earlier generated layouts, schemas, CLI
outputs, Action behavior, or docs only for backward compatibility unless a
maintainer explicitly declares a release boundary. Prefer one clean current
contract, and record any temporary evaluation bridge with removal criteria.

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
  in `docs/harness/evidence/evidence-log.md`.
- Recheck source IDs: python-devguide-versions,
  github-actions-hosted-runners, github-runner-images-windows-vs2026.
