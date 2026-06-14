# repo-harness-creator

Create, assess, and maintain practical AI coding-agent harnesses for real
repositories.

This project is for teams that want agents to start faster, stay scoped, verify
work, and leave durable handoff state without turning the root instruction file
into a manual. It generates a small, repo-owned harness and scores existing
harnesses across the domains that matter in daily work: instructions, tools,
environment, state, feedback, scope, and lifecycle.

This tool is designed for personal machines first. It preserves existing files
by default, rejects unsafe generated paths, keeps runtime dependencies at zero,
redacts common local home paths from durable output, and uses hard-pinned
tooling in this repository.

## Status

Early implementation. The CLI is usable locally, but the score is structural.
It checks whether the harness is present and coherent. It does not prove that a
specific agent will succeed on a specific task without real before and after
task runs.

## Platform Contract

- Python 3.13 or newer.
- macOS 15 or newer.
- Windows 11 or newer.
- Linux starting with Ubuntu 22.04. Other modern Linux distributions should
  work when Python 3.13+ is available, but Ubuntu 22.04+ is the explicit floor.
- Runtime dependencies: Python standard library only.

## Install Locally

```bash
python -m pip install --editable .
```

Then run:

```bash
repo-harness --help
```

## Create A Harness

```bash
repo-harness init --target /path/to/repo
```

By default this writes missing files and skips anything that already exists:

- `AGENTS.md`
- `feature_list.json`
- `progress.md`
- `session-handoff.md`
- `init.sh`
- `init.ps1`
- `docs/harness/README.md`
- `docs/harness/change-contract.md`
- `docs/harness/verification-matrix.md`
- `docs/harness/component-inventory.md`
- `docs/harness/dependency-change-policy.md`
- `docs/harness/security-boundary-map.md`
- `docs/harness/feature-privacy-labels.json`
- `docs/harness/evidence-log.md`
- `docs/harness/clean-state-checklist.md`
- `docs/harness/evaluator-rubric.md`
- `docs/harness/quality-document.md`
- `docs/harness/self-healing.md`
- `docs/harness/manifest.json`
- `docs/harness/sources.md`
- `docs/harness/research-sources.json`
- `docs/harness/research-inbox.md`
- `docs/harness/entropy-control.md`
- `docs/harness/agent-operating-model.md`
- `docs/harness/multi-agent-orchestration.md`
- `docs/harness/feature-list.schema.json`

Use `--dry-run` to preview writes and `--force` only when overwriting generated
surfaces is intentional.

`--agent-file` accepts a Markdown filename in the target repository root, such
as `AGENTS.md` or `CLAUDE.md`. Paths, absolute names, and traversal are rejected.
Generated files are preflighted so symlinks cannot redirect writes outside the
target repository.

## Assess A Harness

```bash
repo-harness audit --target /path/to/repo
repo-harness audit --target /path/to/repo --json
repo-harness audit --target /path/to/repo --html harness-report.html
```

The audit returns a 0-100 structural score, a bottleneck domain, failed checks,
and concrete recommendations.

## Use The GitHub Action

This repo also ships a composite GitHub Action backed by the same Python code:

```yaml
name: Harness Audit

on:
  pull_request:
  push:

permissions:
  contents: read

jobs:
  harness:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6
      - uses: cboyd0319/repo-harness-creator@<reviewed-commit-sha> # v1
        with:
          command: audit
          min-score: "85"
          html-report: harness-report.html
          json-report: harness-report.json
```

See [docs/action.md](docs/action.md) for inputs, outputs, and update examples.
For production workflows, replace `<reviewed-commit-sha>` with a reviewed
full-length commit SHA rather than a moving branch or tag.

## Apply Safe Corrections

```bash
repo-harness update --target /path/to/repo
repo-harness update --target /path/to/repo --apply
```

`update` is conservative. Without `--apply`, it reports what it would change.
With `--apply`, it creates missing generated artifacts and leaves existing files
alone unless `--force` is also provided.

## Verify This Repo

```bash
./init.sh
```

On Windows:

```powershell
.\init.ps1
```

The local check runs the package doctor, bytecode compilation, unit tests, and a
self-audit.
