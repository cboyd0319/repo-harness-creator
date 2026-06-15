# Roadmap

Last reviewed: 2026-06-15 UTC.

This roadmap captures accepted product improvements that should be considered
after the current docs update and before, during, or after release prep. It is
separate from `docs/harness/research/remaining-ideas-research.md`, which records the
research trail and rejected defaults.

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

Release prep is intentionally deferred. Keep building the accepted roadmap
items before returning to release gates, package publishing, or Action tag
decisions.

HarnessForge is still alpha/pre-release, has not been deployed, and has no
external users. Accepted backlog work should optimize for the clean current
product contract instead of preserving earlier generated layouts, report
schemas, manifest formats, CLI outputs, Action behavior, or docs as backward
compatibility promises. Add a shim only when a maintainer declares a release
boundary or records a temporary evaluation bridge with removal criteria.

The current pre-release buildout includes:

- golden public-repo fixture corpus and generated-artifact quality scorer;
- first-agent task lifecycle evidence;
- report expansion for repo-map summaries, policy preset status, and release
  evidence fields;
- better instruction-quality and signal-to-noise reporting;
- compact repo maps from `index`, default SBOM detection, and optional SBOM
  adapter design;
- GitHub Action summary polish;
- `release-check` command or equivalent release report mode;
- evidence-gated harness maturity levels;
- expanded policy presets;
- interactive quickstart/init UX.

Return to release prep only after these items are completed or explicitly
deferred with owner, evidence, and risk recorded.

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
- unified reports carry the repo-map summary.

Remaining report expansion: add policy preset status and release evidence
automation as those surfaces land.

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

### SBOM-Aware Indexing

Status: default detection of existing SPDX and CycloneDX-style SBOM files is
implemented in `index --json` and `report`. Optional SBOM generation/import
adapters remain future work.

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

Optional behavior can add an explicit SBOM adapter later. That adapter should:

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

- Local repo harness: primary owner; reduces updates to `progress.md`,
  `session-handoff.md`, manifest snippets, evidence logs, and overlapping
  harness docs.
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

Latest local startup compaction replaced append-only root state logs with
current-state snapshots, reducing `progress.md` and `session-handoff.md` from
2,557 combined lines to 153 combined lines while self-audit stays `100/100`.
Local and generated startup routes now read compact state first and open
heavier README, harness README, roadmap, and component-inventory docs only when
the task touches those surfaces.

Done condition met for the current pre-release contract. Reopen only if a
routine low-risk change again needs broad manual doc/state edits.

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

Add stronger guidance and reporting around observability that helps agents
debug from evidence.

Candidate behavior:

- report whether startup, critical paths, logs, traces, health checks, or
  benchmark scripts are discoverable;
- distinguish runtime observability from process observability such as change
  contracts, acceptance criteria, rubrics, and evidence logs;
- encourage agent-oriented failure messages in generated sensor guidance;
- record when real user-flow or full-pipeline checks are required because a
  change spans components;
- keep OpenTelemetry, tracing stacks, Playwright, and app-specific logging as
  project-owned or explicit opt-in adapters, not generation defaults.

### Golden Public-Repo Fixture Corpus

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

Candidate behavior:

- extend section parsing beyond the current Markdown-heading pass;
- classify project-owned rules, generated routers, stale generated blocks,
  and conflicts beyond the current finding set;
- extend the implemented instruction signal-to-noise report into task-class
  guidance and suggest focused topic docs when root files become dumping
  grounds;
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

Add an interactive first-run flow after the non-interactive command surfaces
are stable.

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

### Action Summary Polish

Status: implemented for report and sync summaries.

Improve the composite GitHub Action user experience.

Implemented behavior:

- richer `$GITHUB_STEP_SUMMARY` output for `command: report`, including
  readiness, score, drift, docs fan-out, verify evidence, effectiveness,
  instruction quality, first-agent lifecycle, repo-map counts, and SBOM count;
- richer `command: sync` summary with readiness, warning, review-required,
  runnable-check, instruction-quality, first-agent, and verify-evidence status;
- existing audit and verify summaries remain concise and table-oriented.

Remaining polish:

- examples for artifact upload without making upload a default requirement.

### Release Evidence Automation

Add a `harnessforge release-check --target <repo>` command or equivalent report
mode for release prep.

Candidate checks:

- package build and isolated install smoke status;
- harness audit status;
- sync preflight status;
- pin and research-source checks where applicable;
- docs local-link and local-path hygiene;
- generated-harness smoke test;
- optional platform CI evidence;
- SBOM/provenance report presence when the project opts into those controls;
- immediate clean-state checks and periodic cleanup or drift-scan evidence when
  the target project defines those sensors;
- release notes and tag readiness.

Release checks should assemble evidence. They should not publish, tag, upload,
or push without explicit user action.

### Harness Maturity Levels

Add evidence-gated maturity labels alongside structural audit score.

Candidate levels:

- `generated`: HarnessForge created or detected the harness structure.
- `reviewed`: project maintainers reviewed placeholders and boundaries.
- `verified`: approved project checks have recent passing evidence.
- `release-ready`: release evidence gates are satisfied for the target policy.
- `measured`: representative effectiveness evidence is reviewable and approved.

Maturity should be based on evidence, not marketing language. Structural audit
score should remain separate.

### Policy Presets

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

## Suggested Build Order

1. Keep the generated target wording advisory unless the repo owner opts into
   the Action, and continue quality passes against real repositories.
2. Keep the pinned public-repo quality corpus and generated-artifact scorer
   green as quality and detection gates evolve.
3. Expand `harnessforge report` with repo-map, policy preset, and release
   evidence fields as those surfaces land.
4. Add evidence-gated feature-state and deeper instruction-quality reporting
   to the generated-harness quality scorer.
5. Add compact repo maps from `index`, then SBOM detection and optional SBOM
   adapter design.
6. Improve GitHub Action summaries and release evidence automation.
7. Add maturity levels and expanded policy presets.
8. Design the interactive quickstart/init UX once the underlying decisions are
   stable.

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
