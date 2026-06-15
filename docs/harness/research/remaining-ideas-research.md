# Remaining Ideas Research

Reviewed: 2026-06-15 UTC.

This repo-local note records the compact outcome of the remaining-ideas mining
pass. It is not generated into target repositories. The full prior research
detail remains in git history; keep this file current-state only.

Scope reviewed: local AWMAN, ASPEC, Maki, public HarnessForge-like projects,
OpenAI, Martin Fowler, LangChain, OpenHarness, Walking Labs, spec-driven
development sources, harness-engineering papers, Bluepeak-AI harness docs,
JobSentinel harness docs, and root `AGENTS.md` files where present. No AGY
review was used for the manual pass.

## Product Conclusion

The best default-generator ideas are already implemented or routed into the
roadmap. The remaining value is not more default files; it is clearer product
modes, better read-only analysis, quality gates, and opt-in owner workflows.

Current release boundary:

- Normal `init` should stay portable, review-required, zero-install, and
  target-owned after generation.
- Richer behavior belongs in explicit commands such as `inspect`, `sync`,
  `report`, `enhance`, `plan`, `session`, `index`, `effectiveness`, and
  `blueprint`.
- Generated target repos must not receive local HarnessForge preferences,
  copied sibling-repo formats, autonomous repair workflows, product-local
  research allowlists, or structural-score performance claims.

## Accepted Ideas

| Idea | Status | Boundary |
| --- | --- | --- |
| Readiness reporting | Implemented through `inspect`, `sync`, and `report` | Read-only; no target command execution |
| Project verification contract | Implemented through `verify --json` and explicit `--run` | Plan-only by default |
| Existing spec/source-of-truth routing | Implemented in detection, readiness, audit, and generated instructions | Detect and route; do not install Spec Kit or ASPEC |
| Work-item and workflow awareness | Implemented as readiness/governance inventory | Report surfaces; do not become a workflow runtime |
| Context budget and duplicate instruction signals | Implemented as readiness/report signals | Advisory until thresholds are proven on real repos |
| Permission/governance inventory | Implemented | Security review surface, not generated platform config |
| Blueprint mode | Implemented as explicit opt-in | Review-required artifacts separate from default `init` |
| Session snapshot | Implemented as `harnessforge session` | Read-only; no writes or target checks |
| Diff-aware verification planner | Implemented as `harnessforge plan` | Read-only; execution stays in `verify --run` |
| Structural repo index | Implemented as `harnessforge index` | No network service, embeddings, or private summaries by default |
| Effectiveness evidence assessment | Implemented as `harnessforge effectiveness` | Reviews stored evidence; does not run benchmarks |
| Source-record schema | Implemented as generated schema/example | Project-owned records only |
| First-agent harness improvement task | Implemented | Review-oriented; no project command execution by default |

## Still Worth Considering

These remain useful but should stay behind explicit roadmap/release decisions:

- SBOM-aware indexing and optional SBOM adapters when dependency inventory
  improves generated quality.
- Better instruction-quality and signal-to-noise reporting beyond current size
  and duplicate checks.
- More real-repo golden fixtures built from popular public open-source repos.
- Harness maturity levels backed by evidence, not marketing scores.
- Expanded policy presets with clear owner opt-in.
- Better interactive quickstart/init UX.
- Action summary polish and release evidence automation.

Track accepted work in `docs/roadmap.md`; do not duplicate full backlog state
here.

## Rejected Defaults

Do not add these to normal generated harness output:

- Large skill or memory trees, MCP config, browser credentials, or platform
  permission files.
- LLM-assisted init-time refinement by default.
- Copied ASPEC, AWMAN, Maki, or public HarnessForge templates.
- Autonomous setup, teardown, self-heal, push, or PR workflows.
- Spec Kit installation, `.specify`, slash commands, presets, extensions,
  catalogs, or workflow engines.
- Structural audit scores presented as real-agent effectiveness.
- Silent fallback from a requested platform/runtime contract to a weaker one.
- Overwrites of coherent existing spec, workflow, or instruction systems.

## Next Use

Use this file only as a research outcome summary. For implementation order,
status, and release decisions, use `docs/roadmap.md` and `current-state.md`.
