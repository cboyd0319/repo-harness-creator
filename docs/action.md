# GitHub Action

This repository is also a composite GitHub Action. It sets up Python, sets
`PYTHONSAFEPATH=1`, points `PYTHONPATH` at the action checkout, then runs the
same library code as the CLI.

## Boundary Model

The Action is separate from this repo's live harness and from generated target
harness files. It must not assume HarnessForge's own `pins.toml`, workflows,
state files, or release process are present in the caller repository.

- `audit` reads the declared `target`, writes only requested reports inside
  that target, and can run with `contents: read`.
- `init` and applied `update` may write generated harness files inside
  `target`; callers should grant write permissions only when they intend to
  commit or open a pull request.
- The Action does not schedule jobs, refresh research, create branches, commit,
  push, or open pull requests by itself.
- Report paths are target-relative outputs with forward slashes on every
  runner.
- The caller owns checkout credentials, branch creation, commits, pushes, and
  pull-request creation.

## Audit With HarnessForge

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
        with:
          persist-credentials: false
      - uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
        with:
          command: audit
          min-score: "85"
          html-report: harness-report.html
          json-report: harness-report.json
```

## Plan Safe Corrections

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: update
```

`update` does not change files unless `apply: "true"` is set.

## Create Missing Harness Files

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: init
```

Existing files are preserved. Set `force: "true"` only when overwriting
generated harness files is intentional.

Optional workflow scaffolds are off by default:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: init
    with-ci-workflow: "true"
    with-self-heal-workflow: "true"
```

Review and pin the generated workflows before relying on them. The scaffolded
workflows use manual triggers by default to avoid surprise CI cost. They are
project-owned generated files, not the live HarnessForge repository workflow
and not behavior embedded in the composite Action runtime.

## Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `command` | `audit` | `audit`, `init`, `update`, or `doctor` |
| `target` | `.` | Repository path to inspect or modify |
| `python-version` | `3.13.14` | Python version passed to `actions/setup-python` |
| `min-score` | `85` | Minimum passing structural audit score from 0 to 100 |
| `fail-on-score` | `true` | Fail the action when score is below threshold |
| `apply` | `false` | Apply safe corrections for `update` |
| `force` | `false` | Allow overwrites for generated files |
| `agent-file` | `AGENTS.md` | Root instruction file to generate |
| `platform-contract` | `cross-platform` | Generated harness platform contract: `cross-platform`, `macos-only`, `windows-only`, or `linux-only` |
| `with-ci-workflow` | `false` | Include optional manual HarnessForge CI workflow scaffolding during `init` or applied `update` |
| `with-self-heal-workflow` | `false` | Include optional manual self-heal pull-request workflow scaffolding during `init` or applied `update` |
| `html-report` | empty | Optional target-relative HTML report path; POSIX and Windows absolute/rooted paths are rejected |
| `json-report` | empty | Optional target-relative JSON report path; POSIX and Windows absolute/rooted paths are rejected |

Report paths must be relative and stay inside `target`. Absolute paths and
traversal outside the target repository are rejected.

## Outputs

| Output | Purpose |
| --- | --- |
| `overall-score` | Harness score from 0 to 100 |
| `bottleneck` | Lowest-scoring harness domain |
| `report-json` | Target-relative JSON report path when requested |
| `report-html` | Target-relative HTML report path when requested |
| `changed-files` | Number of files written by `init` or applied `update` |

Report path outputs use forward slashes on every runner so workflow consumers
can handle them consistently across Windows and POSIX jobs.

## Version Pinning

For production workflows, pin this Action and all other third-party Actions to a
full-length commit SHA. A release tag such as `@v1` is acceptable for quick
evaluation, but release-critical checks should use an immutable SHA after
reviewing the release.

Audit-only workflows should also set `persist-credentials: false` on
`actions/checkout`, as shown above. Workflows that intentionally push branches
or tags need their own reviewed credential path.
