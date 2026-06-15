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
- `verify` reads the declared `target` and defaults to read-only plan mode.
  It executes target repository checks only when `verify-run: "true"` is
  explicit. Verify plan mode can run with `contents: read`; verify run mode
  inherits the permissions and side effects of the repo-owned commands it runs.
- `sync` reads the declared `target`, reports the same readiness verdicts as
  the CLI, writes only requested JSON reports inside that target, and can run
  with `contents: read`.
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

## Sync Readiness Preflight

Run the same read-only readiness preflight used by the CLI:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: sync
    json-report: harness-sync.json
```

`command: sync` returns the same exit codes as `harnessforge sync --check`:
`0` for ready, `1` for warning, and `2` for blocked. It does not run target
repository commands and does not write generated harness files.

Require stored run-mode verify evidence before release promotion:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: sync
    require-verify-evidence: "true"
    json-report: docs/harness/evidence/sync.json
```

The `readiness-verdict` and `sync-exit-code` outputs expose the preflight
result to later workflow steps.

Use `sync-command` when detection cannot infer the project-owned readiness
command. Sync mode records that command as readiness evidence but does not
execute it.

## Verify Project Checks

Plan verification checks without running target commands:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: verify
    json-report: harness-verify.json
```

Run verification checks explicitly:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: verify
    verify-run: "true"
    verify-timeout-seconds: "120"
    verify-command: |
      python -m unittest discover
      python scripts/check_pins.py --root .
    json-report: harness-verify.json
```

`verify-command` is newline-separated. Each line is one repo-owned command.
Run mode uses argument lists rather than a shell, so shell control syntax such
as `&&`, `||`, pipes, and redirection is rejected. If `verify-command` is
empty, HarnessForge uses detected project verification commands.

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
Set `enhance-existing: "true"` when existing instruction files should preserve
their project text but receive a reviewed HarnessForge quality addendum.

Optional workflow scaffolds are off by default:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: init
    with-ci-workflow: "true"
    with-self-heal-workflow: "true"
```

Review and pin the generated workflows before relying on them. The scaffolded
workflows use manual triggers by default to avoid surprise CI cost. The CI
scaffold runs `command: sync` before audit, records
`docs/harness/evidence/sync-preflight.json`, keeps
`require-verify-evidence: "false"` by default, treats warning verdicts as
advisory, and stops only when readiness is blocked. Generated workflows are
project-owned generated files, not the live HarnessForge repository workflow
and not behavior embedded in the composite Action runtime.

## Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `command` | `audit` | `audit`, `init`, `update`, `sync`, `verify`, or `doctor` |
| `target` | `.` | Repository path to inspect or modify |
| `python-version` | `3.13.14` | Python version passed to `actions/setup-python` |
| `min-score` | `85` | Minimum passing structural audit score from 0 to 100 |
| `fail-on-score` | `true` | Fail the action when score is below threshold |
| `apply` | `false` | Apply safe corrections for `update` |
| `force` | `false` | Allow overwrites for generated files |
| `enhance-existing` | `false` | Append reviewed guidance to existing instruction files without replacing project text |
| `agent-file` | `AGENTS.md` | Root instruction file to generate |
| `platform-contract` | `cross-platform` | Generated harness platform contract: `cross-platform`, `macos-only`, `windows-only`, or `linux-only` |
| `with-ci-workflow` | `false` | Include optional manual HarnessForge CI workflow scaffolding during `init` or applied `update` |
| `with-self-heal-workflow` | `false` | Include optional manual self-heal pull-request workflow scaffolding during `init` or applied `update` |
| `verify-run` | `false` | Execute checks when `command` is `verify`; default verify mode is read-only plan mode |
| `verify-command` | empty | Optional newline-separated repo-owned verification commands for `command: verify` |
| `verify-timeout-seconds` | `300` | Per-command timeout when `command` is `verify` and `verify-run` is `true` |
| `require-verify-evidence` | `false` | Require current passed stored verify evidence when `command` is `sync` |
| `sync-command` | empty | Optional newline-separated repo-owned readiness commands for `command: sync`; commands are not executed |
| `html-report` | empty | Optional target-relative HTML report path; POSIX and Windows absolute/rooted paths are rejected |
| `json-report` | empty | Optional target-relative audit, sync, or verify JSON report path; POSIX and Windows absolute/rooted paths are rejected |

Report paths must be relative and stay inside `target`. Absolute paths and
traversal outside the target repository are rejected.

## Outputs

| Output | Purpose |
| --- | --- |
| `overall-score` | Harness score from 0 to 100 |
| `bottleneck` | Lowest-scoring harness domain |
| `report-json` | Target-relative JSON report path when requested |
| `report-html` | Target-relative HTML report path when requested |
| `changed-files` | Number of files written or enhanced by `init` or applied `update` |
| `verify-verdict` | Verify verdict when `command` is `verify` |
| `readiness-verdict` | Readiness verdict when `command` is `sync` |
| `sync-exit-code` | Sync readiness exit code when `command` is `sync` |

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
