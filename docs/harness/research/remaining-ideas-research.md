# Remaining Ideas Research

Reviewed: 2026-06-15 UTC.

Scope: local `awman`, `aspec`, and `maki`; the public
`jcaiagent7143-ui/harnessforge`; OpenAI, Martin Fowler, LangChain,
OpenHarness, Walking Labs, spec-driven-development sources, and current
harness-engineering research sources. A later local supplement reviewed the
supplied paper catalog, Bluepeak-AI `docs/harness`, JobSentinel `docs/harness`,
and root `AGENTS.md` files where present.

This note is repo-local product research. It is not generated into target
repositories. No AGY review was used for this pass.

## Conclusion

The previous pass captured the best immediate generator improvements: generic
structured-spec detection, Just task-runner detection, architecture-lint
routing, generated-doc drift context, read-only `inspect`, and Python package
priority over docs-site classification.

The remaining good ideas are mostly not more default generated files. They are
product modes, audit signals, and opt-in checks that help users understand what
HarnessForge detected, what is safe to rely on, and what still needs project
review. The first explicit product-mode implementation is `harnessforge
blueprint`, which keeps richer operating-model guidance separate from normal
`init` output.

The dedicated harness-docs and AGENTS supplement added two read-only UX slices:
`harnessforge session` and `harnessforge plan`. Sensor registry support is now
implemented as a review-required generated artifact. Structured project-source
records are now implemented as a generated schema and review-required example.
The highest-value remaining product risk is accurate analysis and indexing of
large existing codebases before HarnessForge designs or improves a harness. The
initial research pass is recorded in `large-codebase-indexing-research.md`, and
the first read-only `harnessforge index --target . --json` structural index is
implemented. The remaining score/benchmark risk is closed as read-only
`harnessforge effectiveness --target . --json`, which assesses stored
representative evidence and blocks unsupported claims instead of running
benchmarks or creating synthetic performance scores.

## Highest-Value Next Ideas

| Idea | Source signal | HarnessForge fit | Boundary |
| --- | --- | --- | --- |
| Readiness report mode | AWMAN `ready`, OpenHarness `--dry-run` readiness verdicts | Add a read-only `ready` or `inspect --readiness` path that reports `ready`, `warning`, or `blocked` with next actions | Must not execute project commands by default |
| Project verification contract | Public HarnessForge verify protocol, OpenAI feedback loops, Fowler sensors | Add a stable project-check JSON contract separate from harness `audit` | Running target repo commands must be explicit because commands are executable code |
| Existing-spec sync checks | ASPEC source-of-truth model, AWMAN's `aspec/` usage | Detect structured specs and report whether generated/enhanced instructions route agents to them | Do not impose ASPEC folder names or rewrite spec systems |
| Work-item/template awareness | ASPEC work-item template, AWMAN work-item workflows | Detect work-item directories/templates and surface them as planning inputs | Do not generate work items by default |
| Workflow surface detection | AWMAN TOML/YAML workflow schema | Detect repo-owned workflow definitions and report setup/teardown/remediation surfaces | Do not become an AWMAN runtime or generate autonomous workflows by default |
| Context budget and duplication audit | Maki context-efficiency focus, OpenAI short repo maps | Add audit signals for oversized/duplicative instruction surfaces and router files | Avoid brittle token counting claims; use approximate size and duplication signals |
| Permission/governance inventory | Maki permissions, OpenHarness governance, GitHub governing-agents guide | Detect MCP configs, agent settings, permission files, and setup-step workflow files as security-critical surfaces | Do not author platform permission files until current primary docs are verified |
| Explicit blueprint mode | Public HarnessForge profile/blueprint split, local Harness Forge, ASPEC/AWMAN boundary review | Add opt-in blueprint packs for deeper operating models without changing normal generated harness defaults | Keep blueprint artifacts review-required and preserve existing project edits unless forced |
| Real-agent evaluation harness | Public HarnessForge A/B benchmark, OpenAI/Fowler feedback-loop claims | Implemented as read-only `harnessforge effectiveness --target . --json` evidence assessment | Does not run benchmarks or market structural audit as real agent effectiveness |
| Config precedence report | AWMAN layered config model | Show which overrides shaped detection: CLI flags, detected files, generated manifest, existing project ownership | Keep deterministic; no LLM refinement needed |
| Short `sync --check` alias | Public HarnessForge quickstart, current drift-report UX | Add a discoverable CI-oriented alias for `update --drift-report --json` | Alias only; no new mutation semantics |
| Session snapshot | JobSentinel `harness:session`, Bluepeak-AI and JobSentinel state docs | Implemented as read-only `harnessforge session` | Must not write files or run target checks |
| Diff-aware verification planner | JobSentinel `harness:plan -- --since` | Implemented as read-only `harnessforge plan --since` | Uses detected or explicit project checks; command execution remains explicit through `verify --run` |
| Source-record schema | Bluepeak-AI structured provenance records | Implemented as generated schema plus review-required example | Keep separate from HarnessForge's own fixed research allowlist |
| First-agent harness improvement instruction | Real-repo quality passes and generated-harness review gaps | Implemented as generated `docs/harness/state/first-agent-task.md` plus canonical instruction routing | Must not impose repo-local preferences, overwrite project-owned instructions, or bypass review/verification |

## New Backlog: Large-Codebase Analysis And Indexing

Research status: completed in `large-codebase-indexing-research.md`.
Implementation status: first structural `harnessforge index --target . --json`
slice implemented.

Problem:

- HarnessForge can generate and audit structure, but existing large repos need
  better automatic analysis before the generated harness can be truly tailored.
- Weak indexing can miss important components, ownership boundaries, generated
  code, tests, local tools, package relationships, and source-of-truth docs.
- A bad harness for a large repo is often caused by incomplete repo
  understanding, not by missing template text.

Research task:

- Completed: reviewed current open source solutions for code search, semantic
  indexing, repo maps, call/dependency graphs, language-server indexes, static
  analysis, and monorepo navigation.
- Completed: compared scale, offline operation, privacy, incremental updates,
  language coverage, generated files, vendored code, and cross-platform setup
  at the product-design level.
- Completed: implemented the first no-dependency structural index command.

Boundary:

- No networked indexing service by default.
- No committed embeddings, private code summaries, or machine-local paths in
  generated harnesses.
- No dependency on one language server, one code host, or one monorepo tool.
- Any optional index cache must be target-contained, reviewable, ignored or
  explicitly owned, and safe to delete.

## Implemented Effectiveness Evidence Assessment

`harnessforge effectiveness --target . --json` closes the remaining
score/benchmark command backlog without weakening the evidence boundary.

Behavior:

- Scans target-contained `docs/harness/evidence/effectiveness*.json` reports,
  or explicit target-relative `--evidence` paths.
- Assesses the existing `harnessforge.effectivenessEvidence.v1` contract.
- Reports `reviewable`, `inconclusive`, `not_better`, or `blocked`.
- Blocks missing evidence, invalid schema shape, frozen replay used for
  quality claims, missing held-out tasks, non-candidate-sensitive metrics,
  unmet do-no-harm floors, unresolved safety violations, unredacted result
  artifacts, missing rollback, or candidate-better claims without human
  approval.
- Reports metric deltas only from stored evidence. It does not run project
  benchmarks, install dependencies, call models, inspect private code excerpts,
  or convert structural audit score into real-agent effectiveness.

Boundary:

- A reviewable report means the evidence is ready for human review. It is not
  automatic promotion.
- A blocked report means no benchmark or performance claim should be made from
  that evidence.
- Real benchmark runners remain repo-owned until HarnessForge has a
  representative, maintained, target-safe corpus and execution contract.

## Implemented Session Snapshot

`harnessforge session` adopts the useful restart pattern from the local
harness-docs and AGENTS review without generating repo-specific scripts into
target repositories.

Current command shape:

- `harnessforge session --target <repo>`
- `harnessforge session --target <repo> --json`

Boundary:

- Read-only.
- Does not run target verification commands.
- Does not write state files.
- Redacts target roots from portable JSON output.
- Reports git status, latest commit, detected stack, readiness verdict,
  harness audit summary when a harness exists, selected state-file presence,
  and next actions.

## Implemented Diff-Aware Verification Planner

`harnessforge plan` adopts the useful changed-file planning pattern without
turning HarnessForge into a workflow runtime or executing target commands.

Current command shape:

- `harnessforge plan --target <repo> --since HEAD`
- `harnessforge plan --target <repo> --since HEAD --json`
- `harnessforge plan --target <repo> --since <ref> --command "<check>"`

Boundary:

- Read-only.
- Uses `git diff --name-only` for changed-file discovery.
- Does not run target verification commands.
- Redacts target roots from portable JSON output.
- Maps changed files to detected or explicit project checks with a fallback to
  baseline checks when no file-specific match is available.
- Reports unmatched changed files when some files match focused checks and
  others do not.

## Implemented Sensor Registry

Generated harnesses now include `docs/harness/feedback/sensor-registry.md` as a
review-required artifact. It seeds detected verification commands, requires the
project to review owner, source, purpose, retirement condition, and review
cadence, and states that configured sensors do not prove real-agent
effectiveness.

Boundary:

- Review-required before relying on the listed checks as completion, release,
  self-heal, or automation gates.
- Does not execute target repository commands.
- Does not infer human ownership or retirement conditions.
- Does not promote structural or runnable-check evidence into benchmark claims.

## Implemented Source-Record Schema

Generated harnesses now include `docs/harness/research/source-record.schema.json` and
`docs/harness/research/source-record-example.json`. The schema gives projects a
structured way to record source owner, purpose, trust boundary, review status,
claims, limitations, usage, and retirement condition for project-curated
provenance records.

Boundary:

- Project-owned source records are separate from HarnessForge's fixed
  `research-sources.json` allowlist.
- The generated example is review-required and must be replaced before a
  project relies on it.
- Records must use target-relative paths or reviewed URLs, not machine-local
  absolute paths.
- Records do not make structural audit score or runnable checks into
  real-agent effectiveness claims.

## Implemented Explicit Blueprint Mode

`harnessforge blueprint` is the first deliberately robust opt-in product mode.
It is separate from `harnessforge init` so the base generator remains portable
and conservative while advanced users can apply richer project guidance with a
clear review boundary.

Current command shape:

- `harnessforge blueprint list`
- `harnessforge blueprint show <blueprint-id>`
- `harnessforge blueprint apply <blueprint-id> --target <repo> --dry-run`
- `harnessforge blueprint apply <blueprint-id> --target <repo> --force`

Current built-in packs:

- `agentic-app`
- `spec-driven`
- `web-service`
- `data-ml`
- `security-sensitive`
- `workflow-automation`

Generated blueprint artifacts live under `docs/harness/blueprints/`, include
ownership metadata, and are explicitly marked review-required. Existing files
are preserved unless `--force` is supplied after review. This adopts the useful
profile/blueprint and source-of-truth ideas from the research pass without
copying ASPEC, AWMAN, Maki, MCP, memory, or platform permission systems into
target repos by default.

## Implemented Explicit Verification Execution

`harnessforge verify --run` closes the first project-verification execution
slice. Default `verify` remains plan-only and read-only. Run mode is explicit,
visible in JSON as `"mode": "run"`, and records command status, exit code,
duration, capped stdout/stderr previews, and overall timing metadata.

Current command shape:

- `harnessforge verify --target <repo> --json`
- `harnessforge verify --target <repo> --json --run`
- `harnessforge verify --target <repo> --json --run --timeout-seconds 120`
- `harnessforge verify --target <repo> --json --run --command "<repo-owned check>"`
- `harnessforge verify --target <repo> --run --json-report docs/harness/evidence/verify-<date>.json`

Boundary:

- Run mode uses subprocess argument lists, not a shell.
- Shell control syntax is rejected; use separate `--command` values.
- Missing verification remains blocked and exits `2` in run mode.
- Failed or timed-out checks exit `1`.
- Passing required checks exit `0`.
- The JSON target root remains `null` for portable artifacts.
- `--json-report` writes the same verify payload to a target-relative path,
  normalizes Windows-style relative separators, and rejects absolute, rooted,
  or escaping paths.

## Implemented Action Verification Bridge

The composite GitHub Action now exposes verification evidence without changing
the default command-execution boundary.

Current Action inputs:

- `command: verify`
- `verify-run: "false"` by default
- `verify-command` as newline-separated repo-owned commands
- `verify-timeout-seconds`
- `json-report` for the target-relative verify JSON payload

Boundary:

- Action verify plan mode is read-only by default.
- Action verify run mode requires `verify-run: "true"`.
- Failed or timed-out run checks return exit code `1`.
- Blocked run checks return exit code `2`.
- `html-report` remains unsupported for verify reports.
- The Action writes `verify-verdict` as an output for CI routing.

## Implemented Generated Verification Evidence Guidance

Generated harnesses now explain how to turn explicit verify runs into durable
project evidence. `verification-matrix.md` tells maintainers to use
`harnessforge verify --target . --run --json-report
docs/harness/evidence/verify-<date>.json`, review failed, timed-out, or
blocked checks, and keep long logs and secrets out of durable docs.

`evidence-log.md` and `release-controls.md` now carry the same boundary:
runnable check evidence is useful release evidence, but it does not replace
`harnessforge audit` for structural harness score and does not prove
real-agent effectiveness.

## Local Reference Findings

### AWMAN

Useful ideas:

- `ready` is a staged preflight, not just a help command. It checks config,
  runtime, base image, agent image, local agent availability, audit, ASPEC
  folder presence, and work-item config.
- Workflow files are structured TOML/YAML with setup, main steps, teardown,
  dependency ordering, per-step agent/model choices, overlays, CI polling, and
  failure remediation.
- Workflow state is persisted with schema version, invocation id, step states,
  phase state, timestamps, and interrupted-running-step detection.
- Worktree isolation is treated as a first-class safety/UX feature, with
  merge/discard/keep outcomes and conflict recovery instructions.
- Configuration precedence is explicit: flags, environment, repo config, global
  config, built-in defaults.
- Runtime selection is fail-closed. Invalid runtime names are fatal rather than
  silently falling back to a weaker isolation model.
- Overlay and credential rules are explicit. Sensitive environment variables
  are named, masked, and scoped.

What HarnessForge should adopt:

- A read-only readiness report that explains why a target repo is ready,
  warning, or blocked for harness generation and maintenance.
- Detection for repo-owned workflow definitions, work-item templates, and
  existing readiness scripts.
- Better reporting of configuration precedence and project-owned harness
  control planes.
- Warnings when detected workflow/setup/remediation surfaces are likely to run
  commands, use credentials, or push changes.

What HarnessForge should not adopt by default:

- Container, microVM, remote-agent, or TUI orchestration.
- Autonomous setup/teardown/remediation workflows.
- AWMAN-specific ASPEC paths, workflow schemas, or agent names as requirements.

### ASPEC

Useful ideas:

- Specs are the source of truth for architecture, security, UX, local
  development, CI/CD, operations, subagents, and work items.
- The daily workflow starts with a work-item template and ends with
  implementation, tests, build, and docs aligned to the project spec.
- Agent instruction files should be refreshed after the spec changes.
- Published docs should describe current user-facing behavior, not work-item
  implementation notes.

What HarnessForge should adopt:

- Stronger detection of source-of-truth spec surfaces, including `aspec/`,
  `specs/`, `docs/architecture`, `docs/security`, `work-items`, and similar
  generic patterns.
- A future spec-sync check that reports whether instruction files point agents
  to the detected source-of-truth docs.
- Optional generated review placeholders that ask maintainers to confirm the
  source-of-truth docs and work-item location.

What HarnessForge should not adopt by default:

- Copying ASPEC templates into existing repos.
- Treating `aspec/` as the only valid spec layout.
- Making every target repo define personas, RBAC, subagents, or work items.

### Maki

Useful ideas:

- Context economy is a product feature. Maki optimizes for compact prompts,
  concise tool descriptions, high-signal file skeletons before full reads, and
  token/cost visibility.
- The `justfile` exposes a full CI aggregate target and generated-doc checks.
- Permission scopes are structured by tool and target, not only by prompt.
- Plugin permissions are explicit and fail closed when manifests are missing or
  invalid.
- Generated documentation is code-owned and checked by `gen-docs-check`.
- Contribution guidance emphasizes simplification, no trivial comments, and
  tests that prove behavior rather than implementation noise.

What HarnessForge should adopt:

- Approximate context-budget and duplication audit signals for generated and
  enhanced instruction surfaces.
- Permission/governance inventory for detected MCP, agent settings, hooks,
  permission files, and tool registries.
- Stronger generated-doc drift signals for repos with docgen targets.
- Benchmark or audit evidence that generated instructions reduce context load
  rather than adding noise.

What HarnessForge should not adopt by default:

- A plugin runtime, memory system, provider registry, or agent UI.
- Project-specific Rust coding rules from Maki.
- AI-use disclosure language or Maki's personal contribution workflow.

### Harness Forge And Meta-Harness

Useful ideas:

- Harness quality can be measured as a search problem over the code around a
  fixed model: memory, retrieval, context assembly, summarization, prompt
  templates, and tool-selection logic.
- The most reusable pattern is the five-block evaluation setup: one swappable
  candidate interface, a cheap deterministic scorer, a held-out corpus split,
  a proposer prior, and a persistent run log/frontier.
- The "frozen replay" failure mode is directly relevant to HarnessForge's
  benchmark ambitions. If a candidate cannot change the quality score, the
  benchmark is only optimizing cost and should not be used as effectiveness
  evidence.
- Quality should often be a hard do-no-harm floor while cost, context size, or
  latency is minimized. This is a stronger first benchmark shape than a broad
  "maximize agent quality" claim.
- Worst-case quality per record matters. Averages can hide one catastrophic
  failure, so real-agent or harness-quality evals should track both mean and
  minimum quality.
- Full-history logs matter for harness search. The proposer needs queryable
  access to prior code, scores, and execution traces rather than only scalar
  scores or short summaries.
- Short trial runs are useful for debugging the skill or proposer instructions
  before spending budget on a full search.
- Proposed harness candidates should pass lightweight validation, such as
  import/instantiate/smoke checks, before expensive evaluation.
- Evaluation should run outside the proposer and write machine-readable
  artifacts that simple tools can search, diff, and summarize.
- Path-based detection should recognize agent skill directories, plugin
  manifests, and installer scripts as governance surfaces. A read-only
  HarnessForge pass against this repo originally missed those surfaces and
  incorrectly reported `ready`.

What HarnessForge should adopt:

- Add frozen-replay, held-out split, anti-leakage, proxy-fidelity, and
  do-no-harm-floor language to any future real-agent eval guidance.
- Treat deterministic project/harness eval commands as product assets and
  surface them in readiness when they are discoverable.
- Keep benchmark evidence separate from structural audit scores, and require
  candidate-sensitive metrics before claiming harness effectiveness.
- Report agent skill, agent plugin, and installer-script surfaces in
  `governanceInventory`.

What HarnessForge should not adopt by default:

- A Claude-only skill runtime, native Workflow search loop, proposer agents, or
  Pareto optimizer.
- Installing skills, plugin manifests, or proposer-prior files into arbitrary
  target repos.
- `curl | bash` installation as the default HarnessForge onboarding path.
- Auto-promoting generated or evolved candidates without human review and
  held-out validation.

Sources:

- local Harness Forge sibling repo supplied by the user
- user-supplied local Meta-Harness paper PDF
- arXiv HTML for `2603.28052v1`

## Public Source Findings

### OpenAI Harness Engineering

OpenAI frames harness work as environment design, intent specification, and
feedback loops. The most relevant product idea for HarnessForge is to make
application behavior legible to agents through deterministic tools, scripts,
logs, screenshots, browser checks, and repo-owned skills.

HarnessForge implication: do not stop at instruction files. Improve the
discoverability and execution contract for the checks that prove work.

Source: https://openai.com/index/harness-engineering/

### Martin Fowler Harness Engineering

Fowler's guide/sensor model is a good mental model for this project. Guides
are feedforward context such as rules, docs, how-tos, and examples. Sensors are
feedback loops such as static analysis, logs, browser checks, and review agents.
The "harnessability" section also matters: some repos are easier to harness
because their boundaries, type systems, and verification tools are clearer.

HarnessForge implication: add audit output that distinguishes guide quality,
sensor quality, and harnessability risk instead of only asking whether files
exist.

Source: https://martinfowler.com/articles/harness-engineering.html

### LangChain Harness Sources

LangChain's anatomy and middleware articles emphasize state, tools, memory,
sandboxing, hooks, dynamic tool selection, summarization, and human-in-the-loop
interrupts.

HarnessForge implication: these are not default generated files, but they are
useful inventory categories. HarnessForge should detect and report them when a
repo already has them.

Sources:

- https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
- https://www.langchain.com/blog/how-middleware-lets-you-customize-your-agent-harness

### Public HarnessForge-Like Repo

The public `jcaiagent7143-ui/harnessforge` repo has useful UX patterns:

- Deterministic inspection before generation.
- Profile versus blueprint separation.
- Dry-run distinct from verification.
- Stable `verify --json` protocol.
- Real-agent A/B benchmark methodology with caveats.
- `sync --check` as a discoverable drift check.

HarnessForge implication: keep current conservative defaults, but borrow the
UX split: inspect profile, preview writes, verify project outputs, and check
drift as separate commands.

Sources:

- https://github.com/jcaiagent7143-ui/harnessforge
- https://github.com/jcaiagent7143-ui/harnessforge/blob/main/docs/reference/verify-protocol.md
- https://github.com/jcaiagent7143-ui/harnessforge/blob/main/BENCHMARKS.md

### Code As Agent Harness And Paper Catalog

The survey frames code as executable, inspectable, and stateful harness
material. It highlights planning, memory, tool use, deterministic sensors,
permissioned state transitions, multi-agent state, and regression-free harness
improvement.

The companion paper catalog adds a useful taxonomy: harness interface,
harness mechanisms, scaling the harness, and application domains. Its release
notes also reinforce source-list quality controls: every public paper row needs
a canonical URL, venue/arXiv IDs should be audited, and missing citations
should be explicit instead of silently invented.

HarnessForge implication: project-check contracts, eval evidence, and source
integrity are more important than generating larger prose files. For this repo,
that means advisory eval inventory and an effectiveness evidence contract. For
generated target repos, this should remain a lightweight boundary rather than a
large research bibliography.

Sources:

- https://arxiv.org/html/2605.18747v1
- https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers

### Deeper Code-As-Harness Catalog Mining

The full paper catalog is a useful product map, not just a reading list. The
README organizes 458 paper rows across interface, mechanism, scaling, and
application axes. Several papers intentionally appear in multiple sections,
which is a useful signal for HarnessForge: mature harnesses combine role
ownership, feedback channels, shared state, and convergence criteria.

Transferable ideas:

- Use a three-part interface model for effectiveness claims: reasoning surface,
  action surface, and environment surface. A claim should say which one
  changed.
- Treat harness mechanisms as review surfaces: planning, memory/context, tool
  use, feedback handling, deterministic verification, and permissioned state
  transitions.
- For multi-agent harnesses, require explicit role ownership, interaction mode,
  topology, shared representation, synchronization rule, and convergence rule
  before treating results as comparable.
- Separate feedback channels. Compile errors, tests, runtime exceptions, static
  analysis, fuzzing, simulation, profiling, human critique, and trajectory
  safety measure different things.
- Treat adaptive harness evolution as a governed promotion loop: collect
  observations, diagnose failure or waste, propose a candidate, replay/evaluate,
  and promote only after review.
- Keep domain harnesses project-owned. GUI/OS agents, scientific-discovery
  agents, embodied agents, recommender agents, compilers, and cloud operations
  need their own tools, simulators, safety rules, and benchmarks.
- Treat source ledgers as product quality surfaces. Canonical URLs, missing
  citation records, stale venue checks, dedup policy, and broken-link checks
  matter when research claims drive product behavior.

HarnessForge actions from this pass:

- Strengthen `effectiveness-eval-contract.md` with surface taxonomy, feedback
  channels, multi-agent/adaptive addendum, and source-catalog hygiene.
- Keep `effectivenessInventory` advisory and path-based. It should identify
  eval review surfaces without running target benchmarks or reading private
  result contents.
- Keep generated target repos lightweight. Do not generate multi-agent
  topologies, domain simulators, learned governance, dynamic memory systems, or
  research bibliographies by default.

### Additional Harness-Eval Papers

The arXiv/paper-catalog pass surfaced several reusable ideas:

- AutoHarness: invalid-action prevention and environment feedback are harness
  responsibilities, but generated target repos should not receive synthesized
  runtime policy code by default.
- Agentic Harness Engineering, VeRO, and Meta-Harness: evolved harness changes
  need versioned components, observations, candidate identifiers, predictions
  or rewards, budget-controlled runs, and queryable logs.
- Natural-Language Agent Harnesses: harness policy can be represented as
  inspectable modules, but HarnessForge should keep that as documentation and
  review structure rather than a new runtime language.
- Claw-SWE-Bench and RealClawBench: cross-agent comparisons need adapter
  contracts, reconstructed environments, fixed prompts, runtime budgets,
  patch extraction, deterministic scorers, and cost accounting.
- ClawsBench and Agent-ValueBench: success, safety, values, and trajectory
  behavior must be reported separately.
- Terminal-agent and compiler-harness papers: domain-specific harnesses need
  domain tools and benchmarks. HarnessForge should detect and route to existing
  project checks rather than generate domain-specific automation.

Sources:

- https://arxiv.org/abs/2603.03329
- https://arxiv.org/abs/2604.25850
- https://arxiv.org/abs/2602.22480
- https://arxiv.org/abs/2603.25723
- https://arxiv.org/abs/2606.12344
- https://arxiv.org/abs/2606.03889
- https://arxiv.org/abs/2604.05172
- https://arxiv.org/abs/2605.10365
- https://arxiv.org/abs/2603.05344
- https://arxiv.org/abs/2603.20075

### OpenHarness

OpenHarness provides useful UX examples:

- `--dry-run` previews runtime settings, auth state, skills, commands, tools,
  and MCP configuration without model or tool execution.
- Dry-run reports `ready`, `warning`, or `blocked` with concrete next actions.
- Skills, memory, permissions, hooks, MCP, tasks, and coordination are explicit
  runtime categories.

HarnessForge implication: `inspect` should grow toward a static readiness
preview with next actions, while staying separate from any runtime agent loop.

Source: https://github.com/HKUDS/OpenHarness

### GitHub Agent Governance

GitHub's governing-agents guidance treats MCP registry curation, protected MCP
configuration, agent setup workflows, ephemeral runners, code review, CI, and
security scans as governance controls.

HarnessForge implication: detect these as high-risk harness surfaces and
recommend review, but do not generate them by default.

Source: https://wellarchitected.github.com/library/governance/recommendations/governing-agents/

### Anthropic Permission Guidance

Claude Code auto mode and best-practice guidance reinforce a core point:
approval fatigue is real, but the fix is structured authorization, sandboxing,
and specific allowlists rather than broad trust.

HarnessForge implication: optional future agent-platform adapters should
prefer narrow allowlists and explicit permission review over broad permission
shortcuts.

Sources:

- https://www.anthropic.com/engineering/claude-code-auto-mode
- https://www.anthropic.com/engineering/claude-code-best-practices

### Spec-Driven Development Sources

The GitHub Spec Kit launch article frames the workflow as four reviewed phases:
specify, plan, tasks, and implement. The useful HarnessForge signal is the
explicit checkpoint between each phase, plus the emphasis that tasks should be
small, reviewable, and independently testable. The article also raises
organization-scale questions that matter for HarnessForge: managing many spec
files, diffing implementations, and keeping specs usable rather than tedious.

The local Spec Kit checkout adds concrete repo patterns:

- `.specify/memory/constitution.md` is persistent project context.
- `.specify/feature.json` identifies the active feature directory without
  relying on branch naming.
- `specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `research.md`,
  `data-model.md`, `quickstart.md`, `contracts/`, and `checklists/` form a
  feature-scoped artifact set.
- `spec.md` separates user intent from implementation details, with
  acceptance scenarios, functional requirements, measurable success criteria,
  edge cases, assumptions, and explicit clarification markers.
- `plan.md` contains a constitution check, technical context, structure
  decision, and complexity tracking.
- `tasks.md` groups implementation by independently testable user stories and
  uses stable task IDs, parallel markers, story labels, file paths, and
  dependency sections.
- `checklist` treats checklist items as "unit tests for English": requirements
  quality checks, not implementation tests.
- `analyze` is a read-only cross-artifact consistency report across spec,
  plan, tasks, and constitution.
- The built-in workflow uses human review gates between specify, plan, and
  tasks before implementation.

Fowler's SDD article adds two important cautions. First, spec-driven
development has at least three lifecycle levels: spec-first, spec-anchored,
and spec-as-source. Repos may use only one of these, and HarnessForge should
not infer stronger semantics than the repo documents. Second, there is a real
risk that SDD tools create too many files, review burden, and ambiguous
responsibility for product analysis. HarnessForge should surface that risk as
quality/readiness evidence rather than amplify it with generated defaults.

The specdriven.ai methodology reinforces a six-phase shape: constitution,
specify, clarify, plan, tasks, and implement/iterate. Its strongest fit for
HarnessForge is the static audit vocabulary: source-of-truth, clarification,
technical blueprint, atomic tasks, embedded acceptance criteria, and human
review checkpoints.

HarnessForge implications:

- Detect Spec Kit and similar SDD layouts as existing source-of-truth systems:
  `.specify/`, `.specify/memory/constitution.md`, `.specify/feature.json`,
  `specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `checklists/`, and
  `contracts/`.
- Report the active feature directory from `.specify/feature.json` when
  present, validating that it stays inside the repo and that referenced
  artifacts exist.
- Classify likely artifact roles: global context, feature spec, plan, task
  list, quality checklist, research notes, data model, contracts, and
  quickstart.
- Add read-only quality signals for unresolved `[NEEDS CLARIFICATION]`
  markers, incomplete requirement checklists, missing plan/tasks after a spec,
  missing trace IDs, and tasks without file paths.
- Distinguish general repo memory/context from feature-scoped specs in
  generated or enhanced instruction routing.
- Ask maintainers to declare the spec lifecycle model when possible:
  spec-first, spec-anchored, spec-as-source, flow-back, flow-forward, or
  living spec.

What HarnessForge should not adopt by default:

- Installing Spec Kit, `.specify`, slash commands, agent integrations,
  workflow YAML, catalogs, presets, extensions, or agent context markers into
  arbitrary target repos.
- Treating any one SDD folder structure as mandatory.
- Claiming specs are executable or authoritative unless the target repo
  explicitly declares that convention.
- Running AI workflows or target repo commands during static inspect, audit,
  or readiness reporting.

Sources:

- https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- local Spec Kit checkout supplied by the user
- https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- https://specdriven.ai/

## Ranked Backlog

### P0: Next Implementation Candidates

1. Implemented: add `harnessforge inspect --readiness --json`.
   - Output: `verdict`, `warnings`, `blockedReasons`, `nextActions`,
     `sourceOfTruth`, `runnableChecks`, `generatedDrift`, and
     `reviewRequired`.
   - Must stay read-only and avoid running target repo commands.

2. Implemented: add source-of-truth spec sync detection.
   - Detect likely spec roots, `.specify` systems, active feature metadata,
     and work-item templates.
   - Identify global context versus feature-scoped spec artifacts.
   - Report unresolved clarification markers, incomplete requirement
     checklists, missing plan/task artifacts, and missing traceability as
     static quality signals.
   - Report whether generated/enhanced instruction files route agents to those
     roots.
   - Add audit findings for missing routing when specs exist.

3. Implemented: add `sync --check` as a discoverable preflight.
   - Wraps readiness, generated-file drift, source-of-truth spec routing,
     and existing review-required surfaces.
   - Returns CI-oriented exit codes: ready `0`, warning `1`, blocked `2`.
   - No write semantics and no target command execution.

4. Implemented: `verify --json` default plan mode separately from `audit --json`.
   - `audit` scores harness structure.
   - `verify` reports project checks with stable planned/blocked statuses,
     messages, and reserved run-mode fields.
   - Default mode is static and does not run target repository commands.
   - Explicit `--run` mode records executed check evidence when requested.
   - Contract doc, schema, example payload, and CLI modes now exist.

### P1: Important After P0

5. Implemented: add workflow and work-item inventory.
   - Detect `aspec/workflows`, workflow TOML/YAML files, work-item directories,
     and templates.
   - Report setup, teardown, remediation, push, PR, CI-polling, and credential
     surfaces when parseable.
   - Readiness JSON now reports `workflowInventory` and `workItemInventory`
     with advisory review warnings and review-required items.

6. Implemented: add context-budget and duplication audit.
   - Report large instruction files, duplicated router content, and generated
     files that repeat canonical docs too heavily.
   - Readiness JSON now reports `contextBudget` with instruction-file line and
     character counts plus duplicate instruction-block pairs.
   - Findings remain advisory until thresholds are proven on real repos.

7. Implemented: add permission/governance inventory.
   - Detect MCP configs, agent settings, hooks, permission files, cloud-agent
     setup workflows, devcontainers, and sandbox configs.
   - Mark these as review-required security surfaces.
   - Readiness JSON now reports `governanceInventory` for MCP configs, agent
     settings, agent skills, agent plugin manifests, installer scripts, hooks,
     devcontainers, sandbox configs, Copilot setup workflows, and environment
     files/templates.

8. Implemented: add first-run guided UX.
   - A `quickstart` or `wizard` command can explain what will be generated,
     which files will be preserved, what review placeholders remain, and which
     command proves readiness.
   - Include detected spec-system next steps when `.specify`, `specs/`, or
     work-item systems already exist.
   - `harnessforge quickstart` is read-only and composes detected context,
     readiness, dry-run generation planning, preserved-file reporting, review
     placeholders, and next commands.

9. Implemented: add a generated first-agent harness improvement instruction.
   - When HarnessForge generates a harness, include a clear first instruction
     for the first agent session in that target repo.
   - The instruction should ask the agent to use the generated harness
     structure, detection output, readiness signals, component inventory,
     change contract, verification matrix, evidence log, and security
     boundaries to perform deeper repository analysis than static scripts and
     templates can safely perform.
   - The agent should propose or make reviewed improvements to the generated
     harness, such as better component boundaries, verification commands,
     source-of-truth routing, project-specific guardrails, evidence sensors,
     and stale or missing context.
   - Preserve the core boundary: do not inject HarnessForge maintainer
     preferences, do not overwrite project-owned instructions without explicit
     force/review, do not run target commands unless the project has an
     approved verification route, and record any project-specific assumptions
     as review-required until a maintainer accepts them.
   - Implemented as a short generated startup-path section in the canonical
     agent instruction file plus dedicated
     `docs/harness/state/first-agent-task.md`, with the task marked
     review-required in generated manifests.

### P2: Closed Or Deferred Before Release Prep

10. Deferred: add blueprint mode only as explicit opt-in.
   - Useful for domains like RAG, support, workflow automation, finance, and
     browser agents.
   - Needs validators and real evals before it becomes a public quality claim.
   - Keep out of default generation for the first release.

11. Implemented as local evidence contracts: measured real-agent evals.
    - Use fixed task prompts, isolated workspaces, control versus harness arms,
      mechanical scoring, defect evidence, and caveats.
    - Store reproduction commands and reject marketing claims from tiny samples.
    - Include frozen-replay checks, candidate-sensitive quality metrics,
      held-out splits, anti-leakage rules, worst-case quality, and
      do-no-harm-floor cost optimization before promoting any benchmark claim.
    - `effectivenessInventory`, `effectiveness-eval-contract.md`, and
      `effectiveness-evidence.schema.json` now provide the advisory inventory
      and review contract. No benchmark runner is generated by default.

12. Implemented: source-verified platform adapter metadata.
    - Cursor, Windsurf, Continue, Aider, Claude skills/subagents, Copilot MCP,
      and future platform files all have moving load rules.
    - Keep generated/local boundaries explicit.
    - Generated manifests now include `platformSourceReview`, and generated
      change contracts require current primary-source evidence before platform
      floor, interpreter, runner-label, or CI-image changes.

13. Implemented: optional sandbox/container readiness profile.
    - Detect Dockerfile.dev, devcontainers, runtime manifests, and platform
      constraints.
    - Do not attempt to build or install runtimes by default.
    - `governanceInventory` now reports devcontainers, sandbox configs, and
      container runtime files as review-required surfaces.

14. Implemented: session snapshot mode.
    - Dedicated harness-docs and AGENTS mining reviewed Bluepeak-AI and
      JobSentinel root `AGENTS.md` files plus their harness docs. The supplied
      paper catalog checkout had no root `AGENTS.md`.
    - `harnessforge session` gives a restart snapshot of git state, readiness,
      harness audit summary, state-file presence, and next actions.
    - It stays read-only, writes nothing, and does not execute target checks.

15. Implemented: diff-aware verification planner.
    - `harnessforge plan --since <ref>` inspects changed files with `git diff`
      and maps them to detected or explicit project verification checks.
    - JSON output uses schema `harnessforge.plan.v1`, redacts target roots, and
      reports changed files, planned checks, matched files, unmatched files,
      reasons, warnings, and blockers.
    - It stays read-only, writes nothing, and does not execute target checks.

## Rejected Defaults

These ideas can be useful in specific products, but should not be default
HarnessForge generator behavior:

- Generating large `SKILLS/`, `MEMORY.md`, MCP config, browser credentials, or
  platform permission files into arbitrary repos.
- LLM-assisted init-time profile refinement by default.
- Copying ASPEC, AWMAN, Maki, or public HarnessForge templates into target
  repos.
- Creating autonomous setup, teardown, self-heal, push, or PR workflows by
  default.
- Installing Spec Kit, `.specify`, agent slash commands, presets, extensions,
  catalogs, or workflow engines by default.
- Treating structural audit scores as proof of real agent effectiveness.
- Falling back silently from a requested platform or runtime contract to a
  weaker one.
- Overwriting coherent existing spec, workflow, or instruction systems.

## Suggested Next Step

The non-release backlog is closed for the current release-prep boundary. The
remaining release work is manual macOS/Windows platform CI, the `v1` Action tag
decision, and release-time SBOM/provenance gates.
