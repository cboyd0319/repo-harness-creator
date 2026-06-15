# Reference Mining Notes

Reviewed: 2026-06-15 UTC.

This note records ideas mined from local sibling repositories and current open
source projects that are closer to HarnessForge's job: creating, assessing, and
maintaining repo-local harness surfaces. It is not generated into target
repositories.

## Local Repo Ideas

Reviewed local references:

- `awman`
- `aspec`
- `maki`

Accepted for HarnessForge in this pass:

- Generic structured-spec detection. When a target repo already has
  architecture, security, operations, UX, requirements, or work-item docs,
  generated context should treat those docs as possible planning or
  source-of-truth surfaces.
- Project task-runner detection. When a target repo has a `justfile`,
  HarnessForge should prefer a declared aggregate target such as `just ci`
  before inventing lower-level commands.
- Architecture-check routing. When a repo exposes an architecture lint target
  or script, generated verification should surface it without duplicating the
  same check through both a task runner and a raw script.
- Generated-doc drift awareness. Repos with doc-generation or docs-check
  targets should get generated context that treats generated docs as code-owned
  artifacts.

Explicit non-goals:

- Do not make any local sibling repo format a HarnessForge requirement.
- Do not generate local sibling repo instructions or personal tool mandates.
- Do not require one specific spec directory name, workflow language, task
  runner, agent platform, or tool registry.

## Public Harness References

Sources reviewed:

- `jcaiagent7143-ui/harnessforge`:
  https://github.com/jcaiagent7143-ui/harnessforge
- `jcaiagent7143-ui/harnessforge` verify protocol:
  https://github.com/jcaiagent7143-ui/harnessforge/blob/main/docs/reference/verify-protocol.md
- `jcaiagent7143-ui/harnessforge` benchmarks:
  https://github.com/jcaiagent7143-ui/harnessforge/blob/main/BENCHMARKS.md
- `walkinglabs/learn-harness-engineering`:
  https://github.com/walkinglabs/learn-harness-engineering
- `ffy6511/harness-creator-skill`:
  https://github.com/ffy6511/harness-creator-skill
- `HKUDS/OpenHarness`:
  https://github.com/HKUDS/OpenHarness
- `ai-boost/awesome-harness-engineering`:
  https://github.com/ai-boost/awesome-harness-engineering
- OpenAI harness engineering:
  https://openai.com/index/harness-engineering/
- Martin Fowler harness engineering for coding agent users:
  https://martinfowler.com/articles/harness-engineering.html
- Addy Osmani agent harness engineering:
  https://addyosmani.com/blog/agent-harness-engineering/
- Augment Code harness engineering guide:
  https://www.augmentcode.com/guides/harness-engineering-ai-coding-agents

Accepted for HarnessForge in this pass:

- Add a read-only `harnessforge inspect` command so users and agents can see
  the detected profile before `init` writes files.
- Provide a stable JSON inspection shape for future tool and CI integration.
- Keep `init --dry-run` for generated-file previews, but separate it from
  detection preview because those answer different user questions.
- Treat root Python packages with docs sites as Python projects, not docs-only
  repos, so verification routing keeps package checks visible.
- Keep root instruction files as short maps to repository-owned source material
  rather than making them encyclopedias.

High-value ideas to consider next:

- Remaining ideas research is ranked in
  `docs/harness/remaining-ideas-research.md`.
- Existing-repository mode. If a repo already has a coherent control plane
  such as specs, docs decisions, issue queues, or custom readiness scripts,
  HarnessForge should improve that surface instead of adding a competing state
  system.
- Greenfield mode. Empty or very small repos may benefit from a lighter
  first-run path that asks for project type, verification preference, platform
  contract, and agent surfaces before writing the full harness.
- Blueprint mode as an explicit opt-in. Domain-specific skill bundles and
  validators can help, but they should not become the default generated
  surface for arbitrary repos.
- Stable machine-readable verification. The current `audit --json` is useful
  for harness quality; a future project-check contract could expose checks,
  statuses, durations, and actionable failure messages for agents to consume.
- `sync --check` style drift detection. The current `update --drift-report`
  covers generated-file drift; a shorter CI-oriented alias could improve
  discoverability.
- First-run UX. A `quickstart` or `wizard` command could explain what will be
  generated, which existing files will be preserved, and which decisions need
  project review.
- Measured real-agent evaluations. Public claims should eventually come from
  repeatable A/B tasks against pinned repos, with caveats, workspaces, and
  reproduction commands.
- Local instruction adapters. Cursor, Windsurf, Continue, and Aider support
  may be useful, but only after their current loading rules are verified from
  primary docs and the generated/local boundary is explicit.

Ideas to defer unless a target repo opts in:

- MCP server configuration, browser credentials, memory schemas, and
  agent-platform permission files.
- Domain blueprints such as finance, RAG, customer support, or workflow
  automation.
- Large generated `SKILLS/` trees.
- LLM-assisted init-time profile refinement.
- Overwriting or replacing coherent existing repo-local spec systems.
