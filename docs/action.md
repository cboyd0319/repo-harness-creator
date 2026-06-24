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
- `report` reads the declared `target`, composes readiness, audit, drift,
  index, verify evidence, effectiveness evidence, first-agent status, and
  platform contract, policy preset recommendations, and SBOM adapter status
  into one review artifact, and writes only requested JSON or Markdown reports
  inside that target.
- `release-check` reads the declared `target`, assembles release readiness
  gates from the same report evidence, writes only requested JSON or Markdown
  reports inside that target, and never publishes, tags, uploads, pushes, or
  runs target commands.
- `finalize-review` reads the declared `target`, plans first-agent review
  finalization, and writes only when `apply: "true"` is explicit. It records
  accepted advisory high-risk surface evidence only when
  `accept-detected-high-risk: "true"` is explicit.
- `migrate-state` reads the declared `target`, plans split state migration from
  `progress.md` and `session-handoff.md` into `current-state.md`, and writes
  only when `apply: "true"` is explicit. It preserves legacy files and never
  runs target commands.
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
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
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

## Unified Harness Report

Create a read-only review artifact without running target commands:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: report
    json-report: docs/harness/evidence/report.json
    markdown-report: docs/harness/evidence/report.md
```

`command: report` is not a release gate by itself. It exits zero when the
artifact is produced and reports readiness through the `readiness-verdict`
output. Use `require-verify-evidence: "true"` when the report should include
release-gate verify evidence blockers.

Use `report-command` when detection cannot infer repo-owned verification
commands. Report mode records those commands as readiness context but does not
execute them. Use `report-max-files` to raise the bounded structural index
scan limit for large repositories and `report-component-limit` to raise the
included component inventory for large monorepos; report JSON and the step
summary include file coverage from `git ls-files` when the caller target is a
git checkout and verification-command class/source metadata from detected
repo-owned command sources.
Use `report-since` to add read-only docs fan-out analysis for changed files
since a git ref. Use
`require-docs-fanout-budget: "true"` when that analysis should fail the Action
on over-budget fan-out or duplicated durable fact blocks.

The step summary includes readiness, accepted high-risk surface count, audit
score, generated drift, docs fan-out, verify/effectiveness evidence,
instruction quality, first-agent lifecycle, maturity, policy preset status,
SBOM adapter status, feature-state status, observability status,
index-adapter status, unresolved review-work count, accepted advisory
inventory count, nested instruction-plan status, repo-map counts, file
coverage, source-doc and local-doc counts, verification-command count/classes,
and SBOM file count.

Upload report artifacts in the caller workflow when that is useful. The
HarnessForge Action does not upload artifacts by default:

```yaml
- uses: actions/upload-artifact@<reviewed-commit-sha> # v7
  if: always()
  with:
    name: harness-report
    path: |
      docs/harness/evidence/report.json
      docs/harness/evidence/report.md
    if-no-files-found: warn
```

## Release Evidence Check

Assemble release readiness evidence without publishing anything:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: release-check
    json-report: docs/harness/evidence/release-check.json
    markdown-report: docs/harness/evidence/release-check.md
```

`command: release-check` returns `0` for passed, `1` for warning, and `2` for
blocked. It requires current passed run-mode verify evidence, applies the
`min-score` audit threshold, checks generated drift, first-agent lifecycle,
instruction quality, docs fan-out, feature-state alignment, runtime/process
observability, release controls, accepted high-risk surface review evidence,
effectiveness evidence, and existing SBOM evidence. It also surfaces the
evidence-gated maturity level from the source report. Use `report-command`
when detection cannot infer repo-owned
verification commands; release-check records those commands but does not
execute them. Set `require-sbom: "true"` only when the project has opted into
SBOM evidence as a hard release gate.

The `release-verdict`, `readiness-verdict`, `docs-fanout-verdict`,
`overall-score`, `report-json`, and `report-markdown` outputs expose the gate
result to later workflow steps.

## Review Finalization

Plan first-agent review finalization without writing files:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: finalize-review
    json-report: docs/harness/evidence/review-finalization.json
```

Apply the reviewed finalization only after a maintainer accepts the detected
surfaces:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: finalize-review
    apply: "true"
    accept-detected-high-risk: "true"
    reviewed-by: |
      repo maintainer
    evidence-ref: |
      docs/harness/evidence/evidence-log.md
    json-report: docs/harness/evidence/review-finalization.json
```

`command: finalize-review` never runs target commands. It can retire the
generated first-agent task, update `first-agent-review.json`, refresh manifest
metadata for those reviewed generated files, and record accepted advisory
high-risk surfaces. The caller still owns committing or opening a pull request.
Because GitHub Actions cannot prompt, `apply: "true"` and
`accept-detected-high-risk: "true"` are the explicit confirmation boundary for
this write-capable command.

## State Migration

Plan legacy state consolidation without writing:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: migrate-state
    json-report: docs/harness/evidence/state-migration.json
```

Apply the reviewed migration only when the repo owner wants
`current-state.md` updated:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: migrate-state
    apply: "true"
    json-report: docs/harness/evidence/state-migration.json
```

`command: migrate-state` writes or updates a bounded migration section in
`current-state.md`, preserves `progress.md` and `session-handoff.md`, and does
not delete legacy files. Because GitHub Actions cannot prompt, `apply: "true"`
is the explicit confirmation boundary.

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
    verify-summary: docs/harness/evidence/verify-summary.json
```

`verify-command` is newline-separated. Each line is one repo-owned command.
Run mode uses argument lists rather than a shell, so shell control syntax such
as `&&`, `||`, pipes, and redirection is rejected. If `verify-command` is
empty, HarnessForge uses detected project verification commands. Use
`verify-summary` when the workflow should persist compact run evidence without
stdout or stderr previews; use `json-report` when diagnostic previews are
needed.

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
Generated harness files are project-owned generated files after review; use the
manifest and drift report to distinguish template-owned changes from local
project edits.
For large repositories, set `generation-max-files` so `command: init` or
applied `command: update` renders generated content from the same deeper scan
you expect from `report-max-files`. Set `generation-component-limit` and
`report-component-limit` together when a large monorepo has more than 80
detected component manifests.

The optional CI workflow scaffold is off by default:

```yaml
- uses: cboyd0319/harnessforge@<reviewed-commit-sha> # v1
  with:
    command: init
    with-ci-workflow: "true"
```

Review and pin the generated workflow before relying on it. The scaffolded
workflow uses a manual trigger by default to avoid surprise CI cost. The CI
scaffold runs `command: sync` before audit, records
`docs/harness/evidence/sync-preflight.json`, keeps
`require-verify-evidence: "false"` by default, treats warning verdicts as
advisory, and stops only when readiness is blocked. The generated workflow is
a project-owned generated file, not the live HarnessForge repository workflow
and not behavior embedded in the composite Action runtime.

## Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `command` | `audit` | `audit`, `init`, `update`, `sync`, `verify`, `report`, `release-check`, `finalize-review`, `migrate-state`, or `doctor` |
| `target` | `.` | Repository path to inspect or modify |
| `python-version` | `3.13.14` | Python version passed to `actions/setup-python` |
| `min-score` | `85` | Minimum passing structural audit score from 0 to 100 |
| `fail-on-score` | `true` | Fail the action when score is below threshold |
| `apply` | `false` | Apply safe corrections for `update`, review finalization for `finalize-review`, or state migration for `migrate-state` |
| `force` | `false` | Allow overwrites for generated files |
| `enhance-existing` | `false` | Append reviewed guidance to existing instruction files without replacing project text |
| `agent-file` | `AGENTS.md` | Root instruction file to generate |
| `platform-contract` | `cross-platform` | Generated harness platform contract: `cross-platform`, `macos-only`, `windows-only`, or `linux-only` |
| `with-ci-workflow` | `false` | Include optional manual HarnessForge CI workflow scaffolding during `init` or applied `update` |
| `generation-max-files` | `4000` | Maximum number of files scanned while rendering generated files for `command: init` or applied `command: update` |
| `generation-component-limit` | `80` | Maximum number of detected components included while rendering generated files for `command: init` or applied `command: update` |
| `verify-run` | `false` | Execute checks when `command` is `verify`; default verify mode is read-only plan mode |
| `verify-command` | empty | Optional newline-separated repo-owned verification commands for `command: verify` |
| `verify-timeout-seconds` | `300` | Per-command timeout when `command` is `verify` and `verify-run` is `true` |
| `verify-summary` | empty | Optional target-relative compact verify evidence JSON path for `command: verify`; omits stdout and stderr previews |
| `require-verify-evidence` | `false` | Require current passed stored verify evidence when `command` is `sync` or `report`; release-check always requires it |
| `sync-command` | empty | Optional newline-separated repo-owned readiness commands for `command: sync`; commands are not executed |
| `report-command` | empty | Optional newline-separated repo-owned readiness commands for `command: report`, `command: release-check`, or `command: finalize-review`; commands are not executed |
| `report-max-files` | `4000` | Maximum number of files included in the `command: report` or `command: release-check` structural index summary |
| `report-component-limit` | `80` | Maximum number of detected components included in the `command: report` or `command: release-check` structural index summary |
| `report-since` | empty | Optional git ref for `command: report` or `command: release-check` docs fan-out analysis; no target commands are executed |
| `require-docs-fanout-budget` | `false` | Fail `command: report` or block `command: release-check` when docs fan-out exceeds the budget or duplicate durable fact blocks are present |
| `require-sbom` | `false` | Block `command: release-check` when no existing SPDX or CycloneDX SBOM is detected |
| `accept-detected-high-risk` | `false` | Record accepted advisory high-risk surface evidence for `command: finalize-review` |
| `reviewed-by` | empty | Optional newline-separated reviewer names for `command: finalize-review` |
| `evidence-ref` | empty | Optional newline-separated evidence references for `command: finalize-review` |
| `html-report` | empty | Optional target-relative HTML report path; POSIX and Windows absolute/rooted paths are rejected |
| `json-report` | empty | Optional target-relative audit, sync, verify, report, release-check, finalize-review, or migrate-state JSON report path; POSIX and Windows absolute/rooted paths are rejected |
| `markdown-report` | empty | Optional target-relative Markdown report path for `command: report` or `command: release-check`; POSIX and Windows absolute/rooted paths are rejected |

Report paths must be relative and stay inside `target`. Absolute paths and
traversal outside the target repository are rejected.

## Outputs

| Output | Purpose |
| --- | --- |
| `overall-score` | Harness score from 0 to 100 |
| `bottleneck` | Lowest-scoring harness domain |
| `report-json` | Target-relative JSON report path when requested |
| `report-html` | Target-relative HTML report path when requested |
| `report-markdown` | Target-relative Markdown report path when requested |
| `changed-files` | Number of files written by `init`, applied `update`, applied `finalize-review`, or applied `migrate-state` |
| `verify-verdict` | Verify verdict when `command` is `verify` |
| `verify-summary` | Target-relative compact verify evidence JSON path when requested |
| `readiness-verdict` | Readiness verdict when `command` is `sync`, `report`, or `release-check` |
| `sync-exit-code` | Sync readiness exit code when `command` is `sync` |
| `docs-fanout-verdict` | Docs fan-out verdict when `command` is `report` or `release-check` |
| `release-verdict` | Release-check verdict when `command` is `release-check` |

Report path outputs use forward slashes on every runner so workflow consumers
can handle them consistently across Windows and POSIX jobs.

When `GITHUB_STEP_SUMMARY` is available, the Action writes a concise Markdown
summary. `command: report` summarizes readiness, accepted high-risk surface
count, structured review-surface status counts, audit score, drift, docs
fan-out, verify evidence, effectiveness evidence, instruction quality,
skill wiring, unresolved actionable review work, accepted advisory inventory,
first-agent lifecycle, maturity level, feature state, observability, index
adapters, repo-map component/source counts, and SBOM file count.
`command: release-check` summarizes the release verdict, audit score,
readiness, accepted high-risk surface count, verify evidence, maturity level,
skill wiring, feature state, observability, and individual release gates.
`command: finalize-review` summarizes dry-run/apply mode, planned writes,
changed files, high-risk surface count, and whether high-risk acceptance is
still missing.
`command: migrate-state` summarizes dry-run/apply mode, legacy state files
found, planned writes, changed files, and truncated excerpts.
`command: sync` includes readiness, warning, review-required, structured
review-surface status, accepted high-risk surface, runnable-check,
instruction-quality, skill-wiring, and first-agent lifecycle counts.

## Version Pinning

For production workflows, pin this Action and all other third-party Actions to a
full-length commit SHA. A release tag such as `@v1` is acceptable for quick
evaluation, but release-critical checks should use an immutable SHA after
reviewing the release.

Audit-only workflows should also set `persist-credentials: false` on
`actions/checkout`, as shown above. Workflows that intentionally push branches
or tags need their own reviewed credential path.
