# Usage

This document is the CLI workflow guide. See [Installation](installation.md)
for setup and [Capabilities](capabilities.md) for the full product boundary.

## Normal Flow

The normal flow is guide, inspect as needed, preview, generate, audit:

```bash
harnessforge quickstart --target /path/to/repo
harnessforge init --target /path/to/repo --dry-run
harnessforge init --target /path/to/repo
harnessforge audit --target /path/to/repo --min-score 85
```

`quickstart` reports detected project context, readiness, source-of-truth
systems, preserved existing files, planned generated files, generated review
placeholders, and the safest next commands.

After `init`, the generated canonical agent instruction routes the first agent
session to `docs/harness/state/first-agent-task.md` and the generated
`.agents/skills/harness/SKILL.md` skill. Those review-required files give the
agent a repo-local zero-install path for deepening the harness with
repo-specific analysis before unrelated feature work.

## Inspect And Index

Inspect a repository before writing anything:

```bash
harnessforge inspect --target /path/to/repo
harnessforge inspect --target /path/to/repo --json
```

Build a read-only structural index for a large existing repo:

```bash
harnessforge index --target /path/to/repo --json
harnessforge index --target /path/to/repo --max-files 20000 --json
```

The default index scans up to 4,000 files for fast first-pass analysis. Use
`--max-files` for larger repositories. The JSON report also states when the
bounded component inventory was truncated, so humans can add important omitted
boundaries to `docs/harness/boundaries/component-inventory.md`.

`index --json` includes a compact `repoMap` built from the structural index:
primary languages, component candidates, source-of-truth docs, manifest kinds,
entrypoints, boundary examples, verification commands, review-required files,
unknowns, and existing SBOM evidence. It does not summarize private code or run
target commands.

Existing SPDX or CycloneDX-style SBOM files are detected and cited under
`sbom`. HarnessForge does not generate SBOMs during normal `init`, `inspect`,
`index`, `sync`, or `report` flows.

## Session And Planning

Get a compact restart snapshot for an existing repo:

```bash
harnessforge session --target /path/to/repo
harnessforge session --target /path/to/repo --json
```

Map changed files to a read-only verification plan:

```bash
harnessforge plan --target /path/to/repo --since HEAD
harnessforge plan --target /path/to/repo --since HEAD --json
```

## Unified Report

Compose the current read-only harness signals into one review artifact:

```bash
harnessforge report --target /path/to/repo
harnessforge report --target /path/to/repo --since HEAD
harnessforge report --target /path/to/repo --json
harnessforge report --target /path/to/repo --json-report docs/harness/evidence/report-YYYY-MM-DD.json
harnessforge report --target /path/to/repo --markdown-report docs/harness/evidence/report-YYYY-MM-DD.md
```

`report` combines readiness, structural audit score, generated drift,
structural index summary, stored verify evidence, stored effectiveness
evidence, first-agent task lifecycle evidence, platform contract, and docs
fan-out routing status. It also includes instruction-quality and context-budget
signals for startup instruction files plus the compact repo-map summary from
`index`. It is read-only by default, does not run target repository commands,
and writes files only when a target-relative `--json-report` or
`--markdown-report` path is supplied.

Use `--require-verify-evidence` when the report should include release-gate
verify evidence blockers. Use `--command` when detection cannot infer
repo-owned verification commands; report mode records the command as readiness
context but does not execute it. Use `--since` to add read-only docs fan-out
analysis for changed files since a git ref. Add
`--require-docs-fanout-budget` when an over-budget docs fan-out or duplicated
durable fact block should return a blocking report status.

## Readiness And Sync

`inspect --readiness` and `sync --check` are static and read-only. They do not
run target repository commands and do not write files.

```bash
harnessforge inspect --target /path/to/repo --readiness
harnessforge inspect --target /path/to/repo --readiness --json
harnessforge sync --check --target /path/to/repo
harnessforge sync --check --target /path/to/repo --json
harnessforge sync --check --target /path/to/repo --require-verify-evidence
```

Readiness reports:

- `verdict`: `ready`, `warning`, or `blocked`
- `blockedReasons`
- `warnings`
- `nextActions`
- `sourceOfTruth`
- `runnableChecks`
- `generatedDrift`
- `reviewRequired`
- `configPrecedence`
- `workflowInventory`
- `workItemInventory`
- `contextBudget`
- `instructionQuality`
- `governanceInventory`
- `effectivenessInventory`
- `verifyEvidence`

`sync --check` wraps the same readiness report in a CI-friendly command with
stable exit codes:

| Verdict | Exit code | Meaning |
| --- | ---: | --- |
| `ready` | 0 | No blockers, warnings, review-required surfaces, or generated drift were detected |
| `warning` | 1 | The repo can be inspected, but drift or review-required surfaces need human attention |
| `blocked` | 2 | HarnessForge could not identify a safe verification path or another blocking condition exists |

For spec-driven repos, readiness also reports static quality gaps such as
unresolved clarification markers, incomplete requirement checklists, missing
plan/task artifacts, weak FR/SC traceability, tasks without explicit file
paths, and workflow surfaces that need review.

Workflow inventory is advisory. It detects `.github/workflows/`,
`aspec/workflows/`, and `workflows/` TOML/YAML files, then reports visible
setup, teardown, remediation, push, pull-request, CI polling, and credential
surfaces. Work-item inventory reports templates and concrete work-item files
without adopting ASPEC or AWMAN formats as generated defaults.

Context budget is also advisory. It reports instruction-file size and repeated
instruction blocks across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot
instructions so teams can keep router files compact and avoid wasting agent
context on duplicated guidance.

Instruction quality is advisory. It reports startup instruction signal,
required-section coverage, placeholder noise, word/line/byte budget status, and
largest instruction surfaces. Budgets use warning mode so teams can review
oversized or low-signal instructions without making HarnessForge the target
repo's canonical policy.

Governance inventory is advisory as well. It reports MCP configs, agent
settings, agent skills, agent plugin manifests, installer scripts, hooks,
devcontainers, sandbox configs, agent setup workflows, and environment template
or local env files as review surfaces without reading or exposing secret
values.

Verify evidence inventory is advisory. It detects target-contained
`docs/harness/evidence/verify*.json` reports, identifies the latest report,
flags invalid, failed, blocked, timed-out, or stale evidence, and keeps that
separate from structural `audit` scoring and real-agent effectiveness claims.
Use `--require-verify-evidence` with `inspect --readiness` or `sync --check`
to turn this into an explicit release gate. Gate mode requires at least one
valid stored run-mode report, blocks on any invalid verify report, and requires
the latest valid report to be fresh, passed, and free of failed, blocked,
timed-out, or error summary counts.

## Verify Project Checks

HarnessForge has a `verify --json` report for project checks. Default plan mode
maps detected or explicitly provided verification commands into a stable JSON
shape without running target repository commands. Explicit run mode executes
those checks and records exit codes, durations, capped stdout/stderr previews,
and timing metadata.

Report planned project verification checks without running them:

```bash
harnessforge verify --target /path/to/repo --json
harnessforge verify --target /path/to/repo --json --command "python -m pytest"
```

Run project verification checks explicitly:

```bash
harnessforge verify --target /path/to/repo --json --run
harnessforge verify --target /path/to/repo --json --run --timeout-seconds 120
harnessforge verify --target /path/to/repo --run --json-report docs/harness/evidence/verify-YYYY-MM-DD.json
```

Command execution is explicit opt-in through `--run`. Run mode uses argument
lists rather than a shell, rejects shell control syntax, runs from the target
repository root, and applies a per-command timeout. Use `--json-report` with a
target-relative path to write the same verify payload to a file without shell
redirection.

See [harness/feedback/verify-json-contract.md](harness/feedback/verify-json-contract.md),
[harness/feedback/verify-json.schema.json](harness/feedback/verify-json.schema.json),
and
[harness/feedback/verify-json-example.json](harness/feedback/verify-json-example.json).

## Effectiveness Evidence

Assess stored effectiveness evidence before making benchmark claims:

```bash
harnessforge effectiveness --target /path/to/repo --json
harnessforge effectiveness --target /path/to/repo --evidence docs/harness/evidence/effectiveness-YYYY-MM-DD.json --json
```

`harnessforge effectiveness --json` is the read-only assessor for the proposed
evidence contract. It scans target-contained
`docs/harness/evidence/effectiveness*.json` reports, or an explicit
target-relative `--evidence` path, and reports whether evidence is reviewable,
inconclusive, not better, or blocked. It does not run benchmarks or create a
score when representative evidence is missing.

See [harness/feedback/effectiveness-eval-contract.md](harness/feedback/effectiveness-eval-contract.md).

## Blueprint Mode

Blueprints are optional operating-model overlays for repos that need more than
the base generated harness. They are intentionally separate from `init` so a
normal harness run stays portable and does not inherit project-specific
preferences.

```bash
harnessforge blueprint list
harnessforge blueprint show agentic-app
harnessforge blueprint show agentic-app --json
harnessforge blueprint apply agentic-app --target /path/to/repo --dry-run
harnessforge blueprint apply agentic-app --target /path/to/repo
```

Built-in blueprints:

| Blueprint | Use when |
| --- | --- |
| `agentic-app` | The repo has agent runtime behavior, tool calls, model-mediated outputs, or autonomous actions |
| `spec-driven` | The repo uses specs, plans, tasks, and traceability as the source of truth |
| `web-service` | The repo exposes web apps, APIs, UI flows, or server-backed product workflows |
| `data-ml` | The repo has data pipelines, notebooks, models, benchmarks, or result artifacts |
| `security-sensitive` | The repo handles auth, secrets, permissions, infrastructure, or sensitive data |
| `workflow-automation` | The repo has CI, scheduled jobs, bots, self-heal flows, or PR automation |

`blueprint apply` writes under `docs/harness/blueprints/` and records ownership
metadata in `docs/harness/blueprints/manifest.json`. Existing blueprint files
are preserved unless `--force` is explicit. Treat generated blueprint docs as
review-required project drafts, not automatic policy.

## Generation Boundary

`init` creates missing HarnessForge-owned files. It preserves existing project
files by default:

```bash
harnessforge init --target /path/to/repo
```

Use `--dry-run` first when reviewing a new target:

```bash
harnessforge init --target /path/to/repo --dry-run
```

Use `--enhance-existing` when an existing instruction file should keep its
project text but receive a reviewed HarnessForge quality addendum:

```bash
harnessforge enhance --target /path/to/repo
harnessforge enhance --target /path/to/repo --json
harnessforge init --target /path/to/repo --enhance-existing --dry-run --json
harnessforge init --target /path/to/repo --enhance-existing
```

The addendum routes agents to the canonical harness files and adds
smallest-correct-change guidance for assumptions, speculative scope,
dependencies, simplification ceilings, and focused verification. The dry-run
JSON plan reports parsed sections, canonical section coverage, review-required
proposed edits, placeholder patch previews, duplicated instruction blocks,
local absolute paths, user-specific tool mandates, and verification conflicts
before any project-owned instruction file is changed. Patch previews are
review-only and are not applied automatically.

Use `enhance` for the review-only command surface. It reports the same existing
instruction plan without writing files. Use `init --enhance-existing` only when
you are ready to append the reviewed HarnessForge quality addendum.

Use `--force` only after reviewing the target diff:

```bash
harnessforge init --target /path/to/repo --force
```

The optional CI workflow scaffold is off by default:

```bash
harnessforge init --target /path/to/repo --with-ci-workflow
```

The generated workflow uses a manual trigger and placeholder Action pin. The CI
scaffold runs a read-only `command: sync` preflight before audit, treats
warning verdicts as advisory by default, and stops only when readiness is
blocked. `require-verify-evidence` stays `"false"` until the project has
reviewed run-mode verify evidence under `docs/harness/evidence/`. Review
permissions, triggers, branches, credential surfaces, and full-length commit
SHAs before relying on the generated workflow.

Generated harnesses also include `docs/harness/state/first-agent-task.md` and
`docs/harness/evidence/first-agent-review.json`, plus
`.agents/skills/harness/SKILL.md`. Treat them as review-required first
improvement guidance and evidence for the target repo harness, not as automatic
policy.

## Audit

```bash
harnessforge audit --target /path/to/repo
harnessforge audit --target /path/to/repo --json
harnessforge audit --target /path/to/repo --html harness-report.html
harnessforge audit --target /path/to/repo --min-score 85
```

The audit returns:

- an overall 0-100 score
- the bottleneck domain
- per-domain checks
- failed checks
- concrete recommendations

The score covers instructions, tools, environment, state, feedback, scope, and
lifecycle controls. Treat it as a harness quality signal, not as a substitute
for code review, security review, or real agent task evaluation.

## Public Repo Quality Corpus

Run the offline generated-content quality corpus:

```bash
harnessforge corpus
harnessforge corpus --json
harnessforge corpus --min-score 90
```

`corpus` uses temporary fixtures modeled on pinned popular public repositories
to test detection, stack-specific context, generated content hygiene, audit
quality, and local-path/template-token safeguards. It does not clone
repositories, use network access, run target commands, or write outside the
temporary fixture root.

## Update And Drift

Plan safe missing-file corrections without writing:

```bash
harnessforge update --target /path/to/repo
```

Apply safe missing-file corrections:

```bash
harnessforge update --target /path/to/repo --apply
```

Report generated-file drift:

```bash
harnessforge update --target /path/to/repo --drift-report
harnessforge update --target /path/to/repo --drift-report --json
```

`update --apply` creates missing generated artifacts. Existing files are left
alone unless `--force` is supplied.

## Command Reference

| Command | Purpose |
| --- | --- |
| `harnessforge quickstart` | Guide the first safe run without writing files |
| `harnessforge inspect` | Show detected project profile or readiness without writing files |
| `harnessforge index` | Build a read-only structural repo index for harness design |
| `harnessforge effectiveness` | Assess stored real-agent effectiveness evidence without running benchmarks |
| `harnessforge session` | Show a read-only restart snapshot with git, readiness, audit, and state-file status |
| `harnessforge report` | Compose readiness, audit, drift, index, and evidence into one read-only report |
| `harnessforge enhance` | Review existing instruction files without writing files |
| `harnessforge plan` | Map changed files to a read-only verification plan |
| `harnessforge sync --check` | Run a read-only CI preflight with readiness exit codes |
| `harnessforge verify` | Report planned project checks, or run them explicitly with `--run` |
| `harnessforge blueprint` | List, inspect, or apply optional review-required operating-model overlays |
| `harnessforge corpus` | Run the offline public-repo generated-content quality corpus |
| `harnessforge init` | Create missing harness artifacts |
| `harnessforge audit` | Score an existing repo harness |
| `harnessforge update` | Plan or apply safe missing-file corrections, or report generated drift |
| `harnessforge doctor` | Check local runtime support |

Run `harnessforge <command> --help` for command-specific options.

## GitHub Action

Use [action.md](action.md) for every Action input, output, and command mode,
including `command: sync` for read-only readiness preflight and
`command: verify` with read-only plan mode by default and explicit
`verify-run: "true"` execution.
