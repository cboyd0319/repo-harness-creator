# Roadmap

Last reviewed: 2026-06-16 UTC.

This roadmap captures accepted product improvements and candidate follow-up
ideas. It is separate from
`docs/harness/research/remaining-ideas-research.md`, which records the research
trail and rejected defaults.

## Product Direction

HarnessForge should keep its default generator portable and conservative while
building stronger opt-in product modes around analysis quality, reporting,
review evidence, and user experience.

The main boundary remains unchanged:

- Default generation should not copy personal repo preferences into target
  repositories.
- Existing project files should stay project-owned unless the user explicitly
  asks HarnessForge to update them.
- Normal inspection, sync, index, audit, and dry-run flows should stay
  read-only and avoid target command execution.
- Richer analysis, adapters, generated reports, workflows, and policy presets
  should be explicit, reviewable, and target-contained.

## Current Release Boundary

Release prep can resume. The accepted pre-release backlog and RunHaven-derived
review-finalization work are complete. New field-test findings should stay as
release-prep evidence or candidate roadmap items until maintainers explicitly
accept them as product work.

HarnessForge is still alpha/pre-release, has not been deployed, and has no
external users. Accepted backlog work should optimize for the clean current
product contract instead of preserving earlier generated layouts, report
schemas, manifest formats, CLI outputs, Action behavior, or docs as backward
compatibility promises. Add a shim only when a maintainer declares a release
boundary or records a temporary evaluation bridge with removal criteria.

Current release-prep work should focus on clean package evidence, release
notes, tags, Action pin guidance, optional SBOM/provenance decisions, and any
manual platform checks the maintainer wants before publishing.

## Surface Impact Checklist

Every roadmap item should identify which HarnessForge surface it changes before
implementation starts.

| Surface | Question |
| --- | --- |
| Local repo harness | Does this affect HarnessForge's own `AGENTS.md`, state files, docs, sensors, or release controls? |
| Generated target harness | Should generated repos receive a file, section, warning, manifest rule, or review-required placeholder? |
| CLI runtime | Does this add or change a `harnessforge` command, flag, JSON contract, exit code, report, or default behavior? |
| Existing project files | Could this modify or enhance project-owned `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot instructions, specs, workflows, or docs? |
| GitHub Action | Should the composite Action expose the same behavior, inputs, outputs, reports, or summaries? |
| Optional workflow scaffolds | Should the generated manual CI scaffold change, and must it remain opt-in? |
| Tests and fixture corpus | Which generated snapshots, public-repo fixtures, contract tests, and real-repo quality checks prove this behavior? |
| Release/package surface | Does this affect packaging, tags, SBOM/provenance, isolated install smoke, or release evidence? |
| Research and source ledger | Does this need current primary-source evidence, fixed allowlist updates, or a new source-record shape? |
| Security and privacy | Could this expose secrets, local paths, private code, tool permissions, network access, or cost-incurring behavior? |
| Platform contracts | Does this affect macOS, Windows, Linux, Python, runner labels, or platform adapters? |
| Docs and UX | Which user-facing docs, help output, Action summaries, and first-run guidance need to change? |

If a surface is out of scope, state that explicitly in the change plan. This
keeps local HarnessForge maintenance, generated target harnesses, and the
published Action from drifting into each other.

## Source Weighting

For generic harness and task-list patterns, the Walking Labs
learn-harness-engineering public repository
(`https://github.com/walkinglabs/learn-harness-engineering`) carries higher
weight than sibling-project examples. Sibling repos are field evidence. The
canonical harness-learning resources define the default shape unless a target
repository's own files, commands, platform contract, or maintainer decision
proves a narrower local override.

Current weighted patterns:

- baseline verification should run before new feature work when practical;
- work should start from one bounded plan, feature, or roadmap item;
- implementation should stop at the first rung that satisfies the request: no
  change, deletion, docs, config, existing behavior, standard library, native
  platform feature, existing dependency, one clear local change, then minimum
  new code;
- quality score or quality document state should influence what gets worked
  next;
- repeated review feedback should become a mechanical rule, sensor, test, or
  durable doc instead of recurring chat advice;
- instruction entries should have source, applicability, and retirement
  conditions when they become durable rules;
- feature or task state should be evidence-gated: behavior, verification,
  status, and evidence must agree before anything is marked passing;
- completion evidence should climb the verification ladder: static checks,
  runtime/startup checks, and system or user-flow checks when the change spans
  components;
- sensor, lint, and validation failures should be agent-oriented: explain what
  failed, why it matters, and the likely repair path;
- observability has two layers: runtime signals that explain what happened and
  process artifacts that explain why a change should be accepted;
- cleanup has immediate session-exit work and periodic drift-reduction work;
- generated evidence and candidate queues should be promoted into durable docs,
  tests, schemas, templates, or code before they become contracts.
- durable instructions should reject hidden assumptions, speculative features,
  drive-by refactors, style drift, unrequested configurability, and
  over-abstracted single-use code;
- intentional simplifications should record their known ceiling and upgrade
  path, while preserving input validation at trust boundaries, data-loss
  prevention, security, accessibility, platform parity, and explicit
  requirements.

## Smallest Correct Work Gate

Use this gate for accepted roadmap items before implementation starts:

1. Can the outcome be met by no change, deletion, documentation,
   configuration, or existing behavior?
2. Can the standard library or built-in language feature cover it?
3. Can a native platform feature cover it?
4. Can an existing project dependency cover it without new configuration?
5. Can one clear local change satisfy the contract?
6. Only then add the minimum new code or harness surface area.

This applies to local HarnessForge harness work, generated target harness
content, CLI/runtime features, existing project-file enhancement modes,
GitHub Action behavior, the optional CI scaffold, docs, and release
automation. If a surface is out of scope, say so before editing.

## Task-List Patterns To Adopt

Recent reference-doc review found several patterns worth adopting for
HarnessForge roadmap and generated task-list guidance.

| Pattern | Adopted Direction |
| --- | --- |
| Compact active status | Keep the restart surface short. Move detailed historical progress into completed or archived records when it stops helping current work. |
| Active, completed, archive buckets | Separate in-flight work from completed evidence and historical provenance. Avoid one growing task list that agents must reread forever. |
| Explicit status lifecycle | Use statuses such as `candidate`, `accepted`, `planned`, `in_progress`, `blocked`, `validated`, `shipped`, `superseded`, and `abandoned`. |
| Execution gate | Each accepted item should say what must be true before work starts, including release-prep, validation, source-evidence, or design gates. |
| Task table with owner, evidence, and retirement | Roadmap items should include owner, verification evidence, and done or retire condition, not just a title. |
| Technical debt separation | Recurring cleanup and drift belong in a debt tracker or dedicated section until they become tests, sensors, or release gates. |
| Candidate vs commitment boundary | Candidate refinements and mined ideas should stay separate from accepted roadmap commitments. |
| Generated evidence is not a contract | Reports, ledgers, and candidate queues are review evidence. Durable behavior should be promoted into docs, tests, schemas, templates, or code. |
| Failure-mode method map | Connect task-list artifacts to the failure they prevent: cold-start confusion, scope sprawl, premature completion, fragile startup, weak handoff, or subjective review. |
| Phase plus health lane | Roadmaps can use phases, but should also keep a pre-release health lane for refactors, docs drift, and verification debt that would make release work unsafe. |
| Fresh-session test | A generated or enhanced harness should help a fresh agent answer what the system is, how it is organized, how it starts, how it is verified, and what is currently in progress. |
| Instruction lifecycle metadata | Durable rules should record why they exist, when they apply, and when they can be removed or replaced. |
| Evidence-gated state transitions | A feature, task, or roadmap item should not move to passing, validated, or shipped from agent assertion alone. Verification evidence must be recorded. |
| Agent-oriented repair feedback | Checks and sensors should produce actionable feedback that tells an agent what failed, why the boundary exists, and where to repair. |
| Smallest-correct work gate | Each accepted item should ask whether no change, deletion, docs, config, existing behavior, stdlib/native/existing dependency, or one local change is enough before new code or surface area is added. |
| Intentional simplification notes | Known ceilings and upgrade paths should be recorded when a simplified implementation is accepted, without weakening security, accessibility, data-loss handling, platform parity, or explicit requirements. |

These patterns should shape both local HarnessForge planning and generated
`docs/harness/state/roadmap.md` guidance. They do not require copying any sibling
repo's docs or process wholesale.

## Accepted Improvements

### Unified Report Command

Initial CLI and Action support is implemented through
`harnessforge report --target <repo>` and `command: report`. The report
composes current inspection surfaces into one review artifact without running
target repository commands.

Candidate report inputs:

- readiness verdict and next actions;
- harness audit score and failed checks;
- generated-file drift;
- structural index summary;
- repo-map summary when available;
- stored verify evidence;
- stored effectiveness evidence;
- first-agent task lifecycle status;
- policy preset and platform contract;
- release evidence status.

Reports should support Markdown and JSON. Report paths must be target-relative
when written, and reports must avoid local absolute paths, private code
excerpts, secrets, and raw command output.

Reports should distinguish structural readiness from real task evidence. Useful
quality signals include fresh-session answerability, instruction bloat or
duplication, first-agent review state, evidence-gated feature state, runtime
observability gaps, and cleanup or stale-artifact drift.

Implemented report expansion:

- instruction-quality and context-budget signals now report startup instruction
  coverage, signal/noise, placeholder noise, word/line/byte budget status, and
  largest instruction surfaces in warning mode;
- structural index output now includes a compact `repoMap` with primary
  languages, components, source-of-truth docs, manifest kinds, entrypoints,
  boundary examples, verification commands, review-required files, unknowns,
  and existing SBOM evidence;
- unified reports carry the repo-map summary;
- report and Action summaries include policy preset status;
- report and release-check surfaces include release evidence automation and
  evidence-gated maturity;
- reports include feature-state scope, runtime/process observability,
  optional index-adapter status, and SBOM adapter status while keeping SBOM
  generation and external index generation out of normal flows.

### Compact Repo Map From Index

Status: initial compact `repoMap` implemented in `index --json` and carried by
`report`.

Build a compact, cited repo map from `harnessforge index` output. The map
should help generated instructions and `--enhance-existing` addenda become
more repo-specific without turning harness docs into broad code summaries.

Useful repo-map fields:

- component name and target-relative source paths;
- inferred purpose and confidence;
- source-of-truth docs and spec surfaces;
- localized docs and the detected source-of-truth locale or canonical docs
  root when the repo has translated copies;
- module-near architecture, decision, or constraint files that should be read
  only when relevant;
- package, build, test, and release manifests;
- verification commands and evidence gaps;
- generated, vendored, fixture, and training-code boundaries;
- unknowns that require project review.

The repo map should be deterministic, compact, and reviewable. It should never
commit embeddings, private code summaries, or machine-local paths by default.

### Deterministic Large-Repo File Discovery Priority

Status: accepted, not started.

The 2026-06-16 Kubernetes, VS Code, and Bazel field refresh shows
`harnessforge.fileCoverage.v1` is now visible, but all three sampled large
repos still have budget-limited file categories. The next indexing improvement
is deterministic priority ordering before representative source/test scanning.

Scope:

- CLI/runtime: improve `detect_project` or index discovery ordering so root
  instructions, runtime files, workflows, source-of-truth docs, harness docs,
  manifests, and SBOM evidence are scanned before broad source/test examples.
- Generated target harness: no new default files unless the improved signal
  changes generated guidance quality.
- GitHub Action: report and release-check paths should inherit the same
  deterministic discovery behavior through shared library code.
- Tests/fixtures: cover capped scans where high-signal files would otherwise
  appear after many source files.
- Security/privacy: keep paths target-relative, avoid code excerpts and
  embeddings, and do not add network access.

Definition of done:

- Large-repo field evidence shows fewer high-signal categories marked
  budget-limited at the same `--max-files` value.
- `fileCoverage.categories[*]` distinguishes budget limits from intentionally
  skipped categories if the scanner excludes tracked vendor/generated files.
- Generated guidance quality improves without increasing default harness size.

### SBOM-Aware Indexing

Status: default detection of existing SPDX and CycloneDX-style SBOM files is
implemented in `index --json` and `report`. The optional adapter contract is
implemented as a read-only report plan. Actual SBOM generation remains a
future explicit opt-in.

SBOM data can add value when it is used as evidence, not as a default
dependency or quality claim.

Good uses:

- improve dependency and package-manager detection;
- identify component boundaries that are clearer in package metadata than in
  source layout alone;
- surface supply-chain, license, container, and external-service review areas;
- connect release evidence to dependency inventories;
- detect existing project-owned SBOMs and cite them in reports.

Default behavior should detect existing SPDX or CycloneDX-style SBOM files and
report them as review surfaces. HarnessForge should not generate SBOMs during
normal `init`, `inspect`, `index`, or `sync --check`.

Optional generation behavior can add an explicit SBOM adapter later. That
adapter must:

- require an explicit command or flag;
- use installed or project-owned tooling only;
- report tool name, version, input paths, output path, duration, and warnings;
- write only to target-relative report paths;
- avoid making vulnerability, license, or compliance claims without a reviewed
  policy and current source evidence.

### First-Agent Task Lifecycle

Status: implemented as advisory report/readiness evidence.

Generated harnesses include `docs/harness/state/first-agent-task.md` and
`docs/harness/evidence/first-agent-review.json` so projects can tell whether
the first deep harness review is pending, completed, retired, blocked, invalid,
or stale.

Implemented behavior:

- readiness warning when the task exists but first-agent review evidence is
  missing;
- generated review evidence placeholder under `docs/harness/evidence/`;
- `harnessforge report` summary of completed, pending, stale, invalid, blocked,
  or retired first-agent review state;
- advisory by default; audit and sync do not hard-gate this unless a future
  target repo opts into a stricter policy.

The task has a retirement path once project maintainers accept repo-specific
harness improvements.

The first-agent lifecycle should preserve initialization as its own phase. A
newly generated harness should ask the first agent to confirm runnable startup,
at least one trustworthy verification path, current progress visibility, and
project-specific source-of-truth routing before unrelated feature work.

### RunHaven-Derived Review Finalization Flow

Status: implemented before release prep. Structured high-risk acceptance,
explicit review finalization, state migration, skill-wiring validation,
compact verification evidence capture, report review-work polish, stable report
field docs, and the RunHaven-shaped fixture are implemented.

The RunHaven harness overhaul showed that several correct target-repo actions
were still manual even though HarnessForge had enough structure to guide or
automate them. HarnessForge should provide a safe review-finalization flow that
keeps repo-owned docs authoritative while reducing hand-written harness
maintenance.

Accepted behavior:

- Detect split or stale state contracts such as `progress.md` plus
  `session-handoff.md` and offer a safe migration to `current-state.md`.
- Add a review-finalization command or explicit mode that can retire the
  first-agent task, update `first-agent-review.json`, record accepted
  high-risk surfaces, and show exactly what changed.
- Generate and consume structured high-risk surface acceptance evidence for
  instruction routers, CI/workflow files, container runtime files, agent
  skills, hooks, environment templates, MCP configs, and other governance
  surfaces.
- Wire target-side high-risk acceptance evidence into readiness, report,
  release-check, Action summaries, and maturity scoring.
- Replace raw marker-string review detection with structured fields and
  machine status values such as `review_required`, `reviewed`, `retired`,
  and `accepted_advisory`.
- Provide a safe manifest metadata refresh for reviewed target-owned generated
  files without rewriting project-owned prose.
- Validate repo-local harness skill wiring, reference paths, trigger text, and
  first-agent status in generated and enhanced repositories.
- Capture compact verification evidence from known command results into target
  evidence JSON without pasting raw logs.
- Separate advisory detected high-risk inventory from unresolved actionable
  review work in human and JSON report output.
- Publish or document the stable report JSON schema fields used by downstream
  tools and Action summaries.

Boundaries:

- Default `inspect`, `report`, `audit`, `index`, `sync --check`, and dry-run
  flows remain read-only.
- Target-side finalization writes require an explicit command or flag and must
  stay target-contained.
- HarnessForge must not make itself canonical for a target repo after initial
  generation unless the repo owner opts into the CLI or Action as a recurring
  gate.
- Existing project-owned instruction files, workflows, scripts, and docs
  remain project-owned. HarnessForge can propose or record reviewed evidence;
  it cannot silently claim ownership.
- No target command execution, dependency installation, workflow creation,
  push, PR, credential action, or remote Action adoption happens without
  explicit opt-in.

Surface impact:

- Local repo harness: track this as the active pre-release objective and keep
  the product boundary clear.
- Generated target harness: update templates for first-agent review evidence,
  source-record status values, current-state migration guidance, and harness
  skill validation.
- CLI runtime: add the finalization command or mode, state migration planning,
  evidence writing, manifest refresh, and clearer report fields.
- Existing project files: preserve existing owner files unless the user
  explicitly approves applying a reviewed patch.
- GitHub Action: surface the same readiness, maturity, and high-risk
  acceptance state in summaries and outputs; do not write target files unless
  the Action input explicitly selects a write-capable command.
- Optional workflow scaffolds: no default change.
- Tests and fixture corpus: add a RunHaven-shaped fixture with root
  instruction routers, CI workflow, multiple Containerfiles, current-state,
  first-agent evidence, high-risk acceptance evidence, and report/maturity
  expectations.
- Release surface: implemented; release prep can resume with real-repo field
  quality passes as release evidence.

Done when:

- a target repo can move from generated/pending review to reviewed maturity
  using target-contained evidence;
- RunHaven-style high-risk surfaces no longer require manual JSON invention;
- false-positive review markers from schema vocabulary are gone;
- state migration, first-agent retirement, manifest refresh, skill wiring
  validation, and evidence capture have focused tests;
- report, release-check, Action summary, and corpus fixtures agree on
  advisory versus actionable review state.

### Feature-State Gate And Scope Surface

Improve `feature_list.json`, roadmap guidance, reports, and optional future
helpers around a stricter feature/task state machine.

Candidate behavior:

- every feature or task has behavior, verification, status, and evidence fields;
- only one active item by default unless explicit multi-agent ownership exists;
- `passing`, `validated`, and `shipped` states require recorded evidence, not
  agent confidence;
- reports flag mismatches between feature state, progress logs, roadmap state,
  and stored verification reports;
- generated guidance asks maintainers to keep items roughly completable within
  one focused session when possible;
- scope drift detection can later compare changed files to the active item and
  report likely out-of-scope changes.

This should remain advisory until a target project opts into state transition
automation.

### Instruction Lifecycle And SNR Review

Improve instruction-file quality rather than only checking whether instruction
files exist.

Candidate behavior:

- detect oversized root instruction files and repeated rules across AGENTS,
  Claude, Gemini, and Copilot surfaces;
- classify root instructions as startup, hard constraint, verification, routing
  link, topic detail, historical note, or personal preference;
- suggest moving low-SNR topic detail into focused docs;
- preserve project-owned wording while adding source, applicability, and
  retirement metadata for durable generated or accepted rules;
- report contradictory or stale generated blocks for review before writing.

This belongs primarily in `--enhance-existing`, `report`, and generated
roadmap/first-agent guidance.

### Harness Maintenance Optimization

Reduce the doc and harness-update fan-out for small HarnessForge changes.

Status: implemented for the current pre-release contract.

Problem:

- tiny code, template, or wording changes previously required updates across
  several local harness docs, state files, manifests, and evidence logs;
- that overhead can erase the intended token and time savings of having a
  harness;
- duplicated boundary and status text increases drift risk because one surface
  inevitably goes stale.

Implemented behavior:

- defines which files are authoritative for each class of fact, and makes other
  docs link or summarize instead of duplicating;
- adds an authoritative fact map for product boundaries, CLI command surfaces,
  generated-file contracts, Action behavior, release evidence, and local
  harness state;
- adds a lightweight change-to-docs routing table so agents know which harness
  docs actually need updates for code, template, Action, audit, release, or
  research changes;
- prefers generated summaries, reports, or manifest-derived checks over manual
  repeated prose when the information is mechanical;
- teaches audit/report to flag stale or missing canonical updates without
  requiring every small change to touch every harness file;
- sets a maximum expected docs fan-out for routine changes, with explicit
  exceptions for release, security, platform, boundary, and generated-contract
  changes.

Surface impact:

- Local repo harness: primary owner; reduces updates to `current-state.md`,
  manifest snippets, evidence logs, and overlapping harness docs.
- Generated harness: apply only if the pattern improves target repos without
  hiding important review obligations.
- CLI/runtime: initial `report` output now summarizes docs fan-out routing
  status from `docs/harness/authoritative-facts.md`, reports duplicate durable
  fact blocks, and can block with `--require-docs-fanout-budget`.
- GitHub Action: report mode inherits the docs fan-out summary and can fail
  with `require-docs-fanout-budget: "true"`.
- Tests and fixtures: regression coverage exists for canonical routing,
  duplicate fact reporting, Action/CLI fan-out enforcement, and organized
  harness layout; avoid adding tests for every prose copy.

Latest state consolidation replaces split root progress and handoff logs with
one `current-state.md` restart file while self-audit stays `100/100`.
Local and generated startup routes now read compact state first and open
heavier README, harness README, roadmap, and component-inventory docs only when
the task touches those surfaces.

Done condition met for the current pre-release contract. Reopen only if a
routine low-risk change again needs broad manual doc/state edits.

### Harness Token Economics Research

Status: accepted, not started.

Research whether comprehensive repository harnesses increase or decrease agent
token consumption in real work. This must be evidence-backed, not assumed from
intuition or anecdote.

Required research receipts:

- current primary or high-quality public sources on agent context usage,
  prompt/instruction length, retrieval, task success, and cost tradeoffs;
- measured HarnessForge field evidence from representative repos with minimal,
  moderate, and comprehensive harnesses;
- before/after task traces or controlled evaluations that compare token usage,
  tool calls, retries, completion quality, and verification success;
- a clear separation between startup-token cost, repeated-session savings,
  reduced rework, and any failure modes from instruction bloat;
- conclusions that state whether the evidence shows net token increase, net
  token decrease, mixed results, or insufficient evidence.

Output should be a research note with citations, a compact metric schema for
future evaluations, and a recommendation for how HarnessForge should size,
route, summarize, or lazily load harness content. Do not turn the conclusion
into generated behavior until the receipts show the tradeoff.

### Generated Harness Skill Fallback

Status: implemented for the current generated-harness contract.

Generated target harness docs should not imply HarnessForge is the canonical
status source for a repository. Repository-owned docs and state are canonical by
default. The HarnessForge GitHub Action can become a repo's recurring harness
quality/check surface only when the repo owner explicitly adopts it.

Candidate behavior:

- make generated harnesses usable by contributors who only have the repository
  checkout and normal project tooling; do not assume `harnessforge` is
  installed after the initial generation; implemented with generated
  `.agents/skills/harness/SKILL.md`;
- review generated `README.md`, `verification-matrix.md`,
  `sensor-registry.md`, `quality-document.md`, and related planning docs for
  wording that makes HarnessForge sound required or canonical;
- downgrade generated HarnessForge references to advisory guidance unless the
  owner opts into the GitHub Action or an explicit command workflow they run;
  implemented for generated target docs;
- render `.agents/skills/harness/SKILL.md` plus compact reference routing so
  agents can learn how to maintain and improve the repo harness without
  treating HarnessForge itself as the project source of truth; implemented;
- reference that skill from generated `AGENTS.md` as a review-required helper
  for harness-maintenance tasks, not as a general startup mandate; implemented;
- organize generated `docs/harness/` into purpose-based subdirectories while
  keeping `README.md`, `authoritative-facts.md`, and `manifest.json` at the
  top level; implemented for new generated target harnesses;
- keep the skill target-owned, portable, and free of repo-local preferences,
  local paths, MCP config, personal tool mandates, or autonomous workflow
  assumptions; implemented and covered by generated-content tests;
- prefer repo-native verification scripts, checked-in instructions, and
  structured target-owned state over generated docs that tell every
  contributor to install or run HarnessForge;
- keep future generated-doc consolidation behind quality evidence instead of
  deleting review-required safety surfaces blindly;
- test the result against real generated target repos, including RunHaven-style
  evaluations that inspect content quality instead of only structural score.

Latest optimization evidence:

- Generated target harness root clutter drops to 3 top-level files under
  `docs/harness/`: `README.md`, `authoritative-facts.md`, and `manifest.json`.
- RunHaven's current flat harness has 29 top-level files under `docs/harness/`,
  which made manual review harder.
- The generated write count is currently 36 for the representative Python
  target after removing the product-local source allowlist. Further token and
  file-write savings should come from deliberate consolidation of overlapping
  lifecycle/status docs, not from deleting review-required safety surfaces
  blindly.
- A rendered target with a real verification command audited at `100/100`, had
  zero stale flat-path references, and generated `AGENTS.md` stayed at 140
  lines.
- Generated Markdown footprint was reduced from 85,839 bytes and 1,730 lines
  to 69,009 bytes and 1,454 lines while preserving generated audit `100/100`.
- Generated total artifact footprint is now 136,337 bytes and 2,911 lines,
  down from 160,684 bytes and 4,190 lines at the start of the second
  optimization pass. Generated targets no longer receive this repo's
  product-local research source allowlist, and generated manifests are compact
  machine-readable JSON.
- Regression tests now cap generated Markdown below 70,000 bytes and 1,500
  lines, and total generated output below 140,000 bytes and 3,000 lines for the
  representative Python target.

Surface impact:

- Local repo harness: track the boundary and quality evidence only.
- Generated harness: main surface; may add a target-owned agent skill and
  update generated docs/AGENTS routing.
- CLI/runtime: generator templates, ownership metadata, audit/report wording
  checks, and public corpus expectations.
- Existing project files: preserve owner text; `--enhance-existing` should
  propose review-only guidance rather than claiming HarnessForge authority.
- GitHub Action: remains explicit opt-in for recurring HarnessForge checks.
- Tests and fixtures: add rendered-content quality assertions for canonicality,
  advisory wording, skill references, and no local preferences.

Done condition met for the current generated-harness contract: generated docs
distinguish project-owned canonical state from optional HarnessForge checks,
generated targets include a compact target-owned maintenance skill, and the
default generated Markdown footprint is guarded. Reopen only if quality passes
show recurring confusion, unnecessary generated file churn, or meaningful token
bloat.

### Repo-Local Harness Layout Convergence

Status: implemented.

This repo's own `docs/harness/` directory now uses the organized
layout generated into target repositories: top-level `README.md`,
`authoritative-facts.md`, and `manifest.json`, with supporting files grouped
under focused `boundaries/`, `feedback/`, `state/`, `evidence/`, `research/`,
`operations/`, `release/`, and `schemas/` directories.

Implemented behavior:

- moved HarnessForge repo-local harness docs into the deployed directory shape
  instead of relying on a repo-local flat layout;
- updated local manifests, links, snippets, sensors, report paths, state docs,
  and tests in one coordinated pass;
- removed the repo-local path bridge once this repo's harness shape matched the
  generated target shape;
- kept HarnessForge-only files such as self-healing docs clearly repo-local and
  out of generated target harnesses;
- added audit coverage so flat top-level harness docs fail the organized
  layout check.

Surface impact:

- Local repo harness: main surface; reorganizes this repo's own
  `docs/harness/` shape.
- Generated harness: should not change except for tests proving the shape is
  still the deployed contract.
- CLI/runtime: removed the repo-local path bridge.
- GitHub Action: no behavior change unless report paths or summaries reference
  local harness docs.
- Tests and fixtures: update snippet, link, audit, report, and corpus coverage.

Done condition met: this repo's local harness uses the same organized
`docs/harness/` shape generated into target repositories, and the runtime path
bridge has been removed.

### Runtime And Process Observability

Status: implemented as read-only report and release-check evidence.

Add stronger guidance and reporting around observability that helps agents
debug from evidence.

Implemented behavior:

- `harnessforge report --json` emits `observability` with detected runtime
  and process signals;
- `harnessforge release-check` includes an `observability` gate;
- distinguish runtime observability from process observability such as change
  contracts, acceptance criteria, rubrics, and evidence logs;
- encourage agent-oriented failure messages in generated sensor guidance;
- record when real user-flow or full-pipeline checks are required because a
  change spans components;
- keep OpenTelemetry, tracing stacks, Playwright, and app-specific logging as
  project-owned or explicit opt-in adapters, not generation defaults.

### Golden Public-Repo Fixture Corpus

Status: implemented as an offline pinned fixture corpus with a metadata refresh
check.

Build a stable quality corpus from popular public open-source repositories.
The corpus should test generated-content quality, not only command success.

Corpus selection should cover:

- Python package;
- JavaScript or TypeScript app;
- Go service or CLI;
- Rust CLI or library;
- Java or JVM project;
- .NET project;
- Swift package;
- C or C++ project;
- container or devcontainer-heavy repo;
- monorepo;
- docs or research repo;
- spec-driven repo;
- security-sensitive repo.

Use pinned public commit SHAs and expected detection metadata. Normal unit tests
should not require network access or full repository checkouts. A separate
fetch/update script or scheduled quality job can refresh the corpus and record
diffs for review.

Implemented behavior:

- `harnessforge corpus --json` runs the offline generated-content quality
  corpus without network access;
- `scripts/refresh_public_repo_corpus.py` validates pinned fixture metadata
  offline by default;
- `scripts/refresh_public_repo_corpus.py --verify-remote` is the explicit
  owner action for networked `git ls-remote` checks.

Quality checks should include:

- no local absolute paths;
- no unrendered template tokens;
- no generic fallback context when specific context is detectable;
- root instruction files stay router-sized and route deeper detail on demand;
- bounded review-marker counts;
- expected stack, component, workflow, and instruction-surface detection;
- source-of-truth docs, localized docs, and existing planning systems are
  detected without blindly editing translations or project-owned plans;
- useful verification placeholders when no repo-owned check is detected;
- stable generated artifact snapshots for representative fixtures.

### Real Large Public Repo Field Corpus

Status: first repo-local field slice implemented; product follow-up accepted.

The deterministic `harnessforge corpus` command remains offline. Separately,
this repo now has `docs/harness/research/large-public-repo-corpus.json` and
`scripts/analyze_large_public_repos.py` for explicit maintainer-run analysis
against real large public GitHub repositories. The script clones only with
`--clone`, writes checkouts under ignored `.harnessforge/large-public-repos/`,
does not run target commands, and writes compact evidence reports under
`docs/harness/evidence/`.

First field run:

- selected Kubernetes, VS Code, and Bazel from the 13-repo corpus;
- all three cloned and analyzed successfully;
- Kubernetes hit the 20,000-file scan limit with 30,513 tracked files;
- VS Code and Bazel hit the bounded component inventory limit;
- all three exposed the current `create_harness(..., dry_run=True)` default
  4,000-file scan as a large-repo quality gap;
- all three produced review-required nested `AGENTS.md` candidate scopes.

Accepted product follow-up:

- analyze the real corpus evidence and produce a HarnessForge gap analysis
  that separates deterministic fixes, review-required heuristics, optional
  adapters, and release-prep evidence needs;
- add a large-repo scan control or index-reuse path to generation dry-runs;
- add nested instruction-scope planning to large-repo analysis, dry-run init,
  enhance, and report flows;
- keep nested `AGENTS.md` writes review-required and off by default;
- continue expanding field runs across the remaining pinned repos before
  release.

### Better `--enhance-existing` Mode

This is one of the highest-value quality areas. HarnessForge should become much
better at improving existing instruction files without taking ownership away
from the project.

Initial slice: `harnessforge init --enhance-existing --dry-run --json` now
emits a review plan with parsed sections, canonical section coverage,
review-required proposed edits, placeholder patch previews, duplicate
instruction findings, local absolute path findings, user-specific tool mandate
findings, and verification-conflict findings before any instruction file is
changed. Patch previews are review-only and are not applied automatically.

Dedicated surface: `harnessforge enhance --target <repo>` and
`harnessforge enhance --target <repo> --json` now expose the same read-only
review plan without making users discover it through `init`.

Current implemented slice:

- reports per-file instruction-quality recommendations;
- emits `taskClassGuidance` for verification, boundary, instruction
  maintenance, platform routing, and general guidance;
- emits `ruleLifecycle` source, applicability, owner, and retirement guidance
  for accepted durable rules;
- keeps patch previews review-only and never rewrites existing instruction
  files automatically.

Further candidate behavior:

- extend section parsing beyond the current Markdown-heading pass;
- classify project-owned rules, generated routers, stale generated blocks,
  and conflicts beyond the current finding set;
- optionally apply reviewed cleanup edits after explicit patch preview approval;
- preserve local wording unless it conflicts with a detected boundary or
  generated ownership metadata;
- deduplicate repeated AGENTS, Claude, Gemini, and Copilot guidance;
- route to detected source-of-truth specs, workflows, verification, and
  harness docs;
- flag user-specific mandates, local paths, unverified platform claims, and
  personal tool preferences as review findings;
- add source, applicability, and retirement metadata for durable rules when the
  target project accepts them;
- support a `--enhance-existing --dry-run --json` plan that is detailed enough
  for CI or review.

This work should get a dedicated design and fixture pass before implementation.

### Interactive Quickstart And Init

Status: initial reproducible decision plan implemented.

`harnessforge quickstart --interactive --json` emits an interactive-ready plan
without prompts or writes. It records the selected agent file, platform
contract, verification commands, planned writes, preserved files, readiness,
and reproducible `quickstart`, `init`, and `sync` commands. Non-JSON
`--interactive` prints the dry-run summary first, skips prompts safely when
stdin is not a TTY, and asks before writing in real TTY sessions.

Useful prompts:

- target repo and platform contract;
- primary agent instruction file;
- preserve existing files or write to a HarnessForge-specific agent file;
- optional generated CI scaffold;
- verify evidence policy;
- policy preset or blueprint;
- report output path.

The UI should be quiet, reversible, and copy the same decisions into explicit
CLI flags so users can reproduce the result non-interactively. It should start
with a dry-run summary, then ask before writes.

### Optional Index Adapters

Status: implemented as a read-only report plan and detection surface.

Keep the standard-library structural index as the default. Add optional
adapters only where they improve generated artifact quality or report evidence.

Candidate adapters:

- symbol indexes, such as ctags;
- structural search or parser tools;
- existing code-intelligence artifacts, such as SCIP or LSIF;
- existing local code-search indexes;
- SBOM files or explicit SBOM generation;
- repo-owned static-analysis reports.

When adapter data materially changes generated output, HarnessForge should say
so in dry-run, report, and readiness output. Adapter output should include
provenance, freshness, confidence, and risks.

Implemented behavior: `harnessforge report --json` emits `indexAdapters` with
detected local tools, existing index artifacts, default behavior, adapter
candidates, and explicit opt-in requirements. Normal generation still uses the
standard-library structural index.

### Action Summary Polish

Status: implemented for report and sync summaries.

Improve the composite GitHub Action user experience.

Implemented behavior:

- richer `$GITHUB_STEP_SUMMARY` output for `command: report`, including
  readiness, score, drift, docs fan-out, verify evidence, effectiveness,
  instruction quality, first-agent lifecycle, maturity, policy preset status,
  SBOM adapter status, feature-state status, observability status,
  index-adapter status, repo-map counts, and SBOM count;
- richer `command: sync` summary with readiness, warning, review-required,
  runnable-check, instruction-quality, first-agent, and verify-evidence status;
- existing audit and verify summaries remain concise and table-oriented.

Caller-owned artifact upload examples are documented in `docs/action.md`.
HarnessForge still does not upload artifacts, publish releases, create tags, or
open pull requests by itself.

### Release Evidence Automation

Status: implemented for the current pre-release contract.

`harnessforge release-check --target <repo>` assembles read-only release
readiness evidence from the unified report surface. It never publishes, tags,
uploads, pushes, or runs target repository commands. It returns `0` for passed,
`1` for warning, and `2` for blocked, and can write target-relative JSON or
Markdown evidence files.

Implemented checks:

- harness audit status;
- sync preflight status;
- current run-mode verify evidence;
- generated-file drift;
- instruction quality;
- first-agent lifecycle;
- docs fan-out budget status;
- release controls presence;
- effectiveness evidence;
- existing SPDX or CycloneDX SBOM evidence, optionally hard-gated with
  `--require-sbom`;
- immediate clean-state checks and periodic cleanup or drift-scan evidence when
  the target project defines those sensors.

Release-prep evidence candidates:

These are release-prep decisions, not accepted pre-release backlog. Add them
only when the maintainer chooses the release evidence boundary.

- package build and isolated install smoke evidence import;
- pin and research-source check evidence import where applicable;
- generated-harness smoke evidence import;
- optional platform CI evidence import;
- provenance report presence when the project opts into that control;
- release notes and tag readiness evidence import.

### Harness Maturity Levels

Status: implemented in `harnessforge report`, `harnessforge release-check`,
and Action summaries.

Evidence-gated maturity labels now sit alongside structural audit score:

- `generated`: HarnessForge created or detected the harness structure.
- `reviewed`: project maintainers reviewed placeholders and boundaries.
- `verified`: approved project checks have recent passing evidence.
- `release-ready`: release evidence gates are satisfied for the target policy.
- `measured`: representative effectiveness evidence is reviewable and approved.

Maturity should be based on evidence, not marketing language. Structural audit
score should remain separate.

### Policy Presets

Status: initial expanded preset catalog and report recommendations
implemented.

Expand policy presets beyond the current blueprint packs. Presets should tune
readiness checks, report sections, suggested sensors, and review gates. They
should not inject personal preferences or platform-specific config by default.

Candidate presets:

- open-source library;
- internal service;
- monorepo;
- CLI or developer tool;
- security-sensitive application;
- regulated or privacy-sensitive repository;
- data or ML project;
- agentic application;
- spec-driven project;
- infrastructure or IaC repository;
- mobile or desktop application;
- docs or research repository;
- legacy migration project;
- education or intentionally vulnerable training repository.

Presets should have source-reviewed rationale, dry-run output, and fixture
coverage before they become recommended defaults.

Implemented behavior:

- built-in review-required blueprints now cover the accepted preset families;
- `harnessforge report --json` includes `policyPresets` with available,
  applied, and recommended presets;
- recommendations are read-only and advisory until a project owner reviews and
  applies a blueprint explicitly.

### Source Package Organization

Status: implemented for the current pre-release package shape.

Reorganize `src/harnessforge/` so related command, report, generator, evidence,
and policy modules are easier to navigate and maintain.

Boundary:

- local CLI/runtime source organization is in scope;
- generated target harness content is out of scope unless imports or templates
  need a direct adjustment;
- GitHub Action behavior is out of scope unless module moves affect the Action
  entry point or packaging data;
- package import compatibility is not required before the first release, but
  tests must prove CLI entry points, Action dispatch, and generated rendering
  still work.

Done when the package layout has clear module groups, stale imports are gone,
focused import/CLI/Action/generator tests pass, and the public docs do not
advertise internal paths as stable API.

Implemented shape:

- public entrypoints and command dispatch stay top-level in `cli.py` and
  `github_action.py`;
- generated harness creation, update planning, blueprint writing, and the
  offline public-repo corpus live under `src/harnessforge/generation/`, while
  templates remain under `src/harnessforge/templates/`;
- shared models, path safety, redaction, report-path helpers, harness path
  constants, and doctor checks live under `src/harnessforge/core/`;
- repo detection, indexing, readiness, planning, session, sync, spec-system,
  and verify helpers live under `src/harnessforge/project/`;
- audit scoring lives under `src/harnessforge/assessment/`;
- evidence, report composition, release-check gates, maturity, policy preset
  recommendations, SBOM adapter status, instruction quality, context budget,
  feature state, observability, index-adapter reporting, first-agent
  lifecycle, governance inventory, workflow inventory, and verify evidence now
  live under `src/harnessforge/evidence/`.

## Suggested Build Order

1. Implemented: structured high-risk surface acceptance evidence updates
   readiness, report, release-check, Action summaries, and maturity scoring.
2. Implemented: readiness and report JSON now expose structured
   `reviewSurfaces` plus `reviewStatusSummary`, and review finalization uses
   those machine status values instead of parsing human-readable messages.
3. Implemented: `finalize-review` can retire the first-agent task, record
   high-risk acceptance evidence, and refresh manifest metadata.
4. Implemented: `migrate-state` plans and explicitly applies bounded,
   idempotent migration from `progress.md` and `session-handoff.md` to
   `current-state.md` while preserving legacy files.
5. Implemented: readiness, report, release-check, and Action summaries validate
   generated and enhanced repo-local harness skill wiring, reference paths,
   trigger frontmatter, and instruction routing.
6. Implemented: `verify --evidence-summary` writes compact
   `harnessforge.verifySummary.v1` evidence without stdout or stderr previews,
   and readiness/release gates consume it.
7. Implemented: report JSON includes `reviewWork`, separating unresolved
   actionable review work from accepted advisory inventory, and
   `docs/harness/feedback/report-json-contract.md` documents stable fields.
8. Implemented: the public-repo quality corpus includes a RunHaven-shaped
   fixture with existing routers, CI workflow, multiple container runtime
   files, `current-state.md`, first-agent evidence, high-risk acceptance, and
   reviewed maturity/report expectations.
9. Implemented first slice: real large public repo field corpus and analysis
   runner, with initial Kubernetes, VS Code, and Bazel evidence.
10. Implemented first slice: large public repo gap analysis captured
   deterministic fixes, review-required heuristics, optional adapters, and
   release-prep evidence needs.
11. Next accepted large-repo quality work: implement generation max-file/index
   reuse and review-required nested `AGENTS.md` scope planning.
12. Release-prep field evidence: re-run real-repo quality passes against
   RunHaven, selected sibling repos, and the remaining large public corpus.
13. Current accepted backlog is complete. Resume release prep and keep new
   findings in the roadmap only after maintainers accept them as product work.
14. Keep the generated target wording advisory unless the repo owner opts into
   the Action, and continue quality passes against real repositories.
15. Keep the pinned public-repo quality corpus and generated-artifact scorer
   green as quality and detection gates evolve.
16. Previously completed: policy preset report status, evidence-gated
   feature-state and instruction-quality reporting, read-only SBOM adapter
   status, expanded policy presets, interactive quickstart decision plan, and
   source package reorganization.

## Rejected Defaults

These remain useful only as explicit opt-ins:

- mandatory SBOM generation during normal harness generation;
- networked indexing services;
- committed embeddings or private code summaries;
- autonomous push, PR, self-heal, setup, or teardown workflows;
- user-specific research mandates;
- platform permission files or MCP config generation without explicit user
  request and current source evidence;
- treating structural audit score as proof of real-agent effectiveness.
