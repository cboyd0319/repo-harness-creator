# Verify JSON Contract

Status: proposed

This document defines the planned `harnessforge verify --json` report contract.
It is a design contract, not a promise that command execution exists today.

## Purpose

`verify --json` will report project verification checks in a stable
machine-readable shape. It is separate from:

- `audit --json`, which scores harness structure.
- `inspect --readiness --json`, which reports static readiness.
- `sync --check --json`, which wraps readiness with CI-oriented exit codes.

The first implementation should make project checks inspectable before it makes
them executable.

## Execution Boundary

Default mode: plan.

Default mode MUST NOT run target repository commands. It should report detected
or explicitly provided checks, source, platform applicability, and why each
check is planned, skipped, or blocked.

Command execution requires an explicit run mode. The eventual explicit run mode
must be opt-in, visible in the JSON payload, and documented in the CLI help
before it is enabled.

Non-goals for the first implementation:

- No hidden shell execution.
- No package installation.
- No network access.
- No automatic remediation.
- No harness scoring. Use `audit --json` for that.
- No readiness/drift exit-code behavior. Use `sync --check` for that.

## Planned Commands

Initial plan-only shape:

```bash
harnessforge verify --target <repo> --json
harnessforge verify --target <repo> --json --command "<repo-owned check>"
```

Future explicit execution shape:

```bash
harnessforge verify --target <repo> --json --run
```

The future `--run` flag is intentionally not part of this implementation slice.

## Exit Codes

Plan mode exit codes are about whether the report could be produced:

| Code | Meaning |
| ---: | --- |
| 0 | JSON report was produced |
| 2 | CLI usage, invalid target, unsafe command, or internal report error |

Future run mode exit codes should represent execution outcome:

| Code | Meaning |
| ---: | --- |
| 0 | Required checks passed |
| 1 | At least one required check failed or timed out |
| 2 | Checks were blocked, unsafe, or could not be started |

## JSON Shape

The schema lives at [verify-json.schema.json](verify-json.schema.json). A
representative plan-mode payload lives at
[verify-json-example.json](verify-json-example.json).

Top-level fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `schemaVersion` | yes | Stable schema identifier. Current value: `harnessforge.verify.v1` |
| `target` | yes | Target metadata without unredacted local absolute paths |
| `mode` | yes | `plan` or future `run` |
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
| `exitCode` | yes | Integer exit code in run mode, otherwise `null` |
| `durationMs` | yes | Runtime duration in milliseconds in run mode, otherwise `null` |
| `message` | yes | Short explanation for humans and CI logs |
| `stdoutPreview` | yes | Redacted and capped stdout preview, or `null` |
| `stderrPreview` | yes | Redacted and capped stderr preview, or `null` |

## Privacy And Safety

The report must not include secrets, environment dumps, credentials, or
unredacted home-directory paths. Output previews must be capped, redacted, and
safe to store in CI artifacts.

Commands must be represented as data before execution. Future run mode must use
explicit subprocess argument lists where practical, a target-relative working
directory, bounded timeout behavior, and clear platform labels.

## Implementation Notes

The implementation should reuse existing detection and readiness data before
adding new verification discovery logic. The first useful version can map
`ProjectProfile.verification_commands` into plan-mode checks.

Before enabling run mode, add tests for:

- no command execution in plan mode
- explicit opt-in for execution
- exit code mapping
- timeout behavior
- stdout and stderr redaction
- missing verification commands
- Windows and POSIX path handling
- generated manifest command sources
