# Harness Engineering Foundations

Reviewed: 2026-06-24 UTC.

This note records the harness-engineering theory HarnessForge implements and how
the product contract maps onto it. It exists so the five-core model, the seven
audit buckets, and the maturity/effectiveness boundaries trace back to a single
reviewed source basis instead of being re-derived per session.

It is repo-local product evidence and is not generated into target repositories.

## Source Basis

Primary synthesis source:

- Walking Labs, "Learn Harness Engineering" course and `harness-creator` skill,
  `https://github.com/walkinglabs/learn-harness-engineering`. The course
  synthesizes the three primary articles below into 12 lectures, 6 projects, a
  template pack, and an advanced repo pack. The `harness-creator` skill is the
  direct conceptual ancestor of HarnessForge.

Backbone articles the course builds on (already tracked in `sources.md`):

- OpenAI, "Harness engineering: leveraging Codex in an agent-first world" —
  repo-as-spec, mechanical guardrails, agent-oriented error messages, cleanup.
- Anthropic, "Effective harnesses for long-running agents" — initializer agent,
  feature list, progress log, handoff across context windows.
- Anthropic, "Harness design for long-running application development" —
  planner/generator/evaluator roles, context resets, harness simplification.

Epistemic note: the course cites several 2026-dated vendor articles. Treat those
dates and figures as the course's own curation, not independently verified here.
Quantitative claims (for example role-separation quality lift) are reported as
the course's stated results, used as mechanism rationale rather than proof.

## Two Five-Subsystem Framings

The literature uses two different "five subsystem" framings. Conflating them is
a common source of confusion.

- Academic framing (course Lecture 02): instructions, tools, environment,
  state, feedback.
- Operational framing (`harness-creator` skill, and HarnessForge's product
  contract): instructions, state, verification, scope, lifecycle.

HarnessForge keeps the operational framing as its core contract and treats the
academic framing's extra buckets as support surfaces. The audit scores seven
implementation buckets for diagnostic granularity, then reports how each maps to
the core model.

## Seven Audit Buckets Mapped To Five Core Subsystems

| Audit bucket | Role | Core subsystem |
| --- | --- | --- |
| `instructions` | core | instructions |
| `state` | core | state |
| `feedback` | core | verification |
| `scope` | core | scope |
| `lifecycle` | core | lifecycle |
| `tools` | support surface | none (serves the core) |
| `environment` | support surface | none (serves the core) |

The `feedback` bucket is the implementation form of the `verification` core
subsystem. `tools` and `environment` are support surfaces: they make the core
subsystems easier to follow, verify, or maintain, but they are not peer core
subsystems. `harnessforge audit` now emits this mapping in both JSON
(`coreModel`, per-domain `coreSubsystem`/`surfaceClass`) and the formatted
output (for example `feedback [verification core]`). `src/harnessforge/
assessment/audit.py` owns the mapping (`DOMAIN_CORE_SUBSYSTEM`).

## Maturity Ladder

The course frames harness depth as a ladder, not a single target:

- Minimal pack: `AGENTS.md` (or `CLAUDE.md`), `feature_list.json`, a progress
  artifact, and `init.sh`. The course states these four are enough to make most
  agent workflows noticeably more stable.
- Advanced pack (OpenAI-style): short routing `AGENTS.md` plus durable
  system-of-record docs, layered domain architecture with mechanically enforced
  boundaries, active and completed execution plans, product/reliability/security
  policy files, and quality scoring by domain and layer.

A repo should sit at the rung its size and lifespan justify. A small, short-lived
repo that is correctly minimal is not deficient; the advanced pack is for
multi-domain, long-running systems.

## Boundaries This Note Locks In

- A higher audit score is not automatically better. Lecture 12 makes
  simplification a first-class goal: as models improve, remove harness
  components that no longer earn their keep. HarnessForge already reflects this
  through harness maturity levels and the simplification framing; the audit
  score is structural conformance, not a maximization target.
- Structure is not effectiveness. The course accepts only ablation (remove one
  subsystem and measure the drop), failure attribution, and benchmark snapshots
  as evidence of harness value, never structural presence. HarnessForge routes
  real-agent claims through the effectiveness evidence contract, and the audit
  score is explicitly a harness-health signal only.
- Ablation finds marginal value, not the bottleneck. Locating the real
  bottleneck still requires failure records and attribution.
- Harness design is model-specific. The course notes models with stronger native
  planning tolerate compaction, while others need context resets, so a "good"
  harness is relative to the target model.

## Non-Structural Dimensions

The jump from a competent harness to an excellent one concentrates in dimensions
a structural audit only partially sees. Each is already represented in
HarnessForge; this note records the lineage and the remaining depth gaps.

| Dimension | Course source | HarnessForge surface |
| --- | --- | --- |
| Evaluator independence (worker is not the checker) | Lectures 09, 11; Project 05 role-separation results | `evaluator-rubric`, effectiveness evidence contract |
| Agent-oriented error messages (what/why/how-to-fix) | Lectures 09, 10 | verification matrix, sensor registry guidance |
| Review feedback promoted to mechanical rules | Lectures 10, 12 | sensor registry, change contract |
| Two-layer observability (runtime + process) | Lecture 11 | observability evidence, report observability signals |
| Golden journeys and end-to-end verification | Lectures 10, 12 | verification matrix, release controls |
| Quality scoring tracked over time | Lecture 12 | quality document |
| Harness simplification log | Lecture 12 | quality document, roadmap simplification framing |

## Applied In This Pass

- `harnessforge audit` reports the seven-to-five mapping in JSON and formatted
  output, resolving the "report both with clear labels" question in the roadmap
  Core Harness Model Course Correction item.
- `docs/harness/README.md` documents the mapping next to the Five Core
  Subsystems table.
- This note is the authoritative source for the lineage and mapping rationale.

Remaining accepted work stays tracked in `docs/roadmap.md` (generated-contract
regression check and generated-template wording alignment), not duplicated here.
