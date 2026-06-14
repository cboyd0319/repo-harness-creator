# GitHub Action

This repository is also a composite GitHub Action. It sets up Python, sets
`PYTHONSAFEPATH=1`, points `PYTHONPATH` at the action checkout, then runs the
same library code as the CLI.

## Audit A Repo Harness

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

## Plan Safe Corrections

```yaml
- uses: cboyd0319/repo-harness-creator@<reviewed-commit-sha> # v1
  with:
    command: update
```

`update` does not change files unless `apply: "true"` is set.

## Create Missing Harness Files

```yaml
- uses: cboyd0319/repo-harness-creator@<reviewed-commit-sha> # v1
  with:
    command: init
```

Existing files are preserved. Set `force: "true"` only when overwriting
generated harness files is intentional.

## Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `command` | `audit` | `audit`, `init`, `update`, or `doctor` |
| `target` | `.` | Repository path to inspect or modify |
| `python-version` | `3.13.14` | Python version passed to `actions/setup-python` |
| `min-score` | `85` | Minimum passing structural audit score |
| `fail-on-score` | `true` | Fail the action when score is below threshold |
| `apply` | `false` | Apply safe corrections for `update` |
| `force` | `false` | Allow overwrites for generated files |
| `agent-file` | `AGENTS.md` | Root instruction file to generate |
| `html-report` | empty | Optional target-relative HTML report path |
| `json-report` | empty | Optional target-relative JSON report path |

Report paths must be relative and stay inside `target`. Absolute paths and
traversal outside the target repository are rejected.

## Outputs

| Output | Purpose |
| --- | --- |
| `overall-score` | Harness score from 0 to 100 |
| `bottleneck` | Lowest-scoring harness domain |
| `report-json` | JSON report path when requested |
| `report-html` | HTML report path when requested |
| `changed-files` | Number of files written by `init` or applied `update` |

## Version Pinning

For production workflows, pin this Action and all other third-party Actions to a
full-length commit SHA. A release tag such as `@v1` is acceptable for quick
evaluation, but release-critical checks should use an immutable SHA after
reviewing the release.
