# Harness Token Economics Research

Status: in progress.

Reviewed: 2026-06-16 UTC.

## Question

Do comprehensive repository harnesses increase or decrease agent token
consumption in real work?

## Current Conclusion

The evidence is insufficient for a universal net-token conclusion.

Current public sources and HarnessForge measurements support a narrower
conclusion: comprehensive harnesses raise the stored and potential startup
context budget, but they can reduce repeated orientation work when agents load
only relevant static context, reuse stable prompt prefixes, and avoid stale or
unfiltered context. Overloaded or poorly routed context can increase cost and
degrade quality.

Do not change generated behavior from this research alone. Use the metric
schema in [token-economics-metric.schema.json](token-economics-metric.schema.json)
to collect task traces before changing default generated sizing, routing,
summarization, or lazy-loading behavior.

## Method

- Ran a read-only Antigravity research pass from this repo to discover current
  sources and local research surfaces.
- Reviewed the Walking Labs harness-engineering lectures as mechanism context
  for why repository harnesses should affect context use and agent execution.
  Those lectures are treated as design rationale and benchmark-shaping input,
  not as primary quantitative receipts unless their cited upstream sources
  provide the measurement.
- Verified key claims against primary or high-quality public sources.
- Ran a static HarnessForge token-proxy measurement over the 14-repo offline
  public-repo fixture corpus.
- Reviewed existing large-public-repo field evidence for Kubernetes, VS Code,
  and Bazel. That evidence covers discovery, ranking, generated guidance, and
  truncation, but not real model token traces.

## Mechanism Map

The token-economics question is not "more docs good" or "fewer tokens good."
It is whether specific harness mechanisms reduce total task cost without
lowering execution quality.

The Walking Labs lectures provide the clearest mechanism map for this repo:

| Harness mechanism | Why it can improve token/context use and execution | How it can make things worse | Evidence needed |
| --- | --- | --- | --- |
| Instruction routing | A short entry file tells the agent what the repo is, how to start, and where task-specific detail lives. The agent can spend more context on the current code path instead of rediscovering project basics. | A giant always-loaded instruction file can bury critical rules, lower signal-to-noise, and consume context that should be used for code and verification. | Compare loaded instruction chars/tokens, first-edit time, relevant-doc recall, ignored hard constraints, and task quality across monolithic and routed variants. |
| Repository system of record | Project conventions, commands, decisions, and current state live in files the agent can read. This can reduce repeated orientation and contradictory assumptions. | Stale or duplicated state can mislead agents and cause rework. | Measure orientation reads, repeated discovery, stale-state incidents, and correction loops across state-present and state-missing runs. |
| Initialization phase | Separating environment readiness from feature work can keep later sessions focused on implementation rather than setup failures. | Overbuilt initialization can spend tokens and time on infrastructure the task never uses. | Track time and tokens to first passing check, setup-error loops, and later-session savings. |
| Scope control | WIP limits and completion evidence keep the agent on one task until verified, reducing broad partial edits and recovery cost. | Too-rigid scope can block useful local repairs or force extra sessions. | Track active task count, touched-file spread, retries, verified completion rate, and escaped partial work. |
| Verification feedback | Runnable checks replace agent self-confidence with external signals and can shorten blind retry loops. | Broad checks can be expensive or flaky; vague failure output can add tokens without improving the next attempt. | Record verification class, failure specificity, retry count, failure-to-fix latency, and final verdict. |
| State persistence | Current-state and decision artifacts let context resets resume without reconstructing every prior decision. | Overlong handoffs or stale decisions can become another instruction-bloat channel. | Compare restart orientation tokens, repeated file reads, contradicted decisions, and successful resume rate. |
| Observability | Task traces, runtime signals, and rubrics give the agent targeted evidence for the next action. | Logging everything can flood context and hide the few signals that matter. | Measure trace size, signal precision, diagnostic turns, blind retries, and defect escape rate. |
| Cleanup and simplification | Clean-state checks and periodic harness simplification reduce stale artifacts and remove obsolete rules. | Cleanup rules can become ceremony if they are not tied to observed failures. | Track stale artifacts, startup time, rule count, removal ablations, and do-no-harm quality results. |

This map is a hypothesis ledger. Each row names how a repository harness could
reduce or increase token use and execution cost. The metric schema requires the
mechanism under test so future records can connect measured tokens to the
harness behavior that caused them.

## Source Receipts

| Source | Finding | HarnessForge use |
| --- | --- | --- |
| [OpenAI prompt caching docs](https://developers.openai.com/api/docs/guides/prompt-caching) | Repeated static prompt prefixes such as system prompts and common instructions can reduce latency and cached input-token cost when the prefix matches. | Stable startup content should be kept ahead of dynamic task context when an agent surface supports prompt caching. |
| [Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | Prompt caching is useful for repeated instructions, large background context, and long conversations; cached reads and writes have different prices and lifetimes. | Token evidence must separate cache writes, cache reads, and uncached input instead of treating all input tokens as equal. |
| [Anthropic context-window docs](https://platform.claude.com/docs/en/build-with-claude/context-windows) and [Claude Code cost docs](https://code.claude.com/docs/en/costs) | More context is not automatically better; context should be curated, stale context should be cleared, and cost scales with context size. | A harness should make relevant state easy to find without requiring every durable doc to enter every task context. |
| [Claude Code system-prompt customization docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) | Dynamic system-prompt content can prevent shared cache reuse across directories or machines; moving dynamic context changes instruction weight. | Evaluation must record where static and dynamic context enter the agent, not only total prompt size. |
| [Walking Labs harness-engineering lectures](https://walkinglabs.github.io/learn-harness-engineering/en/) | The lectures connect harness components to concrete agent failure modes: incomplete context, missing environment readiness, scope overreach, premature completion, lost continuity, weak feedback, and missing observability. | Treat these as mechanism and benchmark-design sources. Do not treat their illustrative percentages, costs, or timing examples as HarnessForge quantitative proof unless separately verified from primary measurement artifacts. |
| [Anthropic effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) and [long-running app harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Long-running agents need structured state and handoffs across context resets; compaction alone is not enough, and context pressure can cause premature wrap-up. | `current-state.md`, task state, and clean restart artifacts can reduce reorientation, but the savings need trace evidence. |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) | Long-context models do not reliably use all positions in long inputs; relevant information placement and context curation matter. | More harness text can be harmful if important instructions are buried in noisy middle context. |
| [Meta-Harness](https://arxiv.org/abs/2603.28052) | Harness code that decides what to store, retrieve, and present can improve quality and reduce context tokens in specific evaluated systems. | The leverage is routing and retrieval policy, not simply adding more always-loaded text. |
| [SWE Context Bench](https://arxiv.org/abs/2602.08316) | Accurate summarized or retrieved prior experience can improve accuracy and reduce runtime and token cost; unfiltered or incorrect context can be neutral or negative. | Compare compact summaries, selected context, and full context as separate arms. |
| [ContextBench](https://arxiv.org/abs/2602.05892) | End-to-end success hides whether agents retrieve and use the right code context; intermediate recall, precision, and efficiency metrics expose context quality. | Token economics should measure context precision and recall, not only total tokens. |
| [SWE-Effi](https://arxiv.org/abs/2509.09853) and [SWE-agent ACI](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf) | Software-agent effectiveness needs token, time, turn, and trajectory metrics in addition to resolve rate. Failures and long trajectories can be disproportionately expensive. | The schema records tokens, turns, tool calls, retries, verification results, and failure outcomes. |
| [CodeMonkeys field report](https://scalingintelligence.stanford.edu/blogs/codemonkeys/) | High-performing SWE-bench systems can be expensive, and public reports increasingly publish cost and full trajectories. | HarnessForge should require cost and trace evidence before claiming an effectiveness or economics win. |
| [Codex non-interactive JSONL docs](https://developers.openai.com/codex/noninteractive) | `codex exec --json` emits event streams with completed-turn usage buckets such as input, cached input, output, and reasoning output tokens. | Use Codex JSONL as the first native trace source because it can be captured locally without adopting a separate observability platform. |
| [Claude Code monitoring docs](https://code.claude.com/docs/en/monitoring-usage) | Claude Code can export OpenTelemetry metrics, logs, and traces for usage, cost, tool activity, LLM request spans, cache-read tokens, cache-creation tokens, output tokens, tool spans, and tool result tokens. | Use Claude Code OpenTelemetry as the second trace source when cache read/write buckets and tool spans must be separated more precisely. |
| [Promptfoo Codex SDK provider docs](https://www.promptfoo.dev/docs/providers/openai-codex-sdk/) | Promptfoo can evaluate Codex SDK coding-agent runs with token usage, session identifiers, shell commands, file changes, MCP calls, search/file steps, and assertions. | Treat Promptfoo as a candidate repeatable eval runner after the native Codex JSONL parser proves the record shape. |
| [Langfuse token and cost tracking docs](https://langfuse.com/docs/observability/features/token-and-cost-tracking), [Phoenix docs](https://github.com/Arize-ai/phoenix/blob/main/docs/phoenix/skill.md), and [OpenLLMetry](https://github.com/traceloop/openllmetry) | Current open observability projects can store or export LLM traces, token/cost usage, OpenTelemetry data, tool calls, and agent steps. | Use these as optional storage, dashboard, or OpenTelemetry plumbing after native traces exist; do not make them the source of truth by themselves. |
| [LiteLLM cost tracking docs](https://docs.litellm.ai/docs/proxy/cost_tracking) and [Helicone cost tracking docs](https://docs.helicone.ai/guides/cookbooks/cost-tracking) | Proxy or gateway tools can track model request tokens, cost, sessions, call IDs, and caching behavior. | Use a proxy only when agent traffic can be safely routed through it. Proxy totals are insufficient alone because they miss local file reads, searches, command retries, verification runs, and quality outcomes. |

## HarnessForge Static Field Evidence

This is static token-proxy evidence, not real provider tokenization and not a
model run. Approximate tokens use `chars / 4` only to make sizes comparable.

Command:

```bash
PYTHONPATH=src:. python3 - <<'PY'
# Generated each offline public-repo fixture with create_harness()
# and counted generated harness text by profile.
PY
```

Results from 14 offline public-repo fixtures:

| Profile | Definition | Median chars | Approx median tokens | Median lines |
| --- | --- | ---: | ---: | ---: |
| Minimal entrypoints | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot router | 7,232 | 1,808 | 172 |
| Moderate startup core | Entry points plus current state, feature list, harness README, authoritative facts, component inventory, verification matrix, sensor registry | 28,562 | 7,140 | 607 |
| Comprehensive generated text | All generated text and JSON harness artifacts in the fixture target, excluding project source files | 134,172 | 33,543 | 2,717 |

Interpretation:

- Default generated storage is large enough that loading every harness file into
  every task context would be wasteful.
- Root startup entrypoints are much smaller than the full generated harness,
  which supports the current router design.
- The measurement does not include real model tokenization, cache behavior,
  tool-call savings, retry reduction, verification success, or quality changes.

Existing real large-public-repo field evidence covers Kubernetes, VS Code, and
Bazel discovery and nested-scope ranking. It does not include before/after task
traces, provider-reported token usage, or controlled minimal/moderate/full
harness comparisons.

## Initial Live Trace Smoke

The first live Codex JSONL smoke record is stored at
`docs/harness/evidence/token-economics/codex-jsonl-smoke-2026-06-16.json`.
It used `codex exec --json --ephemeral --sandbox read-only` to read
`AGENTS.md` and this research note, then normalized the trace with
`scripts/normalize_token_trace.py --source codex-jsonl`.

Observed smoke metrics:

- token source: `agent_usage_report`;
- startup input: `40,348`;
- cached input: `19,200`;
- output: `1,034`;
- reasoning output: `815`;
- total visible tokens: `42,197`;
- trajectory: one turn, two command tool calls, two file reads, zero searches,
  zero edits, and zero verification runs.

This smoke record proves the capture and normalization path only. It is
`inconclusive` and must not be used to decide whether minimal, moderate, or
comprehensive harness profiles increase or decrease total task cost.

## Rejected Profile Comparison Attempt

An attempted two-repeat minimal/moderate/comprehensive orientation comparison
was rejected on 2026-06-16. Local `codex exec --ignore-user-config` still
loaded a user-level orientation skill outside the target in some runs, which
added non-target context to the trace. The raw JSONL also contains local
working-directory output from `pwd`, so it remains ignored under
`.harnessforge/` and is not committed.

No profile comparison records were promoted from that attempt. The next
controlled comparison needs a clean runner that prevents user-level skills,
plugins, hooks, memory, or other non-target startup context from entering the
trace, or it needs to record those surfaces explicitly as the harness under
test.

## Initial Clean Profile Comparison

The first clean minimal/moderate/comprehensive comparison used scratch `HOME`
and `CODEX_HOME`, symlinked auth only, `--ignore-user-config`,
`--ignore-rules`, disabled hooks/plugins/memories/apps/multi-agent features,
read-only sandboxing, and ignored scratch target roots. Raw JSONL traces remain
ignored under `.harnessforge/`; only normalized metric records are committed.

Task: read the repo instructions and the fewest needed files, do not edit, do
not run tests, and answer with the project verification command plus current
next step.

| Profile | Repeat | Loaded harness chars | Input | Cached input | Output | Reasoning output | Total | Tool calls | File reads |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| minimal | 1 | 755 | 24,458 | 14,080 | 224 | 46 | 24,728 | 2 | 1 |
| minimal | 2 | 755 | 24,770 | 4,864 | 360 | 90 | 25,220 | 3 | 2 |
| moderate | 1 | 7,617 | 28,449 | 15,104 | 408 | 48 | 28,905 | 4 | 3 |
| moderate | 2 | 7,617 | 27,172 | 15,104 | 427 | 130 | 27,729 | 3 | 2 |
| comprehensive | 1 | 7,617 | 27,334 | 15,616 | 342 | 58 | 27,734 | 3 | 2 |
| comprehensive | 2 | 7,617 | 27,349 | 15,616 | 412 | 122 | 27,883 | 3 | 2 |

Initial interpretation:

- The full generated harness storage size did not determine task tokens. The
  comprehensive profile stored far more files than moderate, but the agent
  loaded the same startup/state files for this orientation task.
- Minimal used fewer loaded harness chars but did not always produce the lowest
  total visible tokens because cache state, tool trajectory, and model behavior
  varied across repeats.
- Moderate and comprehensive were close on this task because both routed to
  `current-state.md` and `feature_list.json`.
- The evidence supports the router hypothesis for this narrow task: actual
  loaded context matters more than total generated artifact size.

This comparison remains `inconclusive` for product behavior. It is a
read-only, non-held-out orientation task and does not measure edits,
verification loops, retries, implementation quality, or worst-case failure
cost.

## Initial Implementation Repair Comparison

A second clean comparison used the same isolated Codex runner on a tiny Python
repair task. Each profile started with `demo.py` returning `41` while
`tests/test_demo.py` expected `42`. The task asked the agent to make the
smallest code change and run `python3 -m unittest discover -s tests`.

| Profile | Loaded harness chars | Input | Cached input | Output | Reasoning output | Total | Tool calls | File reads | Edits | Verification runs | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| minimal | 755 | 81,081 | 57,088 | 958 | 79 | 82,118 | 11 | 5 | 1 | 2 | passed |
| moderate | 7,617 | 73,912 | 59,776 | 918 | 41 | 74,871 | 9 | 5 | 1 | 2 | passed |
| comprehensive | 7,617 | 73,970 | 59,776 | 892 | 0 | 74,862 | 9 | 5 | 1 | 2 | passed |

Initial interpretation:

- All three profiles completed the repair, changed only `demo.py`, and passed
  the target unittest.
- On this task, minimal used more visible tokens and more tool calls than
  moderate or comprehensive. The extra cost came from trajectory, not from
  stored harness size alone.
- Moderate and comprehensive were effectively identical because the agent
  loaded the same startup/state files and did not need deeper harness docs.

This comparison is still too small to close the backlog item. It strengthens
the evidence that token economics depend on loaded context, cache behavior,
and execution trajectory, not merely on how many harness files exist.

## Representative Duration Override Repair Batch

A third clean comparison used ignored scratch copies of committed HarnessForge
and seeded one failing token-economics test. The task asked the agent to add
support for `metadata["trajectoryOverrides"]["durationSeconds"]` in the Codex
JSONL normalizer, preserve the public metric schema, avoid docs edits, and run
`PYTHONPATH=src:. python3 -m unittest tests.test_token_economics`.

The runner used per-run scratch `HOME` and `CODEX_HOME`, symlinked auth only,
`--ignore-user-config`, `--ignore-rules`, disabled hooks/plugins/memories/apps
and multi-agent features, and workspace-write sandboxing. Raw JSONL remains
ignored under `.harnessforge/`; the committed records are normalized.

Summary:

| Profile | Repeats | Loaded harness chars | Total visible tokens | Median total | Cached input range | Median duration seconds | Tool calls | File reads | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| minimal | 3 | 665 | 122,994-273,545 | 205,636 | 101,504-240,512 | 63.556 | 11-22 | 6-11 | 3/3 passed |
| moderate | 3 | 97,613 | 179,644-271,005 | 189,703 | 136,832-234,368 | 52.698 | 15-18 | 7 | 3/3 passed |
| comprehensive | 3 | 97,613-106,552 | 220,259-312,041 | 245,872 | 164,864-246,016 | 62.161 | 12-19 | 7-10 | 3/3 passed |

Initial interpretation:

- All nine runs changed only
  `src/harnessforge/evidence/token_economics.py` and passed the focused test
  module.
- This task finally exercised a larger loaded-context difference. Minimal
  loaded only the short root instruction file; moderate and comprehensive
  commonly loaded `current-state.md` and `feature_list.json`, producing about
  `98K` loaded harness chars before source repair.
- Moderate had the lowest median total tokens and lowest median duration.
  Minimal had the smallest loaded harness context, but not the lowest median
  total, because its trajectories used more tool calls and file reads.
- Comprehensive had the highest median total on this batch. The extra stored
  harness did not improve quality for this explicit source-level repair, and
  one run loaded the metric schema in addition to state files.
- The result is mixed, not a universal win or loss. It supports the mechanism
  claim that loaded context and trajectory dominate stored harness size.

This batch also added a narrow normalizer path for externally measured wall
clock duration: metadata sidecars may provide
`trajectoryOverrides.durationSeconds`, which is copied into
`trajectory.durationSeconds` and omitted from the public record. Codex JSONL
did not emit native duration or timestamp fields in these runs.

## Unrevealed Failure Repair Batch

A fourth clean comparison used the same HarnessForge-derived scratch profile
shape, but seeded source regressions rather than naming the target behavior in
the prompt. The initial focused test failed twice: `file_change` no longer
counted as an edit call, and duration override metadata no longer reached the
normalized trajectory. The prompt only asked the agent to run
`PYTHONPATH=src:. python3 -m unittest tests.test_token_economics`, inspect the
failure, make the smallest source-only fix, and rerun the same check.

Summary:

| Profile | Repeats | Loaded harness chars | Total visible tokens | Median total | Cached input range | Median duration seconds | Tool calls | File reads | Verification runs | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| minimal | 3 | 678 | 147,222-215,544 | 163,183 | 110,208-175,872 | 39.542 | 12-16 | 6-7 | 2-3 | 3/3 passed |
| moderate | 3 | 100,916 | 191,253-268,619 | 204,213 | 156,800-232,960 | 38.169 | 12-13 | 6-7 | 2 | 3/3 passed |
| comprehensive | 3 | 100,916 | 227,923-244,078 | 241,409 | 169,984-189,824 | 41.097 | 13-15 | 7 | 2 | 3/3 passed |

Initial interpretation:

- All nine runs changed only
  `src/harnessforge/evidence/token_economics.py` and passed the focused test
  module after observing the seeded failure.
- Minimal had the lowest median visible tokens on this unrevealed-failure
  batch. It loaded far less harness context and still completed the repair.
- Moderate and comprehensive loaded the same large state surface and cost more
  without improving final quality for this focused source repair.
- The result contrasts with the explicit duration-override batch, where
  moderate had the lowest median. This supports a mixed conclusion: the token
  effect depends on task framing, loaded context, and trajectory, not on the
  stored profile label alone.

This is stronger than the explicit-repair batch because the prompt did not name
the source defects, but it is still not true external held-out evidence. The
regression was seeded in ignored scratch copies of this repository.

## External pytm Repair Batch

A fifth clean comparison used ignored scratch copies of the public OWASP pytm
repository at commit `e452aaf`. The source regression removed response-linking
from `pytm.flows` helper-created reply flows. The prompt did not name the
missing line; it asked the agent to run
`python -m pytest -q tests/test_flows_helpers.py`, inspect the failure, make a
smallest source-only fix, and rerun the same command.

The runner used the same isolated Codex setup as the prior repair batches:
per-run scratch `HOME` and `CODEX_HOME`, symlinked auth only,
`--ignore-user-config`, `--ignore-rules`, disabled
hooks/plugins/memories/apps and multi-agent features, workspace-write
sandboxing, and an external scratch virtual environment on `PATH`. Raw JSONL
remains ignored under `.harnessforge/`; the committed records are normalized.

Summary:

| Profile | Repeats | Loaded harness chars | Total visible tokens | Median total | Cached input range | Median duration seconds | Tool calls | File reads | Verification runs | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| minimal | 3 | 378 | 95,931-114,985 | 110,924 | 60,544-94,336 | 37.801 | 10-13 | 7 | 2 | 3/3 passed |
| moderate | 3 | 2,061 | 112,523-184,723 | 133,320 | 93,312-148,224 | 39.238 | 11-21 | 6-11 | 2 | 3/3 passed |
| comprehensive | 3 | 3,901 | 136,214-140,606 | 138,835 | 100,992-117,888 | 44.365 | 14-17 | 9-12 | 2 | 3/3 passed |

Human quality review:

- raw `file_change` events were limited to `pytm/flows.py`;
- all nine scratch targets passed `python -m pytest -q tests/test_flows_helpers.py`
  after repair;
- no tests, docs, packaging, or harness files were edited by the agent runs;
- repair shapes varied slightly but preserved the public helper API and restored
  bidirectional response-link behavior.

Initial interpretation:

- Minimal had the lowest median visible tokens and duration on this external
  seeded repair. It also loaded the fewest harness chars.
- Moderate had one long trajectory, which widened its total-token range and
  raised its median above minimal.
- Comprehensive loaded the most harness guidance and had the highest median
  total and duration without improving final quality for this focused helper
  repair.
- This is the first external-real-repo repair evidence in the ledger. It still
  does not close the backlog item by itself because the defect was seeded, not
  a true held-out issue, and the task used a small Python package rather than a
  broader multi-repo matrix.

## External Bluepeak React Repair Batch

A sixth clean comparison used ignored scratch copies of the public Bluepeak-AI
frontend at commit `8049dd4`. The source regression forced the `TrustBadge`
disclosure button to report `aria-expanded="false"` even after opening. The
prompt did not name the source line; it asked the agent to run
`npm test -- --run react/tests/trust-ui.test.tsx`, inspect the failure, make a
smallest source-only TypeScript/React fix, and rerun the same command.

The runner used the same isolated Codex setup as the prior repair batches:
per-run scratch `HOME` and `CODEX_HOME`, symlinked auth only,
`--ignore-user-config`, `--ignore-rules`, disabled
hooks/plugins/memories/apps and multi-agent features, workspace-write
sandboxing, and a prepared local `node_modules` symlink inside ignored scratch
space. Raw JSONL remains ignored under `.harnessforge/`; the committed records
are normalized.

Summary:

| Profile | Repeats | Loaded harness chars | Total visible tokens | Median total | Cached input range | Median duration seconds | Tool calls | File reads | Verification runs | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| minimal | 3 | 434 | 269,155-378,017 | 352,355 | 226,816-286,976 | 76.572 | 19-26 | 6-11 | 4-6 | 3/3 passed |
| moderate | 3 | 2,164 | 304,734-353,176 | 306,817 | 209,792-291,968 | 67.195 | 16-23 | 6-12 | 5-6 | 3/3 passed |
| comprehensive | 3 | 4,079 | 260,553-464,436 | 313,196 | 221,184-396,416 | 84.365 | 16-33 | 8-15 | 4-10 | 3/3 passed |

Human quality review:

- raw `file_change` events were limited to
  `react/src/components/TrustBadge.tsx`;
- all nine scratch targets passed
  `npm test -- --run react/tests/trust-ui.test.tsx` after repair;
- no tests, docs, package metadata, lockfiles, or harness files were edited by
  the agent runs;
- final component files matched the upstream clean component, preserving the
  public component API and accessible disclosure behavior.

Initial interpretation:

- Minimal loaded the fewest harness chars but had the highest median visible
  tokens. Its trajectories included more tool calls than moderate on this
  focused UI repair.
- Moderate had the lowest median total and duration in this React/TypeScript
  batch.
- Comprehensive had one very long trajectory, which widened the range and
  raised its median above moderate. It did not improve final quality for this
  focused UI repair.
- This second external ecosystem strengthens the mixed conclusion. Token cost
  followed trajectory and task framing more than profile label or stored
  harness size alone.

This batch also expanded the Codex JSONL normalizer's verification-command
recognition for JavaScript/TypeScript checks such as `npm test`, `vitest`,
`pnpm test`, `yarn test`, `node --test`, and `playwright test`.

## Required Trace Evidence Still Missing

The accepted backlog item is not complete until HarnessForge has representative
task traces or controlled evaluations that compare:

- minimal, moderate, and comprehensive harness profiles on the same tasks;
- startup input, cache writes, cache reads, uncached repeated input, and output;
- tool calls, file reads, search calls, edit calls, retries, and verification
  runs;
- completion quality, verification success, and worst-case failure cost;
- cold-start cost, repeated-session savings, rework savings, and instruction
  bloat failures.

Still missing after the external pytm and Bluepeak batches: true held-out tasks,
larger-repo coverage such as a large public checkout, and a second telemetry
source such as Claude Code OpenTelemetry for cache-creation and tool-span
buckets.

## Evidence Path

Use native agent telemetry as the evidence source, then normalize it into
`harnessforge.tokenEconomicsMetric.v1`. Observability platforms can help store,
query, or visualize traces, but they do not replace controlled repeated task
runs.

Evidence-source order:

1. Capture `codex exec --json` for the first spike. Use
   `scripts/normalize_token_trace.py --source codex-jsonl` to parse
   completed-turn token usage and event/item streams into one
   token-economics record.
2. Add Claude Code OpenTelemetry when the evaluation needs separate cache-read,
   cache-creation, LLM request, tool, and tool-result token spans.
3. Consider Promptfoo around Codex SDK runs when HarnessForge needs a repeatable
   task matrix with assertions, session IDs, file changes, shell commands, MCP
   calls, and token usage.
4. Consider Langfuse, Phoenix/OpenInference, or OpenLLMetry only as optional
   storage, dashboard, or OpenTelemetry plumbing after native traces are
   captured.
5. Consider LiteLLM or Helicone only for provider-agnostic API request, cost,
   session, call ID, or cache evidence. They are not enough by themselves
   because they do not observe local repo reads, command execution, retries,
   verification, or human quality review.
6. Treat SWE-agent trajectories and similar agent-run formats as baseline or
   schema inspiration, not the default HarnessForge runner.

Controlled-run rules:

- Freeze the target repo commit, task text, agent version, model, sandbox,
  network setting, environment variables, and verification command for every
  profile comparison.
- Run each task in an isolated copy or worktree. Do not let one profile's edits,
  caches, or generated artifacts leak into another profile.
- Compare minimal, moderate, and comprehensive harness profiles as available
  startup and repository guidance, then record the harness files actually loaded
  by the agent. Do not assume the comprehensive profile means every durable doc
  entered the prompt.
- Start with one repository, two representative tasks, three profiles, and two
  repeats before expanding to the larger 3-5 task, multi-repo matrix.
- Keep raw traces ignored and local until reviewed. Commit only redacted,
  target-relative normalized records or summaries that avoid private code,
  secrets, local absolute paths, and long command output.
- Keep provider-reported tokens, agent-reported tokens, tokenizer estimates,
  character proxies, and estimated cost in separate fields. Do not compare
  them as if they are the same measurement.
- Require a do-no-harm quality floor before accepting a token or latency
  reduction as an improvement.

## Metric Schema

Use [token-economics-metric.schema.json](token-economics-metric.schema.json)
for future evaluation records. The schema is intentionally a record format, not
an eval runner. It can be stored beside effectiveness evidence or referenced
from a future `effectiveness*.json` report.

Minimum useful record:

- exact target, task, agent, model, and harness profile;
- harness mechanism under test and expected effect;
- static and dynamic context sizes;
- provider-reported token buckets when available;
- cache read/write buckets when available;
- reasoning output tokens when the trace source exposes them;
- token source, because char proxies and provider counts are not comparable;
- tool, retry, turn, latency, and verification outcomes;
- quality floor and evidence references;
- limitations and whether the run is promoted, deferred, or rejected.

## Recommendation

Until trace evidence exists:

- keep generated root entrypoints short and route to detail instead of copying
  all detail into startup context;
- keep stable, reusable instructions separate from dynamic task state;
- place dynamic state in explicit current-state or task artifacts that agents
  load only when relevant;
- prefer compact summaries and selected context over full-context loading for
  repeated work;
- report context-budget and instruction-quality signals as advisory until
  representative traces prove a product change;
- require any future generated lazy-loading or summarization behavior to pass a
  do-no-harm quality floor and show reduced total cost or retries on held-out
  tasks.

## Next Measurement Slice

Run a small controlled evaluation before closing this backlog item:

1. Add a true held-out task where the expected source fix is not seeded by this
   repo's evaluator, or run a larger public-repo checkout task that exercises
   broader discovery and routing.
2. Expand to 3-5 tasks across a small Python package, a frontend TypeScript
   app, and one large public repo checkout only after the external-repair
   redaction path stays clean.
3. Capture provider or agent token usage, cache buckets when available, tool
   calls, retries, verification result, elapsed time, and human quality review.
4. Add Claude Code OpenTelemetry only when the Codex JSONL record is
   insufficient for cache-creation or tool-span buckets.
5. Conclude net increase, net decrease, mixed, or insufficient evidence only
   after reviewing the normalized trace records.
