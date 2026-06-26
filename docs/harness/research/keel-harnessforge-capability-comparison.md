# Keel And HarnessForge Capability Comparison

Reviewed: 2026-06-26 UTC.

Scope:

- Keel local repo at commit `db0c542 prepare v0.0.1 release (#5)`.
- HarnessForge local repo at commit `e15997d Plan Keel-derived harness enhancements`.

This is a product comparison for HarnessForge planning. It is not a generated
target-harness contract.

## Evidence Used

Keel evidence:

- CLI help from `go run ./cmd/keel --help` and subcommand help.
- Root docs: `README.md`, `ROADMAP.md`, `WALKTHROUGH.md`, `DISTRIBUTION.md`,
  and `RELEASES.md`.
- Source files under `cmd/keel/`, `internal/`, `keel/`, and
  `assets/keel-template/`.
- Test inventory: 133 Go test functions across 14 internal package test files.
- Verification: `go test ./...` passed during the prior mining pass.

HarnessForge evidence:

- CLI help from `harnessforge --help` through `harnessforge.cli`.
- Root docs: `README.md`, `docs/capabilities.md`, `docs/usage.md`,
  `docs/action.md`, and `docs/roadmap.md`.
- Source files under `src/harnessforge/`.
- Test inventory: 322 Python test functions across 14 test files.
- Verification in the prior planning pass: research check, diff hygiene, and
  self-audit `100/100`.

## Executive Summary

Keel and HarnessForge are both agent-harness tools, but they sit at different
layers.

Keel is an execution harness for one project. It installs rules, slash
commands, phase files, gates, snapshots, sessions, hooks, and ledgers so an
agent builds one phase at a time. Its strongest capabilities are phase
discipline, gate writing, rollback DAGs, event ledgers, token/tool reporting,
and deterministic deliverable planning.

HarnessForge is a harness factory, assessor, and evidence compiler for many
project shapes. It detects repository structure, generates compact repo-owned
harness files, audits structural quality, reports readiness and maturity,
reviews existing instructions, assembles release evidence, runs an offline
fixture corpus, and exposes the same library through a composite GitHub
Action. Its strongest capabilities are read-only repo understanding, generated
target-harness quality, Action integration, report breadth, security/privacy
boundaries, policy blueprints, and release evidence.

The product lesson is direct: HarnessForge should not copy Keel's phase runtime
as a default. It should import Keel-shaped signals as optional or read-only
analysis: stale generated-surface detection, work-unit plan quality, evidence
import for existing gates and ledgers, optional deliverable-DAG planning, and a
phase-gated regression fixture.

## Boundary Model

| Boundary | Keel | HarnessForge | Product Reading |
| --- | --- | --- | --- |
| Primary job | Govern agent execution one phase at a time. | Create, assess, update, and report on repo harnesses. | Keel owns a target execution loop; HarnessForge owns harness surfaces and evidence. |
| Default posture | Installs a runtime-like harness with `.agent/`, `keel/`, docs, scripts, hooks, sessions, and agent commands. | Generates compact repo-owned harness files and defaults most analysis to read-only. | HarnessForge has safer defaults for arbitrary repos; Keel has stronger execution state once adopted. |
| Canonical state | `BUILD_MANIFEST.yaml` plus `.agent/phase_gates/` and session ledgers. | `feature_list.json`, `current-state.md`, `docs/harness/`, generated manifest, stored reports, and target evidence. | Different state models. Keel state is phase execution; HarnessForge state is harness readiness and product/repo maintenance. |
| Agent interaction | Slash commands such as `/keel-run`, `/new-feature`, and `/rollback-phase`. | Agent instruction files, repo-local harness skill, first-agent task, and optional CLI/Action use. | Keel gives agents executable rituals; HarnessForge gives agents durable repo guidance and checks. |
| Default command execution | Agent is expected to run project phase checks. Keel CLI writes gates and ledgers. | Read-only by default; `verify --run` and apply modes require explicit confirmation. | HarnessForge should keep this difference. |
| Release posture | Published v0.0.1 with Homebrew flow. | Alpha/pre-release with no external users and no compatibility boundary. | Keel is release-oriented; HarnessForge is still optimizing product contract. |

## CLI Command Matrix

### Keel Commands

| Keel command | Purpose | HarnessForge overlap | HarnessForge gap or difference |
| --- | --- | --- | --- |
| `keel init` | Bootstrap Keel harness, discover/copy PRD, detect/confirm tech stack, install tracking hooks by default. | `harnessforge quickstart`, `init`, `update`, and `enhance-existing` generate or preview harness surfaces. | HarnessForge does not create `.agent/`, phase runtime, slash commands, or hooks by default. |
| `keel current-phase` | Derive next phase from manifest and passed or failed gate files. | `harnessforge session`, `report`, and feature-state report summarize state. | HarnessForge does not have phase-number execution state. |
| `keel verify` | Verify Keel required files, rules, commands, phase files, phase gates, stale references. | `harnessforge audit`, `sync --check`, `verify`, `report`, skill wiring, generated drift, instruction quality. | HarnessForge verifies broader harness health but does not validate Keel-specific phase schema unless added as evidence import. |
| `keel plan-phases` | Build deterministic phases from `docs/TDD.md` deliverables DAG. | `harnessforge plan` maps changed files to checks; `enhance` could host advisory planning. | HarnessForge lacks deliverable-DAG grouping today. This is a strong optional candidate. |
| `keel phase start` | Emit phase-start event and capture pre-phase manifest and stash. | No direct equivalent. | HarnessForge intentionally avoids execution lifecycle hooks by default. |
| `keel phase complete` | Emit phase-completed event. | No direct equivalent. | HarnessForge can import such evidence later, not emit it. |
| `keel phase failed` | Emit phase-failed event with optional reason. | Report/readiness can surface failed stored evidence. | HarnessForge does not write failure gates today. |
| `keel phase close` | Write gate JSON, rollback DAG, build ledger, audit log, JSONL audit/run log, and session event. | HarnessForge `verify --evidence-summary`, report evidence, first-agent review finalization. | Keel has stronger phase completion artifact generation; HarnessForge has broader evidence aggregation. |
| `keel rollback` | Dry-run or confirmed rollback of a phase and downstream phases from rollback DAGs. | HarnessForge blueprints and change contracts require rollback guidance. | HarnessForge does not execute target rollback and should not by default. |
| `keel rollback write-dag` | Derive rollback DAG from a passed gate. | No direct equivalent. | Candidate for import or advisory checks, not generation. |
| `keel session start/current/list/end` | Manage active local session metadata. | `harnessforge session` is a read-only restart snapshot. | Same name, different meaning: Keel mutates and tracks sessions; HarnessForge summarizes repo restart state. |
| `keel report session/phase/tokens/tools/debug` | Query active session event ledger. | `harnessforge report` composes harness readiness, audit, evidence, maturity, observability, and more. | Keel reports execution telemetry; HarnessForge reports harness health and stored evidence. |
| `keel merge-feature` | Merge feature workspace manifest into project manifest. | HarnessForge feature-state reporting and blueprint mode. | HarnessForge does not maintain a project build manifest or feature queue. |
| `keel event append` | Append session events from hooks or commands. | No writer equivalent. | HarnessForge should only import target-contained ledgers if present. |
| Cobra `completion` | Generate shell completion. | No direct equivalent. | Low-priority CLI polish candidate for HarnessForge, not harness-specific. |

### HarnessForge Commands

| HarnessForge command | Purpose | Keel overlap | Keel gap or difference |
| --- | --- | --- | --- |
| `inspect` | Read-only profile and readiness check. | Keel preflight captures some context. | Keel lacks broad readiness inventory and read-only project profile. |
| `index` | Read-only structural repo index with file coverage, component candidates, repo map, SBOM evidence, nested instruction candidates. | Minimal overlap with Keel detect. | Keel lacks structural index, file coverage, nested instruction planning, and SBOM evidence detection. |
| `effectiveness` | Review stored real-agent or benchmark evidence. | Keel roadmap mentions evals; no implemented command. | HarnessForge has an evidence boundary for measured effectiveness. |
| `quickstart` | Guided first-run summary and reproducible decision plan without writes. | Keel `init` prompts during bootstrap. | Keel lacks a separate read-only first-run planner. |
| `corpus` | Offline public-repo fixture quality gate. | Keel has generator/template tests. | Keel lacks a public-repo-shaped generated-content corpus. |
| `enhance` | Read-only review plan for existing instruction files. | Keel installs its own rules and commands. | Keel lacks project-owned instruction review and dedupe planning. |
| `finalize-review` | Finalize first-agent review and accepted high-risk evidence through explicit apply mode. | No direct equivalent. | Keel has phase gates but no first-agent harness review lifecycle. |
| `migrate-state` | Plan/apply migration from legacy root progress files into `current-state.md`. | No direct equivalent. | Keel has a single phase state model, not legacy state migration. |
| `init` | Generate missing harness artifacts, preserve existing files, optional CI scaffold, optional enhance-existing. | Keel `init`. | HarnessForge generates broader docs and skills; Keel installs phase runtime. |
| `audit` | Score seven implementation buckets and map to five core subsystems. | Keel `verify` checks consistency. | Keel lacks structural harness scoring. |
| `update` | Plan/apply safe missing-file corrections and drift reporting. | Keel roadmap mentions upgrade; `init --force-template` can overwrite templates. | HarnessForge has safer update planning; Keel lacks version-aware upgrade. |
| `sync` | Read-only readiness preflight with stable exit codes. | Keel `current-phase` and `verify`. | Keel lacks broad generated drift, review surfaces, and evidence readiness. |
| `session` | Read-only restart snapshot. | Keel session management. | Different semantics: HarnessForge does not create sessions. |
| `report` | Unified harness status report. | Keel report. | HarnessForge report is broader; Keel report is deeper for execution telemetry. |
| `release-check` | Evidence-gated release readiness without publishing or running target commands. | Keel has release workflow for Keel itself. | Keel lacks a target harness release-readiness command. |
| `plan` | Diff-aware verification planner. | Keel plan-phases. | Keel plans build phases; HarnessForge plans checks for changed files. |
| `verify` | Plan or explicitly run project verification checks, optionally record compact evidence. | Keel verify and phase exit criteria. | HarnessForge separates plan mode from run mode and stores verify evidence. |
| `blueprint list/show/apply` | Optional operating-model packs for project classes. | Keel has fixed rules and TDD templates. | Keel lacks multi-domain policy blueprint packs. |
| `doctor` | Check local runtime support. | No direct equivalent. | Keel relies on Go build/runtime environment and install docs. |
| Composite GitHub Action | CI wrapper over audit, init, update, sync, verify, report, release-check, finalize-review, migrate-state, and doctor. | Keel has release workflow for itself, not a reusable Action. | HarnessForge has a publishable CI surface for target repos. |

## Capability-By-Capability Comparison

| Capability | Keel | HarnessForge | Overlap | Gap or Opportunity |
| --- | --- | --- | --- | --- |
| Product positioning | Controlled execution governance for AI agents. | Repo harness creation, assessment, and maintenance. | Both care about agent discipline and auditability. | Keel is narrower and deeper; HarnessForge is broader and safer for arbitrary repos. |
| Installation | Homebrew and source build from Go 1.25+. | Python package from repo clone today, composite Action, pre-release. | Both have local CLI. | HarnessForge release packaging is still a future boundary. |
| Bootstrap | Installs `keel/`, `.agent/`, `agent-rules.md`, `BUILD_MANIFEST.yaml`, scripts, phase 0 docs, Claude/Codex commands. | Generates `AGENTS.md`, platform routers, `docs/harness/`, state, scripts, skill, research/source records, optional CI workflow. | Both generate repo-owned files and preserve by default unless forced. | Keel creates a phase runtime; HarnessForge creates a harness operating surface. |
| Existing file preservation | `init` skips templates unless `--force-template`. | Existing files preserved unless `--force`; destructive/apply paths require confirmation. | Both avoid unrequested overwrite. | HarnessForge has stronger generalized confirmation policy. |
| Repo detection | Detects PRDs and common stack markers; prompts to confirm tech stack. | Detects stack, package managers, verification commands, workflows, specs, work items, SBOMs, monorepo markers, nested instruction scopes, governance inventory, file coverage. | Both inspect target shape. | HarnessForge is substantially broader. |
| First-run UX | `keel init` prompts for PRD and tech stack, then writes. | `quickstart` is read-only and reproducible, `init --dry-run --json` previews writes. | Both guide setup. | HarnessForge has safer first-run dry-run behavior. |
| Agent instructions | `agent-rules.md`, `keel/README.md`, command files, rule files, `.claude` and `.codex` command adapters. | Root agent files, platform routers, harness skill, first-agent task, docs routing, templates. | Both install agent-readable instructions. | Keel has stronger command rituals; HarnessForge has broader cross-agent router support and skill wiring. |
| Skills | `keel/skills.md` is a simple expectation file. | `.agents/skills/harness/SKILL.md` with references and first-agent workflow. | Both name harness-specific agent guidance. | HarnessForge has formal skill structure and validation. |
| Slash commands | `/keel-run`, `/new-feature`, `/approve-feature`, `/rollback-phase`, `/verify`. | No generated slash commands by default. | Both support agent workflows. | Keel owns command protocol; HarnessForge avoids platform-specific command runtime by default. |
| Phase planning | Deterministic deliverable DAG, topological layers, risk scoring, isolated deliverable types, phase packing. | Diff-aware verification planning, blueprints, enhance plan. | Both plan work/checks. | HarnessForge lacks deliverable-DAG planning; this is a strong optional feature candidate. |
| Phase execution | One requested phase at a time, prior-gate checks, stale-plan checks, allowed/blocked paths, exit criteria. | One active feature rule, scope docs, change contract, report signals. | Both fight scope sprawl. | Keel has operational enforcement instructions; HarnessForge has structural guidance and advisory reporting. |
| Allowed and blocked paths | Required in phase files and verified for overlap. | Scope boundaries and component inventory exist; no generic per-work-unit allowed path detector yet. | Same concept. | Add work-unit plan quality detection to HarnessForge. |
| Gates | Passed and failed phase gate JSON files under `.agent/phase_gates/`. | Verify evidence summaries, first-agent review evidence, high-risk acceptance, release gates. | Both use machine-readable evidence. | Keel has phase gates; HarnessForge has broader evidence schemas. |
| Build ledgers and audit logs | Writes human build ledger and audit log per phase plus JSONL audit events. | Evidence log, report artifacts, verify summaries, release-check output. | Both preserve review evidence. | HarnessForge can import target ledgers but should not write phase ledgers by default. |
| Session tracking | Local sessions with owner, implementer, active session pointer, event ledger, hooks. | Read-only session snapshot for restart. | Both use "session" language. | Keel session is mutable telemetry; HarnessForge session is static orientation. |
| Event model | Controlled event vocabulary for sessions, tools, tests, debug loops, LLM calls, tokens, file edits. | Observability report, token-economics records, verify evidence, report JSON. | Both value observability. | HarnessForge should import event ledgers when present, not install hooks. |
| Token tracking | Extracts token usage from hooks/transcripts where configured; reports by phase, implementer, actor. | Token-economics schema and normalizer for Codex JSONL traces, research evidence. | Both model tokens. | Keel has runtime token rollups; HarnessForge has research/evidence contract. |
| Tool reporting | Tool call counts and failure rates from session events. | Governance inventory and report observability signals; no tool-call ledger import yet. | Both inspect tools in different ways. | Add target-contained tool-event import to HarnessForge report. |
| Debug-loop reporting | Counts debug loops from events. | No direct debug-loop report field except observability/effectiveness evidence. | Partial overlap. | Candidate import field for existing ledgers. |
| Snapshotting | Captures file hash manifests and stashes files at phase start. | Generated file manifests and drift detection; no whole-repo stash. | Both compare file state. | HarnessForge should not stash target files by default. |
| Rollback | Dry-run or confirmed rollback from rollback DAGs; deletes created files and invalidates gates. | Change contract and blueprints require rollback strategy; no target rollback execution. | Both require rollback thinking. | Keel has execution power; HarnessForge should stay advisory/import-only. |
| Feature workflow | Draft feature workspace, approve feature, merge manifest, generate phases. | Feature-state JSON, roadmap guidance, blueprints. | Both track features. | HarnessForge does not own a build queue; Keel does. |
| Verification | Harness consistency plus phase-gate validation; phase files carry exit criteria. | Audit, verify plan/run, sync, readiness, report, release-check, pin checks, research checks. | Both require verification before completion. | HarnessForge has broader verification and safety; Keel has phase-specific exit criteria. |
| Readiness | Current phase ready/blocked/complete, verify pass/fail. | Rich readiness: source-of-truth, checks, drift, workflow/work item inventory, context budget, instruction quality, governance inventory, evidence, skill wiring, review surfaces. | Both determine if work can proceed. | HarnessForge is much stronger for general readiness. |
| Audit/scoring | No structural score; verify returns consistency failures. | Seven buckets mapped to five core subsystems, structural score, HTML/JSON output. | Both produce actionable failures. | Keel could benefit from score-like diagnostics; HarnessForge already has them. |
| Report | Session, phase, token, tool, debug reports. | Unified report covering readiness, audit, drift, index, verify, effectiveness, first-agent status, platform, instruction quality, policy, SBOM, feature state, observability, review work, maturity. | Both report status. | Keel is deeper for execution telemetry; HarnessForge is broader for harness health. |
| Release readiness | Roadmap includes release workflow for Keel itself; no target release gate. | `release-check` over stored evidence, score, drift, first-agent lifecycle, feature state, observability, SBOM, docs fan-out, maturity. | Both have release docs/workflows. | HarnessForge has a reusable target release gate. |
| GitHub Action | Release workflow for Keel package and Homebrew tap. | Composite Action for target repo harness commands. | Both use GitHub Actions. | HarnessForge has product Action surface; Keel has project release automation. |
| Workflow policy | Keel says hosted workflows should wrap local scripts. | Generated optional CI is manual; workflows are opt-in; Action does not commit/push/PR. | Both prefer local scripts as source of truth. | HarnessForge has stronger cross-repo workflow safety policy. |
| Security boundaries | Roadmap includes future risk taxonomy and security evals; rules stop on production credentials and blocked paths. | Security boundary map, high-risk acceptance, path containment, redaction, prompt-injection/data-poisoning boundaries, workflow permission review, no network generation. | Both identify high-risk actions. | HarnessForge is stronger today; Keel has valuable future ideas. |
| Privacy | Session hooks may read transcript paths for token extraction; reports local working dir. | Redacts local home paths and secret-like values from durable output; avoids raw logs in compact evidence. | Both handle local evidence. | HarnessForge has stronger default privacy posture. |
| Stale generated surfaces | Verify scans for retired names; generator tests ban selected stale strings. Actual helper scripts still contain old `harness/` references. | Instruction quality and generated tests exist; explicit stale generated-surface detector is planned. | Same failure class. | Keel provides a real example for HarnessForge to detect. |
| Template testing | Embedded asset tests and banned-string tests. | Generated snapshot, audit, corpus, pins, local entrypoint, Action tests. | Both test generated surfaces. | HarnessForge has broader generated-content gates. |
| Fixture corpus | No public-repo fixture corpus. | Offline public-repo corpus with realistic fixture shapes. | Both use tests. | Add a Keel-shaped fixture to HarnessForge. |
| Policy presets | Fixed Keel rules. | Blueprint packs for many repo types. | Both encode operating rules. | HarnessForge is more configurable and opt-in. |
| Research/provenance | No research ledger. | Research source allowlist, lock file, source record schema, inbox, research docs. | Minimal overlap. | HarnessForge uniquely owns provenance/research surfaces. |
| SBOM | No SBOM detection or generation. | Detects existing SPDX and CycloneDX evidence; optional adapter status. | None. | HarnessForge unique. |
| Effectiveness evaluation | Roadmap proposes security evals; no implemented eval command. | `effectiveness` reviews stored evidence and keeps performance claims separate from structure. | Both recognize eval need. | HarnessForge has implemented evidence assessment; Keel has future eval scenarios. |
| MCP | Roadmap proposes read-only MCP server. | Detects MCP config as governance inventory; does not generate MCP config. | Both aware of MCP. | Neither has a read-only MCP server implemented. |
| Dashboard | Static `docs/index.html`; roadmap proposes dashboard. | No dashboard command; reports can write JSON/Markdown/HTML audit. | Both have reporting artifacts. | Keel has dashboard ambition; HarnessForge has report artifacts. |
| Platform support | Go CLI builds macOS and Linux binaries in release Makefile; Homebrew install. | Python 3.13+, macOS 15+, Windows 11+, Ubuntu 22.04+ floor, Action runner pinning. | Both cross-platform minded. | HarnessForge explicitly preserves Windows behavior; Keel release targets omit Windows binaries today. |
| Dependency model | Go module with Cobra, YAML, term/sys dependencies. | Runtime standard library by default; pinned build/test dependencies. | Both pin dependencies. | HarnessForge default runtime dependency policy is stricter. |
| Docs shape | README, walkthrough, roadmap, distribution, release notes, generated harness docs. | Public docs, generated docs, harness docs, research docs, schemas. | Both document operating model. | HarnessForge docs are broader and more formally routed. |

## Internal Module Comparison

### Keel Implementation Inventory

| Area | Source | Capability |
| --- | --- | --- |
| CLI entrypoint | `cmd/keel/*.go` | Cobra commands for init, phase, close, report, rollback, session, verify, planning, events, current phase, merge feature. |
| Embedded assets | `embed.go`, `internal/assets`, `assets/keel-template/` | Bundled target harness template copied by `init`. |
| Bootstrap | `internal/bootstrap` | Directory creation, template copying, manifest/gate/log stubs, session hook setup. |
| PRD discovery | `internal/prd` | Finds or creates `docs/PRD.md`. |
| Tech-stack detection | `internal/detect` | Detects common stacks and writes confirmed stack to `agent-rules.md`. |
| Planner | `internal/planner` | Parses deliverables and phase policy, validates DAG, groups phases, renders manifest and phase files. |
| Current phase | `internal/currentphase` | Reads manifest and gate files to report ready/blocked/complete. |
| Gate writer | `internal/gate` | Writes gate, rollback DAG, build ledger, audit log, and run log. |
| Snapshot | `internal/snapshot` | Hash manifests, diffs, file stash and restore helpers. |
| Rollback | `internal/rollback` | Reads rollback DAGs, computes downstream unwind, dry-runs or executes file rollback. |
| Session | `internal/session` | Config, identity, hook installer, event writer, state/metric reducers, human reports. |
| Audit | `internal/audit` | Append-only project audit JSONL with event vocabulary. |
| Verify | `internal/verify` | Required file/rule/command checks, phase file markers, gate evidence checks, stale reference scanning. |
| Generator tests | `internal/generator` | Template required-file and banned-string validation. |
| Release/distribution | `Makefile`, `.github/workflows/release.yml`, `DISTRIBUTION.md` | Build binaries, release to GitHub, update Homebrew tap. |

### HarnessForge Implementation Inventory

| Area | Source | Capability |
| --- | --- | --- |
| CLI entrypoint | `src/harnessforge/cli.py` | Argparse command surface and text/JSON formatting. |
| GitHub Action | `src/harnessforge/github_action.py`, `action.yml` | Composite Action wrapper over selected CLI/library commands. |
| Core helpers | `src/harnessforge/core/` | Runtime doctor, path safety, redaction, model dataclasses, report writing. |
| Project detection | `src/harnessforge/project/detect.py` | Stack, manifests, workflows, commands, source-of-truth, SBOM, monorepo markers, routing markers. |
| Structural index | `project/indexer.py`, `file_coverage.py`, `nested_instructions.py` | File classes, repo map, component overflow, file coverage, nested instruction candidates. |
| Readiness/sync/session | `project/readiness.py`, `sync.py`, `session.py` | Read-only readiness, stable sync exits, restart snapshot. |
| Verification planner | `project/verify.py`, `project/planner.py` | Plan or run project checks and map changed files to checks. |
| State migration/finalization | `state_migration.py`, `finalize_review.py` | Legacy state consolidation and first-agent review finalization. |
| Generation | `generation/generate.py`, `update.py`, `templates/` | Default harness generation, drift/update, enhance-existing plan and addenda. |
| Blueprints | `generation/blueprints.py` | Optional operating-model packs. |
| Corpus | `generation/public_repo_corpus.py` | Offline generated-content fixture gate. |
| Audit | `assessment/audit.py` | Structural scoring, recommendations, five-core mapping. |
| Evidence/reporting | `evidence/*.py` | Context budget, effectiveness, feature state, governance inventory, high-risk acceptance, instruction quality, maturity, observability, policy, release check, SBOM, skill wiring, token economics, verify evidence, workflow inventory, unified report. |
| Tests | `tests/` | CLI, detection, generation/audit, Action, pins, research, corpus, token/effectiveness contracts, maturity, local entrypoints. |
| Research | `docs/harness/research/`, `scripts/refresh_research.py` | Fixed source ledger, lock, inbox, source-record schemas, research notes. |

## What Keel Has That HarnessForge Does Not

1. A target-project phase execution runtime.
2. Agent slash-command protocol for `/keel-run`, feature approval, rollback,
   and verification.
3. `BUILD_MANIFEST.yaml` as an ordered build queue with phase files.
4. Deterministic deliverable-DAG phase planning from TDD deliverables.
5. Passed and failed phase gate files as first-class execution state.
6. A phase close command that writes all phase completion artifacts at once.
7. Rollback DAG generation and confirmed downstream phase rollback execution.
8. Pre and post file hash snapshots plus file stash/restore helpers.
9. Mutable local sessions with active session pointer and per-session JSONL
   event ledger.
10. Event append command and hook-based event capture.
11. Token/tool/debug reports from execution telemetry.
12. Draft feature workspace and approval flow that merges phases into a build
   manifest.
13. PRD discovery and interactive PRD creation during init.
14. Tech stack confirmation prompt during init.
15. Homebrew distribution workflow for the Keel CLI itself.

## What HarnessForge Has That Keel Does Not

1. Read-only quickstart and dry-run generation plans before writing.
2. Broad repository inspection and structural indexing.
3. File coverage against `git ls-files` and component overflow reporting.
4. Nested instruction candidate planning for monorepos.
5. Generated zero-install harness skill with reference validation.
6. First-agent review lifecycle and finalization command.
7. High-risk surface acceptance evidence.
8. Structural audit scoring across implementation buckets and five core
   subsystem mapping.
9. Unified report with readiness, audit, drift, index, evidence, instruction
   quality, feature state, observability, policy, SBOM, review work, and
   maturity.
10. Release-check command that gates on existing evidence without publishing.
11. Verify plan mode and explicit verify run mode with compact evidence
   summaries.
12. Existing-instruction review through `enhance`.
13. Safe state migration from legacy progress and handoff files.
14. Optional blueprint packs for many repo types.
15. Offline public-repo fixture corpus.
16. Composite GitHub Action for target repositories.
17. SBOM evidence detection and adapter status.
18. Effectiveness evidence assessment.
19. Research source allowlist, lock file, source-record schema, and research
   inbox.
20. Stronger path safety, local path redaction, Action output safety, and
   platform contract metadata.

## Shared Strengths

- Both treat the harness as repo-owned files, not just chat advice.
- Both preserve existing files by default and require an explicit force or
  apply path for riskier writes.
- Both make verification and evidence visible to agents.
- Both recognize stale instructions and generated drift as real harness risks.
- Both distinguish local scripts from hosted CI wrappers.
- Both have tests for generated or installed harness surfaces.
- Both reject agent scope sprawl through one-unit-at-a-time guidance, though
  Keel does this through phases and HarnessForge through active state and
  scope contracts.

## Shared Weaknesses Or Open Work

| Open area | Keel state | HarnessForge state | Reading |
| --- | --- | --- | --- |
| Token/cost budgets | Roadmap only; tokens are tracked but not budget-enforced. | Token-economics evidence exists; no execution budget enforcement. | HarnessForge should measure/import first, not enforce target budgets by default. |
| Security evals | Roadmap proposes injection, timeout, scope escape, and gate integrity evals. | Effectiveness and security boundaries exist, but no live adversarial agent eval runner. | Deterministic negative-path fixture tests are the near-term practical path. |
| Stale generated surfaces | Keel has scanner and tests, but still contains stale helper-script references. | Planned from Keel mining; not implemented yet. | Highest-confidence next HarnessForge improvement. |
| Work-unit quality | Strong in Keel phase files. | Not yet a generic report field. | Add advisory detection for task/phase/plan files. |
| Execution telemetry import | Keel writes ledgers. | HarnessForge does not import Keel-style ledgers yet. | Import target-contained evidence without installing hooks. |
| MCP server | Roadmap only in Keel; HarnessForge detects MCP configs but does not serve MCP. | Not implemented in either. | Low priority until a concrete user need appears. |
| Dashboard | Keel has static dashboard and roadmap for server/export. | HarnessForge has JSON/Markdown/HTML audit reports, no dashboard. | Reports are enough unless users need live exploration. |

## Recommended HarnessForge Improvements

These recommendations match `keel-derived-enhancement-plan.md`.

1. Implement stale generated-surface detection first.
   Keel demonstrates a real mismatch between active docs and helper scripts.
   HarnessForge already has `instructionQuality`, `enhance`, `report`, and
   corpus surfaces that can carry this finding without new defaults.

2. Add advisory work-unit plan quality.
   Detect plan, task, phase, and feature files. Report whether they include
   allowed paths, blocked paths or out-of-scope notes, exit criteria,
   verification commands, evidence requirements, and stop conditions.

3. Strengthen feature-state evidence alignment.
   Warn when `passing`, `validated`, or `shipped` state lacks current evidence
   or conflicts with failed checks, changed surfaces, or roadmap state.

4. Import target-contained execution evidence.
   Parse existing gate files, failed gates, rollback DAGs, session JSONL, audit
   JSONL, token buckets, tool failures, and debug-loop events when present.
   Keep this bounded, redacted, and read-only.

5. Add optional deliverable-DAG planning.
   Use a dependency graph and risk/isolation labels only when project-owned
   files expose structured deliverables. Keep output advisory and dry-run.

6. Add a phase-gated fixture.
   Preserve this comparison as tests: stale helper paths, passed and failed
   gates, rollback evidence, a manifest, and event ledgers.

## What Not To Copy

- Do not make HarnessForge default generation install `.agent/` state,
  execution hooks, slash commands, rollback stashes, or a build manifest.
- Do not require PRD/TDD files for arbitrary target repos.
- Do not run target project commands except through existing explicit
  `verify --run` or apply-mode confirmation paths.
- Do not generate Homebrew, release, push, PR, or credentialed workflow
  automation for target repos.
- Do not present imported Keel-style execution telemetry as HarnessForge-owned
  truth. Treat it as target-contained evidence.

## Bottom Line

Keel is better at governing a single agent execution flow after a repo opts
into its phase model. HarnessForge is better at understanding arbitrary repos,
creating portable harness surfaces, keeping writes safe, reporting maturity,
and compiling release evidence.

The best integration path is asymmetric: HarnessForge should learn to detect,
score, and import Keel-like evidence where target repos already have it, while
keeping its default generator portable, conservative, review-required, and
zero-install.
