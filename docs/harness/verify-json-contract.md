# Verify JSON Contract

Status: implemented plan and explicit run mode

This document defines the `harnessforge verify --json` report contract.
Plan mode is the default. Command execution is implemented only behind the
explicit `--run` flag.

## Purpose

`verify --json` reports project verification checks in a stable
machine-readable shape. It is separate from:

- `audit --json`, which scores harness structure.
- `inspect --readiness --json`, which reports static readiness.
- `sync --check --json`, which wraps readiness with CI-oriented exit codes.

The implementation makes project checks inspectable by default and executable
only when a caller opts in.

## Execution Boundary

Default mode: plan.

Default mode MUST NOT run target repository commands. It should report detected
or explicitly provided checks, source, platform applicability, and why each
check is planned, skipped, or blocked.

Command execution requires explicit run mode. Run mode is opt-in, visible in
the JSON payload, and documented in the CLI help.

Non-goals:

- No hidden shell execution.
- No package installation.
- No network access.
- No automatic remediation.
- No harness scoring. Use `audit --json` for that.
- No readiness/drift exit-code behavior. Use `sync --check` for that.

## Benchmark And Eval Boundary

`verify --json` reports whether project checks are planned or, in explicit run
mode, whether those checks passed. It is not by itself evidence that a
generated harness improves real agent effectiveness.

Benchmark and real-agent eval reports stay separate from this contract. Use
`effectiveness-eval-contract.md` and
`effectiveness-evidence.schema.json` for that evidence. Any eval report should
state:

- the candidate harness surface under evaluation;
- the baseline and control arm;
- a metric that changes for quality reasons when the candidate changes;
- the held-out split or contamination controls;
- worst-case quality, not only average quality;
- any do-no-harm quality floor used while optimizing cost, tokens, latency, or
  tool calls;
- whether the eval is a live run, counterfactual replay, or frozen replay.

Frozen replay that cannot change quality when the candidate changes must not be
used as evidence of harness effectiveness. At most, it can support a narrower
cost or context-budget claim.

## Planned Commands

Plan-only shape:

```bash
harnessforge verify --target <repo> --json
harnessforge verify --target <repo> --json --command "<repo-owned check>"
```

Explicit execution shape:

```bash
harnessforge verify --target <repo> --json --run
harnessforge verify --target <repo> --json --run --timeout-seconds 120
harnessforge verify --target <repo> --run --json-report docs/harness/evidence/verify-<date>.json
```

Run mode executes each check from the target repository root using an argument
list, not a shell. Shell control syntax such as `&&`, `||`, pipes, and
redirection is rejected; pass each check with a separate `--command`.

Use `--json-report <target-relative-path>` to persist the verify payload inside
the target repository. POSIX and Windows absolute or rooted paths are rejected,
Windows-style relative separators are normalized, and traversal outside the
target repository is rejected.

Readiness and sync preflight can inventory stored reports under
`docs/harness/evidence/verify*.json`. This inventory is advisory: it surfaces
latest verdict, schema validity, stale reports, failed or blocked outcomes, and
timed-out checks without turning stored evidence into a hard release gate by
default.

Call `inspect --readiness --require-verify-evidence` or
`sync --check --require-verify-evidence` when stored verify evidence should be
a hard gate. Gate mode requires at least one valid stored report, blocks on any
invalid verify report, and requires the latest valid report to be run-mode,
fresh, passed, and free of failed, blocked, timed-out, or error summary counts.

## Exit Codes

Plan mode exit codes are about whether the report could be produced:

| Code | Meaning |
| ---: | --- |
| 0 | JSON report was produced |
| 2 | CLI usage, invalid target, unsafe command, or internal report error |

Run mode exit codes represent execution outcome:

| Code | Meaning |
| ---: | --- |
| 0 | Required checks passed |
| 1 | At least one required check failed or timed out |
| 2 | Checks were blocked before execution |

## JSON Shape

The schema lives at [verify-json.schema.json](verify-json.schema.json). A
representative plan-mode payload lives at
[verify-json-example.json](verify-json-example.json).

Top-level fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `schemaVersion` | yes | Stable schema identifier. Current value: `harnessforge.verify.v1` |
| `target` | yes | Target metadata without unredacted local absolute paths |
| `mode` | yes | `plan` or `run` |
| `verdict` | yes | Overall report status |
| `platform` | yes | Host and runner metadata useful for platform contracts |
| `execution` | yes | Whether commands were executed and timing metadata |
| `summary` | yes | Count of checks by final status |
| `checks` | yes | Ordered verification check records |
| `blockedReasons` | yes | Conditions preventing useful verification |
| `warnings` | yes | Non-blocking review items |
| `artifacts` | yes | Future report artifacts, if any |

Check fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable report-local identifier |
| `label` | yes | Human-readable check name |
| `command` | yes | Display command string |
| `source` | yes | Detection source, such as `detected`, `explicit`, `manifest`, or `generated` |
| `workingDirectory` | yes | Target-relative working directory |
| `required` | yes | Whether failure should affect run-mode exit status |
| `status` | yes | `planned`, `skipped`, `blocked`, `passed`, `failed`, `timed_out`, or `error` |
| `exitCode` | yes | Integer exit code when the process exits, otherwise `null` |
| `durationMs` | yes | Runtime duration in milliseconds in run mode, otherwise `null` |
| `message` | yes | Short explanation for humans and CI logs |
| `stdoutPreview` | yes | Redacted and capped stdout preview, or `null` |
| `stderrPreview` | yes | Redacted and capped stderr preview, or `null` |

## Privacy And Safety

The report must not include secrets, environment dumps, credentials, or
unredacted home-directory paths. Output previews must be capped, redacted, and
safe to store in CI artifacts.

Commands are represented as data before execution. Run mode uses explicit
subprocess argument lists, the target repository root as the working directory,
bounded per-command timeout behavior, and clear platform labels.

## Implementation Notes

The implementation should reuse existing detection and readiness data before
adding new verification discovery logic. The first useful version can map
`ProjectProfile.verification_commands` into plan-mode checks.

Run mode has tests for:

- no command execution in plan mode
- explicit opt-in for execution
- exit code mapping
- timeout behavior
- missing verification commands
- stdout and stderr previews

Future focused coverage should add Windows path parsing and generated manifest
command-source cases when those sources become executable inputs.
