# Harness Operations

Status: live

This repo uses its own harness as product evidence. The harness makes the CLI
work restartable, scoped, verifiable, and portable across Python 3.13+, macOS
15+, Windows 11+, and Ubuntu 22.04+.

## Goal

Make HarnessForge a practical default for adding agent-ready operating
surfaces to any repository while staying honest about what the tool can prove.
The CLI can score structure. Real effectiveness still requires representative
agent sessions.

## Pre-Release Product Contract

HarnessForge is alpha/pre-release, has not been deployed, and has no external
users. Prefer the clean current product contract over compatibility with
earlier local generated outputs, report schemas, manifest formats, docs
layouts, CLI shapes, or Action behavior. Add migration shims only after a
maintainer declares a release boundary or records a temporary local evaluation
bridge with removal criteria.

## Five Core Subsystems

HarnessForge follows the Walking Labs `harness-creator` core model:
instructions, state, verification, scope, and lifecycle. Missing any one of
these makes a coding-agent harness incomplete. Tools, environment metadata,
research ledgers, reports, Actions, and policy presets are support surfaces.
They must serve one of the five core subsystems, or stay optional and
reviewable.

| Subsystem | This Harness Provides | Review Question |
| --- | --- | --- |
| Instructions | `AGENTS.md` plus short platform routers | Does the agent see purpose, stack, first-run commands, hard constraints, and links to detail? |
| State | `feature_list.json`, `current-state.md`, `docs/roadmap.md` | Can a new session see what is done, in progress, blocked, and next? |
| Verification | Tests, verification matrix, local checks, audit, and release gates | Are checks explicit, runnable, and prioritized before broader process? |
| Scope | Change contract, component inventory, security boundaries, and feature dependencies | Does the harness prevent overreach, drive-by work, and half-finished changes? |
| Lifecycle | `current-state.md`, clean-state checklist, first-agent review, and evidence handoff | Can the next session restart without chat history or stale assumptions? |

Treat verification as the highest-return subsystem. When agent output is weak,
fix missing, stale, or vague checks before adding more instructions or support
surfaces.

`harnessforge audit` scores seven implementation buckets for diagnostic
granularity and reports how each maps onto these five core subsystems. Five map
directly (`instructions`, `state`, `feedback` as the verification core, `scope`,
`lifecycle`); `tools` and `environment` are support surfaces, not peer core
subsystems. The audit emits this mapping as `coreModel` in JSON and as inline
labels in formatted output. The audit score is structural conformance, not proof
of real-agent effectiveness, and a higher score is not automatically the goal: a
correctly minimal harness can be complete. See
[`research/harness-engineering-foundations.md`](research/harness-engineering-foundations.md)
for the lineage, the two five-subsystem framings, the maturity ladder, and the
structure-is-not-effectiveness boundary.

## Effective Agent Boundary

The model is the LLM. The effective coding agent is the model plus the harness:
system prompts, instruction files, shell and file tools, git access, local
filesystem scope, startup scripts, verification commands, stop hooks,
lint/sensor checks, workflow permissions, and evaluator loops. Changing any of
these changes effective agent behavior. Treat those changes as product changes
with scope, verification, and rollback.

## Practical Harness Map

This map lists implementation surfaces that support the five core subsystems.
Do not treat every row as a new mandatory subsystem.

| Domain | Artifact | Purpose |
| --- | --- | --- |
| Instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | Startup path, hard requirements, DRY and YAGNI implementation discipline, verification, and platform routing |
| Tools | `harnessforge`, `action.yml`, `init.sh`, `init.ps1`, `scripts/check_pins.py` | Creation, audit, update, CI action, local checks, and pin enforcement |
| Environment | `pyproject.toml`, CI matrix, `component-inventory.md`, `dependency-change-policy.md` | Python, OS, package, component, and Action support contract |
| State | `feature_list.json`, `current-state.md`, `evidence-log.md`, `docs/roadmap.md`, `authoritative-facts.md` | Feature state, current objective, evidence, docs routing, and restart state |
| Feedback | tests, self-audit, CI, `first-agent-task.md`, `verification-matrix.md`, `sensor-registry.md`, `evaluator-rubric.md`, `verify-json-contract.md`, `effectiveness-eval-contract.md`, research refresh | First-agent harness improvement, deterministic quality checks, sensor ownership, machine-readable verification output, benchmark-claim boundaries, and source drift signal |
| Research | `research/README.md`, `sources.md`, `research-sources.json`, `source-record.schema.json`, `source-record-example.json` | Research directory map, fixed research allowlist, source provenance, and project-owned source records |
| Scope | `docs/harness/boundaries/change-contract.md`, `security-boundary-map.md`, `feature-privacy-labels.json` | Acceptance, rollback, security, and data-flow discipline |
| Lifecycle | `current-state.md`, `clean-state-checklist.md`, `quality-document.md`, `release-controls.md`, `self-healing.md`, entropy control | Restart, roadmap freshness, release readiness, recurring maintenance, and reviewed automation |

## Operating Loop

1. Read `AGENTS.md`.
2. Use `first-agent-task.md` when a newly generated harness needs its first
   repo-specific improvement pass.
3. Check `feature_list.json` and `current-state.md`.
4. Check `docs/roadmap.md` when selecting, deferring, or reshaping backlog,
   release-prep, or product-scope work.
5. Check `authoritative-facts.md` before updating more than one durable doc or
   state file for a routine change.
6. Check `component-inventory.md` when a task touches nested project boundaries.
7. Use `change-contract.md` for non-trivial behavior or template changes.
8. Implement the smallest coherent slice.
9. Review `sensor-registry.md` when adding, deleting, or promoting checks.
10. Run `./init.sh` or the narrowest relevant subset.
11. Run `python scripts/check_pins.py --root .` for dependency, Action, or
   workflow changes.
12. Run `python scripts/refresh_research.py --root . --check` for research
   source ledger or source-doc changes.
13. Use `clean-state-checklist.md` before ending non-trivial sessions.
14. Update only the state file that owns the changed fact; do not update
    `feature_list.json`, `current-state.md`, and the evidence log as a routine
    bundle.

## Assessment And Updates

Use:

```bash
harnessforge quickstart --target .
harnessforge index --target . --json
harnessforge index --target . --max-files 20000 --json
harnessforge effectiveness --target . --json
harnessforge session --target .
harnessforge report --target .
harnessforge enhance --target .
harnessforge migrate-state --target .
harnessforge plan --target . --since HEAD
harnessforge corpus --min-score 90
harnessforge audit --target .
harnessforge update --target .
harnessforge sync --check --target . --json
harnessforge verify --target . --json
```

`quickstart` is a read-only guided first-run view. It composes detection,
readiness, dry-run generation planning, preserved-file reporting, review
placeholder reporting, and next commands without writing files.
Use `quickstart --interactive --json` when a review needs the same decisions
as reproducible CLI flags. Non-JSON `--interactive` prints the dry-run summary
first, skips prompts without a TTY, and asks before writing in a real terminal.

`index --json` is a read-only structural repo map. It reports file class,
language, manifest, component, source-of-truth, entrypoint, generated, vendor,
workflow, SBOM, review-required, compact `repoMap`, and `fileCoverage` signals
without command execution, writes, local absolute paths, code excerpts,
embeddings, or network access. For git checkouts, `fileCoverage` compares the
bounded scan against `git ls-files` by category so large-repo reports do not
look complete when the scan is capped. Existing SPDX and CycloneDX-style SBOM
files are cited as evidence; HarnessForge does not generate SBOMs in normal
read-only flows. The default file scan limit is 4,000 files; pass
`--max-files` for deeper large-repo analysis. Component inventories remain
bounded and report truncation so omitted boundaries can be reviewed and added
manually.

`effectiveness --json` is a read-only assessor for stored real-agent or
benchmark evidence. It scans target-contained
`docs/harness/evidence/effectiveness*.json` reports, or an explicit
target-relative `--evidence` path, and reports whether evidence is reviewable,
inconclusive, not better, or blocked without running benchmarks or turning
structural scores into performance claims.

`migrate-state` is dry-run by default. It plans consolidation from old root
`progress.md` and `session-handoff.md` files into `current-state.md`; apply
mode requires confirmation, preserves legacy files, and does not run target
commands.

`session` is a read-only restart snapshot. It reports git state when available,
detected stack, readiness verdict, harness audit score when a harness surface is
present, state-file presence, and next actions without running target commands.

`report` is a read-only unified harness status artifact. It composes readiness,
audit, generated drift, structural index summary, verify evidence,
effectiveness evidence, first-agent task status, platform contract,
instruction quality, skill wiring, feature state, observability, index-adapter
status, review-work classification, nested instruction-scope candidates, and
docs fan-out without running target commands. It also reports policy preset
recommendations and SBOM adapter status while keeping preset application,
nested instruction writes, and SBOM generation explicit opt-ins. Use
`--json-report` or `--markdown-report` with a target-relative path to persist
review evidence. Stable report fields are documented in
`feedback/report-json-contract.md`.

`corpus` is an offline generated-content quality gate. It creates temporary
fixtures modeled on pinned popular public repositories, runs detection,
generation, indexing, and audit against those fixtures, and reports whether
stack-specific context, generated content, local-path hygiene, and quality
checks stay above the current threshold. It does not clone repositories, use
network access, execute target commands, or write outside the temporary root.

For release-prep field evidence against real large public repositories, use
`scripts/analyze_large_public_repos.py`. It is repo-local, clones only with
`--clone`, stores checkouts under ignored `.harnessforge/large-public-repos/`,
and reports product gaps such as scan truncation and nested `AGENTS.md`
candidate scopes. It is not part of generated target harnesses or the
composite Action.

`plan` is a read-only diff-aware verification planner. It uses `git diff` to
map changed files to detected or explicit project verification checks, but it
does not run those checks.

`update` reports recommended safe corrections unless `--apply` is passed.
Existing files are skipped unless `--force` is passed.

Before enhancing project-owned instruction files, run
`harnessforge enhance --target .` or
`harnessforge enhance --target . --json`. The plan reports proposed addendum
writes, canonical section coverage, review-required section/finding cleanup
edits, placeholder patch previews, and findings for duplicate instructions,
local absolute paths, user-specific tool mandates, and verification conflicts
before files are changed. Patch previews are review-only and are not applied
automatically. Use `harnessforge init --target . --enhance-existing` only when
you are ready to append the reviewed HarnessForge quality addendum.

`verify --json` defaults to read-only plan mode and is documented in
`verify-json-contract.md`, with schema and example artifacts beside it. It
reports detected or explicit checks without running target repository commands.
Use `verify --json --run` only when project checks should execute; run mode
records exit codes, durations, capped stdout and stderr previews, and timing
metadata. Use `--json-report <target-relative-path>` to persist the full
payload without shell redirection. Use
`--evidence-summary <target-relative-path>` for compact stored evidence that
omits stdout and stderr previews while keeping command status, exit code,
duration, verdict, and summary counts.

Project-owned source records use `source-record.schema.json` and
`source-record-example.json`. Keep them separate from the fixed
`research-sources.json` allowlist.

`docs/roadmap.md` is the accepted product roadmap and backlog boundary. Update
it when brainstorming decisions become accepted work, when roadmap items are
implemented or intentionally deferred, and when release prep scope changes.

Readiness also includes advisory workflow and work-item inventory. Treat
detected setup, teardown, remediation, push, pull-request, CI polling, and
credential surfaces as review inputs before agent automation relies on them.
It also includes advisory context-budget data for instruction file size and
duplicated router text.
Governance inventory reports MCP configs, agent settings, agent skills, agent
plugin manifests, installer scripts, hooks, devcontainers, sandbox configs,
agent setup workflows, and environment files as review surfaces before agents
receive tool or runner access.
Verify evidence inventory reports target-contained
`docs/harness/evidence/verify*.json` files, latest verdicts, invalid schemas,
failed or blocked outcomes, timed-out checks, and stale reports as advisory
readiness signals.
Use `--require-verify-evidence` with `inspect --readiness` or `sync --check`
when release preflight should block unless stored verify evidence is valid,
fresh, run-mode, passed, and free of failed, blocked, timed-out, or error
summary counts.

Effectiveness inventory reports visible eval specs, benchmark files, scorer
scripts, result logs, and frontier files as review surfaces before anyone
claims a harness improves agent performance. It is a static inventory only.
Use `effectiveness-eval-contract.md` for the evidence boundary, with
`effectiveness-evidence.schema.json` and
`effectiveness-evidence-example.json` for the machine-readable claim shape.

The GitHub Action in `action.yml` exposes the same behavior to other
repositories. Keep it wired to the Python library instead of duplicating logic
in shell.
The Action also exposes `command: sync` as a read-only readiness preflight with
the same exit codes as the CLI and optional `require-verify-evidence` gating.
The optional generated CI workflow scaffold uses that sync preflight before
audit, keeps verify-evidence gating off by default, treats warning verdicts as
advisory, and stops only when readiness is blocked.

## Bottleneck And Harness Debt

Harness rots like code. Audit it regularly, keep stale instructions and unused
sensors out, and pay down harness debt when failures repeat.

When evaluating a harness change, controlled-variable exclusion tests can help:
hold the model and task fixed, remove one subsystem at a time, and observe the
performance drop. Use that as supporting evidence only. Locate the real
bottleneck from failure records and attribution: unclear task, missing context,
unreproducible environment, missing feedback, broken state, or tool access that
is too narrow or too broad.

Use the entrypoint no-env mode for credential-free local verification when
reviewing trust-boundary changes.

The self-healing workflow definition is parked as
`.github/workflows/harness-self-heal.yml.disabled` during alpha/pre-release to
avoid scheduled runner cost while commits are frequent. If re-enabled later, it
is HarnessForge-maintainer automation for this repository only.

That parked workflow is separate from the published composite Action and from
the optional CI scaffold generated into target repositories.

## When To Add Harness

Add harness when a repeated failure, hidden setup step, source-of-truth conflict,
platform concern, or verification gap can be turned into a small durable guide
or sensor. Do not add ceremony for taste alone.
