# Effectiveness Eval Contract

Status: proposed

This document defines what HarnessForge should require before anyone treats a
benchmark, eval, or real-agent run as evidence that a harness improves agent
effectiveness.

This is separate from:

- `audit`, which scores harness structure.
- `inspect --readiness`, which reports static repo signals.
- `sync --check`, which turns readiness into CI-oriented exit codes.
- `verify --json`, which is a planned project-check report contract.

Structural audit and project verification can show that a repo is coherent and
checkable. They do not prove that a generated or modified harness makes agents
better at real tasks.

## Minimum Evidence

An effectiveness claim needs:

- Harness layer: whether the change affects reasoning, action, environment
  modeling, planning, memory/context, tool use, feedback handling,
  multi-agent coordination, or promotion controls.
- Candidate harness surface: the instruction, retrieval, memory, context,
  tool-routing, workflow, or verification surface being compared.
- Baseline and control arm: what the candidate is being compared against.
- Versioned candidate snapshot: the exact candidate code, instructions, config,
  adapter, and runtime settings that were evaluated.
- Candidate-sensitive metric: a quality metric that can change for quality
  reasons when the candidate changes.
- Held-out split or contamination control: what the proposer, generator, or
  optimizer could not see.
- Worst-case quality: the minimum or tail result, not only average quality.
- Cost axis: tokens, context size, latency, tool calls, dollar cost, or another
  bounded resource when relevant.
- Runtime budget: wall-clock, model-call, token, tool-call, and retry limits.
- Workspace contract: filesystem state, dependency state, network access,
  patch extraction, cleanup, and scoring entrypoint.
- Adapter contract: how heterogeneous agents or harnesses are normalized before
  comparison.
- Do-no-harm floor: the minimum acceptable quality when optimizing cost.
- Replay type: live run, counterfactual replay, or frozen replay.
- Trajectory safety: resource access, permission-boundary compliance,
  information-flow constraints, and mid-run violations, not only final output.
- Reproduction command: the command or procedure that produced the result.
- Human review: confirmation that the result is not a reward bug, leakage, or
  fixture-specific shortcut.

## Harness Surface Taxonomy

Before comparing candidates, name the surface being changed:

- Reasoning surface: code or structured artifacts used to externalize
  inference, intermediate reasoning, solver calls, or execution-guided
  refinement.
- Action surface: tool calls, APIs, shell commands, GUI/OS operations,
  workflow actions, generated policies, or skill selection.
- Environment surface: repository state, logs, traces, tests, fixtures,
  simulators, sandbox state, and history exposed to the agent.
- Mechanism surface: planning, memory/context, tool selection, execution
  feedback, deterministic verification, or permissioned state transitions.
- Scaling surface: role specialization, interaction mode, workflow topology,
  shared representation, synchronization, or convergence rule.

Broad claims such as "better harness" are not enough. The claim should say
which surface changed and which measured feedback channel could show an
improvement.

## Feedback Channels

An eval should identify the feedback channel it relies on:

- compile or syntax feedback;
- test pass/fail feedback;
- runtime error or stack-trace feedback;
- static-analysis or security feedback;
- fuzzing or simulation feedback;
- profiling, latency, token, cost, or tool-call feedback;
- human critique or review feedback;
- trajectory, permission, and state-transition feedback.

Final output quality is only one channel. When a harness coordinates tools,
agents, sandboxes, or stateful workflows, the eval must also account for
mid-run failures and invalid actions.

## Frozen Replay Boundary

Frozen replay is useful for some cost and context-budget questions, but it can
silently invalidate quality claims. If the candidate cannot change the quality
score because the outputs are already recorded, the result is not evidence of
harness effectiveness.

Frozen replay reports must say exactly what can vary. If only cost can vary,
the claim must be limited to cost, context size, latency, or another measured
resource.

## Good First Shape

The safest first benchmark shape is usually:

1. Fix a baseline harness.
2. Choose a small repeated task set that the baseline does not already
   saturate.
3. Define a deterministic candidate-sensitive metric.
4. Require a do-no-harm floor on worst-case quality.
5. Optimize or compare cost only after the quality floor is met.
6. Evaluate the selected candidate once on held-out tasks.
7. Store commands, scores, logs, traces, candidate identifiers, runtime budget,
   and workspace contract in machine-readable files.
8. Review trajectory safety and boundary compliance before promoting the
   candidate.

This favors modest claims with reproducible evidence over broad agent-quality
marketing.

## Machine-Readable Evidence

The evidence schema lives at
[effectiveness-evidence.schema.json](effectiveness-evidence.schema.json). A
representative non-claim example lives at
[effectiveness-evidence-example.json](effectiveness-evidence-example.json).

The schema is intentionally a review contract, not an eval runner. It records:

- the exact claim and whether the result is promoted, rejected, deferred, or
  still inconclusive;
- the target, candidate snapshot, baseline snapshot, changed harness surfaces,
  and control arm;
- the held-out task set, contamination controls, replay type, feedback
  channels, runtime budget, workspace contract, adapter contract, and
  reproduction command;
- candidate-sensitive primary metrics, worst-case quality, do-no-harm floors,
  and cost dimensions;
- trajectory and permission-boundary review;
- result artifacts, reviewer metadata, rollback notes, and human approval.

Keeping this separate from `verify --json` preserves a hard boundary:
verification can prove project checks were planned or run, while effectiveness
evidence must prove that the candidate harness changed real task outcomes under
a fair comparison.

## Source-Mined Design Notes

Recent harness papers and the Code as Agent Harness paper catalog point toward
useful eval discipline, but most of those ideas are too heavy for default
generation.

- Code as Agent Harness and the companion paper catalog separate harness work
  into interface, mechanism, scaling, and application layers. An eval claim
  should name which layer changed.
- The catalog duplicates important papers across roles, feedback channels, and
  convergence types. That duplication is a useful signal: strong harnesses are
  usually multi-role systems, not single-purpose prompts.
- AutoHarness shows that harness code can prevent invalid actions. HarnessForge
  should ask for invalid-action and boundary tests when present, not synthesize
  runtime policy code by default.
- Agentic Harness Engineering, VeRO, and Meta-Harness all reinforce versioned
  candidate snapshots, budget-controlled runs, queryable observations, and
  falsifiable candidate records.
- Natural-Language Agent Harnesses reinforces that harness policy documents can
  be inspectable modules. HarnessForge should keep generated docs reviewable
  and modular without becoming a runtime controller.
- Claw-SWE-Bench and RealClawBench reinforce adapter contracts, reconstructed
  workspaces, patch extraction, deterministic scorers, and fixed runtime
  budgets for fair comparison across harnesses.
- ClawsBench and Agent-ValueBench reinforce separate success, safety, value,
  and trajectory checks. A high final task score is not enough.
- Domain-specific harness papers such as compiler repair show that specialized
  tools and benchmarks can matter. HarnessForge should detect and route to
  repo-owned domain checks instead of generating domain harnesses itself.

## Multi-Agent And Adaptive Harness Addendum

If a candidate uses multiple agents or adaptive harness evolution, the eval
record must also name:

- role ownership: planner, coder, reviewer, tester, verifier, executor,
  red-team, or another repo-owned role;
- interaction mode: collaboration, critique, debate, adversarial validation, or
  another explicit mode;
- topology: chain, cyclic, hierarchical, star, blackboard, parallel branches,
  adaptive DAG, or another explicit topology;
- shared representation: files only, repository state, execution traces,
  database, blackboard, or another explicit shared substrate;
- synchronization rule: how conflicting observations, branches, memories, or
  proposed patches are merged or rejected;
- convergence rule: correctness, security, performance, score threshold,
  consensus, human approval, or another explicit stop condition.

Adaptive harness changes must follow a governed loop: collect observations,
diagnose failure or waste, propose a versioned candidate, replay or evaluate on
held-out tasks, then promote only after review.

## Source Catalog Hygiene

Benchmark and research source ledgers are product surfaces. They should keep:

- canonical URLs, preferably arXiv abstract pages, official venue pages, DOI
  links, project pages, or official docs;
- explicit missing-citation records instead of invented or uncited entries;
- recurring review of stale venue tags, paper IDs, and duplicated entries;
- a clear deduplication policy when one source belongs to multiple harness
  roles;
- link checks in CI only when the project owner accepts the network and
  maintenance cost.

## Readiness Signals

`inspect --readiness` may report obvious eval assets such as `evals/`,
`benchmarks/`, scorer scripts, result logs, or frontier files. That inventory
means review is possible. It does not mean the eval is valid.

When eval assets are detected, review:

- whether the scorer is candidate-sensitive;
- whether there is a held-out split or contamination control;
- whether average and worst-case quality are tracked;
- whether result logs are queryable and tied to candidate identifiers;
- whether runtime budgets, workspace contracts, and adapter behavior are
  explicit;
- whether the harness layer, feedback channel, role ownership, topology, and
  convergence rule are named when relevant;
- whether trajectory safety and permission-boundary failures are captured;
- whether the benchmark claim is separate from structural audit scores.

## Promotion Boundary

Evolved, synthesized, or benchmark-winning harness changes are proposals. They
must not become default generated content or project policy until they have:

- a versioned diff;
- passing lightweight validation;
- reproducible eval evidence;
- rollback instructions;
- human approval for the target repo.

## Non-Goals

- Do not run project benchmarks during static readiness.
- Do not install benchmark dependencies by default.
- Do not generate proposer agents, optimizer workflows, skill packs, or Pareto
  search loops into arbitrary target repos.
- Do not auto-promote a candidate from benchmark output alone.
- Do not treat a structural score, smoke test, or frozen replay as proof of
  real agent effectiveness.
