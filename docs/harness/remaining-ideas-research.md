# Remaining Ideas Research

Reviewed: 2026-06-15 UTC.

Scope: local `awman`, `aspec`, and `maki`; the public
`jcaiagent7143-ui/harnessforge`; OpenAI, Martin Fowler, LangChain,
OpenHarness, Walking Labs, and current harness-engineering research sources.

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
review.

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
| Real-agent evaluation harness | Public HarnessForge A/B benchmark, OpenAI/Fowler feedback-loop claims | Build a repeatable local benchmark protocol for generated harness quality | Do not market structural audit as real agent effectiveness |
| Config precedence report | AWMAN layered config model | Show which overrides shaped detection: CLI flags, detected files, generated manifest, existing project ownership | Keep deterministic; no LLM refinement needed |
| Short `sync --check` alias | Public HarnessForge quickstart, current drift-report UX | Add a discoverable CI-oriented alias for `update --drift-report --json` | Alias only; no new mutation semantics |

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

### Code As Agent Harness

The survey frames code as executable, inspectable, and stateful harness
material. It highlights planning, memory, tool use, deterministic sensors,
permissioned state transitions, multi-agent state, and regression-free harness
improvement.

HarnessForge implication: a future project-check contract and benchmark loop
are more important than generating larger prose files.

Source: https://arxiv.org/html/2605.18747v1

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

## Ranked Backlog

### P0: Next Implementation Candidates

1. Add `harnessforge inspect --readiness --json`.
   - Output: `verdict`, `warnings`, `blockedReasons`, `nextActions`,
     `sourceOfTruth`, `runnableChecks`, `generatedDrift`, and
     `reviewRequired`.
   - Must stay read-only and avoid running target repo commands.

2. Add source-of-truth spec sync detection.
   - Detect likely spec roots and work-item templates.
   - Report whether generated/enhanced instruction files route agents to those
     roots.
   - Add audit findings for missing routing when specs exist.

3. Design `verify --json` separately from `audit --json`.
   - `audit` scores harness structure.
   - `verify` should report project check results with stable statuses,
     durations, messages, and exit codes.
   - Default should be plan/static mode unless the user explicitly allows
     command execution.

4. Add `sync --check` as a discoverable drift alias.
   - It should wrap existing drift-report behavior.
   - No new write semantics.

### P1: Important After P0

5. Add workflow and work-item inventory.
   - Detect `aspec/workflows`, workflow TOML/YAML files, work-item directories,
     and templates.
   - Report setup, teardown, remediation, push, PR, CI-polling, and credential
     surfaces when parseable.

6. Add context-budget and duplication audit.
   - Report large instruction files, duplicated router content, and generated
     files that repeat canonical docs too heavily.
   - Keep the score advisory until thresholds are proven on real repos.

7. Add permission/governance inventory.
   - Detect MCP configs, agent settings, hooks, permission files, cloud-agent
     setup workflows, devcontainers, and sandbox configs.
   - Mark these as review-required security surfaces.

8. Add first-run guided UX.
   - A `quickstart` or `wizard` command can explain what will be generated,
     which files will be preserved, what review placeholders remain, and which
     command proves readiness.

### P2: Longer-Term Opt-Ins

9. Add blueprint mode only as explicit opt-in.
   - Useful for domains like RAG, support, workflow automation, finance, and
     browser agents.
   - Needs validators and real evals before it becomes a public quality claim.

10. Add measured real-agent evals.
    - Use fixed task prompts, isolated workspaces, control versus harness arms,
      mechanical scoring, defect evidence, and caveats.
    - Store reproduction commands and reject marketing claims from tiny samples.

11. Add agent-platform adapters only after current source verification.
    - Cursor, Windsurf, Continue, Aider, Claude skills/subagents, Copilot MCP,
      and future platform files all have moving load rules.
    - Keep generated/local boundaries explicit.

12. Add optional sandbox/container readiness profile.
    - Detect Dockerfile.dev, devcontainers, runtime manifests, and platform
      constraints.
    - Do not attempt to build or install runtimes by default.

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
- Treating structural audit scores as proof of real agent effectiveness.
- Falling back silently from a requested platform or runtime contract to a
  weaker one.
- Overwriting coherent existing spec, workflow, or instruction systems.

## Suggested Next Step

Implement P0 in this order:

1. `inspect --readiness --json`
2. source-of-truth spec sync audit
3. `sync --check` alias
4. design-only issue/doc for `verify --json`

This sequence improves user experience immediately without expanding the
generator's default write surface.
