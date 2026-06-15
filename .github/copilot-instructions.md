# HarnessForge Copilot Instructions

Use [../AGENTS.md](../AGENTS.md) as the source of truth for repo guidance.

This file exists because GitHub Copilot reads
`.github/copilot-instructions.md`. GitHub Copilot can also use `AGENTS.md`, so
keep this file short and point to durable docs instead of duplicating the
project manual.

## Required Reading For Non-Trivial Work

- [Project README](../README.md)
- [Harness engineering](../docs/harness/README.md)
- [Change contract](../docs/harness/boundaries/change-contract.md)
- [Verification matrix](../docs/harness/feedback/verification-matrix.md)
- [Dependency change policy](../docs/harness/boundaries/dependency-change-policy.md)
- [Security boundary map](../docs/harness/boundaries/security-boundary-map.md)
- [Component inventory](../docs/harness/boundaries/component-inventory.md)

## Core Rules

- HarnessForge is a Python 3.13+ standard-library-only CLI and GitHub
  Action for creating, auditing, and safely updating repo harnesses.
- People run this code on personal machines. Choose the most secure and easiest
  behavior for edge cases. When those conflict, security wins and the error
  message must explain the safe next step.
- Preserve Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+
  compatibility.
- Never overwrite target repository files unless the user passes `--force`.
- Generated paths must stay inside the target repo after symlink resolution.
  Reject unsafe path input instead of trying to repair it silently.
- Avoid runtime dependencies. If a dependency or Action changes, use latest
  stable evidence, exact package pins, and full-length GitHub Action SHAs with
  version comments.
- Run `python scripts/check_pins.py --root .` after dependency, workflow, or
  Action metadata changes.
- Keep the reusable Action wired to the Python library. Do not duplicate core
  behavior in shell.
- Treat templates, audit scoring, generated docs, and workflow files as product
  code.
- Add focused tests for CLI behavior, filesystem writes, audit scoring,
  component detection, and cross-platform path handling.
- Do not claim the repo is healthy without relevant verification evidence.
