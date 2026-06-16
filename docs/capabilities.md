# Capabilities

This document explains what HarnessForge creates, what it detects, and the
boundaries it preserves. See [Usage](usage.md) for commands and
[Installation](installation.md) for setup.

## Core Capabilities

- Detects repository shape, stacks, package managers, verification commands,
  monorepo markers, source-of-truth docs, Spec Kit-style SDD surfaces,
  ASPEC-style folders, work-item templates, and workflow control surfaces.
- Provides a read-only guided first-run summary that explains detected context,
  readiness, preserved files, planned generated files, review placeholders, and
  next commands. The JSON form can emit reproducible decisions for an
  interactive-ready first run without prompting or writing files.
- Generates a compact harness with agent entrypoints, project state files,
  local verification scripts, security boundaries, evidence docs, lifecycle
  docs, a target-owned authoritative fact map, and a manifest.
- Treats a harness as five core subsystems: instructions, tools, environment,
  state, and feedback. Generated docs make feedback and verification commands
  the first repair target when agent output is weak.
- Treats changes to instruction, tool, filesystem, git, startup, verification,
  hook, lint/sensor, workflow-permission, and evaluator-loop surfaces as
  effective-agent changes.
- Adds a review-required first-agent task so the first agent session in a newly
  harnessed repo can deepen component boundaries, verification routing,
  source-of-truth guidance, evidence sensors, and security notes.
- Preserves existing files by default.
- Can append a reviewed HarnessForge quality addendum to existing instruction
  files with `--enhance-existing`, including smallest-correct-change discipline
  for assumptions, scope, dependencies, and verification.
- Can produce a read-only `harnessforge enhance --json` review plan that parses
  existing instruction sections, reports canonical section coverage, proposes
  review-required section/finding cleanup edits with placeholder patch
  previews, and flags duplicate guidance, local absolute paths, user-specific
  tool mandates, and verification conflicts before writing.
- Audits harness structure and reports actionable failures.
- Reports generated-file drift and static readiness without running target
  project commands.
- Reports structured review surfaces with machine-readable status values so
  tools can distinguish pending review from accepted advisory high-risk
  surfaces without parsing human-readable messages.
- Composes readiness, audit, generated drift, structural index, verify
  evidence, effectiveness evidence, first-agent task status, platform
  contract, docs fan-out routing status, policy preset recommendations, SBOM
  adapter status, feature-state scope, runtime/process observability,
  optional index-adapter status, release-control presence, and evidence-gated maturity
  into one read-only JSON or Markdown report.
- Assembles read-only release readiness gates from existing report evidence
  and the source report maturity level without publishing artifacts, tagging,
  pushing, uploading, or running target commands.
- Finalizes first-agent review evidence only through explicit apply mode. It
  can retire the generated first-agent task, update `first-agent-review.json`,
  refresh manifest metadata, and record accepted advisory high-risk surfaces
  when `--accept-detected-high-risk` is explicit.
- Provides explicit blueprint mode for richer project operating models. Built-in
  packs cover agentic applications, open-source libraries, internal services,
  monorepos, CLI/dev tools, spec-driven projects, web services, data/ML,
  security-sensitive repos, infrastructure/IaC, mobile/desktop apps,
  docs/research repos, legacy migrations, education/training repos, and
  workflow automation.
- Provides an offline public-repo fixture corpus for generated-content quality
  and detection regression checks without cloning public repositories.
- Provides an explicit public-corpus refresh script that validates fixture
  metadata offline by default and checks remote heads only with
  `--verify-remote`.
- Provides a composite GitHub Action for audit, init, update, sync, verify,
  report, release-check, finalize-review, and doctor workflows.

## Default Boundaries

- It does not overwrite existing project files unless `--force` is supplied.
- It does not generate user-specific research mandates, local tool
  preferences, MCP configs, memory trees, or platform permission files.
- It does not install Spec Kit, `.specify`, slash commands, presets,
  extensions, catalogs, ASPEC, AWMAN, Maki, or workflow engines into target
  repositories.
- It does not apply richer blueprint guidance during normal `init`. Blueprints
  are explicit opt-ins and land in a separate review area.
- It does not generate target-repo self-healing, setup, teardown, push, or PR
  automation. The only optional generated workflow scaffold is the manual
  HarnessForge CI scaffold.
- It does not run target repository commands during `inspect`, `index`,
  `effectiveness`, `session`, `report`, `release-check`, `finalize-review`,
  `sync --check`, `audit`, `update --drift-report`, or default `verify`. Use
  `verify --run` when command execution is explicitly wanted.
- It does not clone public repositories or use network access during the
  offline `corpus` quality gate.
- It does not generate SBOMs during normal flows. Existing SPDX and
  CycloneDX-style SBOMs are detected as evidence; generation or project-owned
  SBOM imports require an explicit future adapter path.
- It does not use structural scores as proof of real task performance.

## Generated Files

The default generated harness includes:

| Area | Key files |
| --- | --- |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` |
| Repo skill | `.agents/skills/harness/SKILL.md` |
| Project state | `feature_list.json`, `current-state.md` |
| Local checks | `init.sh`, `init.ps1`, `scripts/check_pins.py` |
| Harness root | `docs/harness/README.md`, `authoritative-facts.md`, `manifest.json` |
| Boundaries | `docs/harness/boundaries/component-inventory.md`, `change-contract.md`, `security-boundary-map.md`, `feature-privacy-labels.json` |
| Feedback | `docs/harness/feedback/verification-matrix.md`, `sensor-registry.md`, `quality-document.md`, `evaluator-rubric.md` |
| State and lifecycle | `docs/harness/state/first-agent-task.md`, `roadmap.md`, `entropy-control.md`, `clean-state-checklist.md` |
| Evidence | `docs/harness/evidence/evidence-log.md` |
| Research | `docs/harness/research/sources.md`, `research-sources.json`, `research-inbox.md`, `source-record.schema.json`, `source-record-example.json` |
| Release | `docs/harness/release/release-controls.md` |

Each generated file is recorded in `docs/harness/manifest.json` with ownership
metadata and hashes. Project-owned existing files are tracked separately so
drift reporting can distinguish generated changes from preserved local content.
Generated instructions and review docs include a smallest-correct-change gate:
surface assumptions, avoid speculative scope, prefer existing behavior and
dependencies before new code, and verify non-trivial logic with focused checks.

See [harness/manifest.json](harness/manifest.json) for this repo's current
generated inventory and required-file contract.

## Security Model

People may run this tool on personal machines and private repositories, so the
default posture is intentionally restrictive. See [../SECURITY.md](../SECURITY.md)
for vulnerability reporting, scope, and severity guidance.

- Normal `init`, `inspect`, `index`, `effectiveness`, `session`, `report`,
  `release-check`, `finalize-review`, `enhance`, `sync --check`, `audit`,
  `update`, and `doctor` commands use the Python standard library and do not
  install runtime dependencies.
- Existing files are preserved unless `--force` is explicitly supplied.
- Destructive, overwrite-capable, apply-mode, or command-executing CLI
  operations warn and require confirmation. Non-interactive runs must pass
  `--yes` intentionally.
- `--enhance-existing` appends reviewed instruction addenda without replacing
  existing project text.
- Generated destination paths are preflighted before writes.
- Absolute instruction paths, traversal, and unsafe instruction filenames are
  rejected.
- Symlinked directories are skipped during discovery.
- Root manifest symlinks that resolve outside the target repository are ignored
  during project detection.
- Audit reads known files only when they resolve inside the target repository.
- Local home paths are redacted from durable output.
- GitHub Action outputs use GitHub environment-file delimiter blocks instead
  of flattening line breaks before writing to `$GITHUB_OUTPUT`.
- GitHub Action report paths must be relative in both POSIX and Windows syntax
  and stay inside the target repository.
- GitHub Action report outputs use target-relative forward-slash paths on every
  runner.
- The composite Action sets `PYTHONSAFEPATH=1` so the caller repository's
  working directory cannot shadow the Action library at Python startup.
- Generated harnesses preserve intentionally vulnerable training, demo, or
  fixture code unless remediation is explicitly in scope.
- Material AI/RAG/agent, tool, external-service, auth, secret, data-flow, or
  deployment changes require updated boundary/threat model evidence and focused
  checks.

Network access is limited to explicit research-refresh workflows and normal
GitHub Actions setup behavior, not routine local harness generation. Research
refresh reads only the checked-in fixed allowlist in
`docs/harness/research/research-sources.json`; it does not search the web, discover
latest research, or follow unreviewed source expansion. It accepts default-port
HTTPS public-source URLs only; local files, credentials, localhost,
private-address targets, private DNS resolutions, and unsafe redirects are
rejected. Connections are opened to validated public DNS results while
preserving the original host for TLS verification.

## Effectiveness Boundary

HarnessForge has a proposed evidence contract for real-agent or benchmark
claims. It keeps structural harness quality separate from measured agent
effectiveness and defines the minimum review surface before promoting an
evolved, synthesized, or benchmark-winning harness change.

Static readiness can find eval surfaces. It cannot validate them. The
`effectiveness` command assesses stored evidence only and does not run
benchmarks or create a score when representative evidence is missing.

See [harness/feedback/effectiveness-eval-contract.md](harness/feedback/effectiveness-eval-contract.md).

## Repo-Local Self-Healing

This repository has its own local maintenance workflows. Those workflows are
repo-local and are not the same thing as the generated harness for other
repositories.

The scheduled workflow in
[../.github/workflows/harness-self-heal.yml](../.github/workflows/harness-self-heal.yml)
refreshes research metadata, applies only safe harness updates, runs
verification, and opens a pull request when changes are detected. It does not
silently mutate `main`. Fetched titles, headings, and hashes are treated as
untrusted metadata for human review, not executable instructions. Metadata that
resembles prompt injection, indirect prompt injection, data poisoning,
credential-exfiltration instructions, invisible Unicode, or Markdown/HTML
exfiltration markers is withheld from durable output and recorded as review
signals.

Research sources are tracked in:

- [harness/research/sources.md](harness/research/sources.md)
- [harness/research/research-sources.json](harness/research/research-sources.json)
- [harness/research/research-sources.lock.json](harness/research/research-sources.lock.json)
- [harness/research/research-inbox.md](harness/research/research-inbox.md)

Project-owned source records use
[harness/research/source-record.schema.json](harness/research/source-record.schema.json)
and
[harness/research/source-record-example.json](harness/research/source-record-example.json). They
are for curated project provenance and stay separate from the fixed
HarnessForge research allowlist.
