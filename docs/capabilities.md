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
  next commands.
- Generates a compact harness with agent entrypoints, project state files,
  local verification scripts, security boundaries, evidence docs, lifecycle
  docs, and a manifest.
- Adds a review-required first-agent task so the first agent session in a newly
  harnessed repo can deepen component boundaries, verification routing,
  source-of-truth guidance, evidence sensors, and security notes.
- Preserves existing files by default.
- Can append a reviewed HarnessForge quality addendum to existing instruction
  files with `--enhance-existing`.
- Audits harness structure and reports actionable failures.
- Reports generated-file drift and static readiness without running target
  project commands.
- Provides explicit blueprint mode for richer project operating models. Built-in
  packs cover agentic applications, spec-driven projects, web services,
  data/ML, security-sensitive repos, and workflow automation.
- Provides a composite GitHub Action for audit, init, update, sync, verify, and
  doctor workflows.

## Default Boundaries

- It does not overwrite existing project files unless `--force` is supplied.
- It does not generate user-specific research mandates, local tool
  preferences, MCP configs, memory trees, or platform permission files.
- It does not install Spec Kit, `.specify`, slash commands, presets,
  extensions, catalogs, ASPEC, AWMAN, Maki, or workflow engines into target
  repositories.
- It does not apply richer blueprint guidance during normal `init`. Blueprints
  are explicit opt-ins and land in a separate review area.
- It does not create autonomous push, PR, self-heal, setup, or teardown
  workflows unless optional workflow scaffolds are explicitly requested.
- It does not run target repository commands during `inspect`, `sync --check`,
  `audit`, `update --drift-report`, or default `verify`. Use `verify --run`
  when command execution is explicitly wanted.
- It does not use structural scores as proof of real task performance.

## Generated Files

The default generated harness includes:

| Area | Key files |
| --- | --- |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` |
| Project state | `feature_list.json`, `progress.md`, `session-handoff.md` |
| Local checks | `init.sh`, `init.ps1`, `scripts/check_pins.py` |
| Harness docs | `docs/harness/README.md`, `verification-matrix.md`, `sensor-registry.md`, `change-contract.md` |
| First-agent improvement | `docs/harness/first-agent-task.md` |
| Security and privacy | `security-boundary-map.md`, `feature-privacy-labels.json` |
| Evidence and quality | `evidence-log.md`, `quality-document.md`, `release-controls.md`, `evaluator-rubric.md` |
| Research | `sources.md`, `research-sources.json`, `research-inbox.md`, `source-record.schema.json`, `source-record-example.json` |
| Lifecycle | `self-healing.md`, `entropy-control.md`, `clean-state-checklist.md` |

Each generated file is recorded in `docs/harness/manifest.json` with ownership
metadata and hashes. Project-owned existing files are tracked separately so
drift reporting can distinguish generated changes from preserved local content.

See [harness/manifest.json](harness/manifest.json) for this repo's current
generated inventory and required-file contract.

## Security Model

People may run this tool on personal machines and private repositories, so the
default posture is intentionally restrictive. See [../SECURITY.md](../SECURITY.md)
for vulnerability reporting, scope, and severity guidance.

- Normal `init`, `inspect`, `index`, `effectiveness`, `sync --check`, `audit`,
  `update`, and `doctor` commands use the Python standard library and do not
  install runtime dependencies.
- Existing files are preserved unless `--force` is explicitly supplied.
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
`docs/harness/research-sources.json`; it does not search the web, discover
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

See [harness/effectiveness-eval-contract.md](harness/effectiveness-eval-contract.md).

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

- [harness/sources.md](harness/sources.md)
- [harness/research-sources.json](harness/research-sources.json)
- [harness/research-sources.lock.json](harness/research-sources.lock.json)
- [harness/research-inbox.md](harness/research-inbox.md)

Project-owned source records use
[harness/source-record.schema.json](harness/source-record.schema.json) and
[harness/source-record-example.json](harness/source-record-example.json). They
are for curated project provenance and stay separate from the fixed
HarnessForge research allowlist.
