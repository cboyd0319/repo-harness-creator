# Harness Sources

Reviewed: 2026-06-15 UTC.

This file records the source basis for this repo. Refresh before major harness,
packaging, CI, or platform support changes.

## Primary Sources

| Source | Current use |
| --- | --- |
| OpenAI, "Harness engineering: leveraging Codex in an agent-first world" | Repo-as-spec framing, environment design, intent, feedback loops |
| OpenAI Codex guide, "Building an AI-Native Engineering Team" | Delegate/Review/Own boundaries across planning, design, build, test, review, documentation, and operations |
| Anthropic, "Effective harnesses for long-running agents" | Long-running work needs more than compaction and a high-level prompt |
| Anthropic, "Harness design for long-running application development" | One-feature-at-a-time execution and handoff artifacts |
| Martin Fowler, "Harness engineering for coding agent users" | Guides and sensors model, feedback loops, reducing review toil |
| Martin Fowler, "Maintainability sensors for coding agents" | Local and CI sensors, slower drift checks, maintainability feedback |
| Red Hat, "Harness Engineering: Structured Workflows for AI-Assisted Development" | Structured context before free-form prompts, repository impact maps |
| Thoughtworks, "Harness engineering and agent feedback: Exploring AI coding sensors" | Sensor design and feedback flywheel for harness improvement |
| LangChain, "The Anatomy of an Agent Harness" | Filesystem, state, collaboration surface, sandbox and memory primitives |
| LangChain Deep Agents harness docs | Execution environment, context management, delegation, and HITL patterns |
| AGENTS.md open format and OpenAI AGENTS.md docs | Predictable root instruction file for coding agents |
| Claude Code memory docs | `CLAUDE.md` loader behavior and `@AGENTS.md` import pattern |
| Gemini CLI `GEMINI.md` docs | `GEMINI.md` loader behavior and `@file.md` import pattern |
| Google Antigravity Agent docs | Antigravity support for mounted `AGENTS.md` instruction files |
| GitHub Copilot custom instructions docs | Repository-wide `.github/copilot-instructions.md` path |
| GitHub Copilot CLI custom instructions docs | Copilot use of root `AGENTS.md` and `.github/copilot-instructions.md` |
| Python Packaging User Guide | `pyproject.toml`, console scripts, and package metadata |
| Python command-line and environment docs | `PYTHONSAFEPATH` import-path hardening for the composite Action runtime |
| Python PEP 11 and Python downloads | Python 3.13+ and supported-platform framing |
| GitHub Actions metadata syntax and composite action docs | Root `action.yml` inputs, outputs, and composite action shape |
| GitHub Actions hosted runner docs | Ubuntu 22.04, macOS 15, and `windows-2025-vs2026` runner labels |
| `actions/setup-python` docs | Explicit Python 3.13 setup in the reusable action |
| `actions/checkout` and `actions/setup-python` tag refs | Verified full-length SHA pins for v6 on 2026-06-14 |
| PyPI setuptools JSON API | Verified `setuptools==82.0.1` as latest stable on 2026-06-14 |
| Walking Labs learn-harness-engineering full English course | Five-subsystem harness framing, feature-list primitive, clean-state checklist, evaluator rubric, quality document, and initial creator script baseline |
| Walking Labs Lecture 02, skills, and harness-creator skill | Scoring the harness tuple, generic creator structure, validator/report scripts, and compatibility artifacts |
| AgentPatterns.ai, "GitHub Copilot: Harness Engineering for Agent-Ready Code" | Backpressure, repo legibility, mechanical enforcement, multi-session scaffolding, and rollback-first operations |
| Epsilla, "The Repository is the OS" and agent-control harness writing | Repo-as-operating-system framing, codified implicit rules, and validation logic inside the repository |
| Charles Anim `harness-engineering` skill repo | OpenAI-style harness setup packaged as an agent skill for multiple coding agents |
| "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents" | Task state, observability, verification, permissions, entropy auditing, and episode evidence |
| "Observability-Driven Automatic Evolution of Coding-Agent Harnesses" | Observability and feedback-driven harness correction loop |
| "Code as Agent Harness" | Executable, verifiable, stateful agent harness direction |
| Awesome Code as Agent Harness Papers | Harness-interface, mechanism, scaling, and application taxonomy plus source-catalog quality controls |
| "AutoHarness: improving LLM agents by automatically synthesizing a code harness" | Invalid-action prevention, environment feedback, and synthesized harness candidates as proposal-only changes |
| "Natural-Language Agent Harnesses" | Inspectable modular harness policy documents, explicit runtime contracts, and artifact boundaries |
| "VeRO: A Harness for Agents to Optimize Agents" | Versioned snapshots, budget-controlled evaluation, rewards, observations, and structured traces |
| "Claw-SWE-Bench" and "RealClawBench" | Adapter contracts, workspace reconstruction, patch extraction, runtime budgets, deterministic scorers, and cost accounting |
| "ClawsBench" and "Agent-ValueBench" | Separate success, safety, value, and trajectory-level scoring for agent harnesses |
| "Building Effective AI Coding Agents for the Terminal" | Terminal-agent safety controls, context management, model routing, memory, and instruction-reminder patterns |
| "Agentic Harness for Real-World Compilers" | Domain-specific harnesses need project-owned tools, benchmarks, and sparse-bug workflow support |
| Lee et al., "Meta-Harness: End-to-End Optimization of Model Harnesses" | Candidate-sensitive harness evaluation, full-history traces, queryable run logs, held-out validation, Pareto quality/cost frontiers, and frozen-replay overclaim boundaries |
| VS Code, "The Coding Harness Behind GitHub Copilot in VS Code" | Editor-harness responsibilities and Copilot feedback-loop framing |
| HumanLayer, "Harness Engineering for Coding Agents" | Harness as coding-agent configuration surface and skill/prompt/tooling practice |
| GitHub Docs, "About the repository README file" | README purpose, expected content, relative links, and keeping deep docs outside the landing page |
| GitHub Docs, "Basic writing and formatting syntax" | Markdown heading, link, code block, list, and image behavior on GitHub |
| The Turing Way, "Landing Page - README File" | README as project landing page, audience fit, fast start, and jargon control |
| Kubernetes README | Large-project README pattern: short value statement, getting-started links, development, support, governance, roadmap |
| FastAPI README | Product README pattern: tagline, feature/value bullets, install, example, docs, license |
| uv README | CLI README pattern: concise positioning, badges, quick install, docs-first navigation |
| pip README | Infrastructure README pattern: concise purpose, docs links, release cadence, support, contribution, code of conduct |
| pytest README | Developer-tool README pattern: minimal example, features, documentation, issue route, support, security, license |
| Black README | Opinionated-tool README pattern: clear positioning, quick usage, configuration stance, contributing, changelog, code of conduct |
| pre-commit README | Minimal README pattern that sends users to canonical docs when the README is not the full manual |
| Requests README | Minimal mature-project README pattern with docs-first routing |
| OpenSSF Scorecard | Security posture signal and supply-chain best-practice framing |
| OWASP Cheat Sheet Series project | Practical application-security good-practice source set |
| OWASP Security Shepherd | Intentionally vulnerable training apps need explicit scope boundaries, local tests before push, CI cost controls, and release SBOM evidence |
| OWASP pytm | Threat model freshness, LLM/RAG/agent attributes, and focused controls for prompt injection, RAG poisoning, excessive agency, code execution, and data exposure |
| OWASP SAMM | Risk-driven software assurance loop across governance, design, implementation, verification, and operations, with policy-to-check and evidence mapping |
| OWASP AI Agent Security, MCP Security, LLM Prompt Injection Prevention, RAG Security, Secure AI Model Ops, and Secure Coding with AI cheat sheets | Agent trust boundaries, untrusted tool/retrieval output, prompt injection, data poisoning, least privilege, human approval, test integrity, and poisoned metadata controls |
| OWASP CI/CD Security, GitHub Actions Security, Software Supply Chain Security, Dependency Graph/SBOM, Secrets Management, Secure Code Review, Threat Modeling, and Logging cheat sheets | CI least privilege, workflow trigger caution, action pinning, supply-chain provenance, secret logging limits, manual review scope, threat modeling, and audit evidence controls |
| pnpm, Yarn, npm, and Bun workspace docs | JavaScript package-manager workspace root markers and workspace-member routing |
| Turborepo, Nx, Lerna, and Rush docs | JavaScript monorepo orchestrator markers and root-vs-leaf task routing |
| uv workspace docs | Python workspace root marker, shared lockfile model, and all-package run behavior |
| Cargo and Go workspace docs | Rust `[workspace]` and Go `go.work` multi-module workspace detection |
| Gradle multi-project and Maven POM docs | JVM multi-project root markers: `settings.gradle(.kts)` and `pom.xml <modules>` |
| Microsoft .NET solution docs | `.sln` and `.slnx` solution files as multi-project roots |
| Bazel, Pants, and Buck2 docs | Polyglot build-system root markers and root-scoped test commands |
| GitHub Actions workflow syntax docs | Monorepo workflow routing through path filters, reusable workflows, local actions, and `working-directory` |
| Terraform standard module structure docs | Infrastructure roots and nested modules as component boundaries |
| Atlassian monorepo tutorial, Medium monorepo guide, awesome-monorepo, General Reasoning vanilla monorepo, Harness IDP sandbox monorepo, and tomsoir Bazel monorepo | Field examples for large Git performance concerns, app/package/tool/config layouts, vanilla component-folder routing, IDP-generated app roots, and Bazel-plus-pnpm polyglot layouts |
| Chris Mamon and Lukas Masuch repo-local harness field reports | Repo-local harnesses as project-specific workflow, state, validation, automation, and agent-instruction layers |

## Local References

- Bluepeak-AI `docs/harness` local sibling reference.
- JobSentinel `docs/harness` local sibling reference.
- Walking Labs `learn-harness-engineering` local sibling reference.
- Persona `AGENTS.md` local sibling reference for source/docs/tests/contracts
  alignment and research-first routing.
- pi-harness local sibling reference for exact dependency pins, lockfile review,
  package install safety, and harness-as-product discipline.
- JobSentinel `docs/harness/sources.md` local sibling reference for dated
  harness source inventory and refresh checklist.
- Walking Labs `docs/en/resources`, `docs/en/projects`, `projects`, and
  `skills/harness-creator` local sibling references for initializer flow,
  structural benchmarking, project progression, and skill-packaged harness
  validation patterns.
- Awesome Code as Agent Harness Papers local sibling reference for the
  harness-paper taxonomy, source-list release controls, and missing-citation
  handling.

Generated harnesses must use portable URLs, repo-relative paths, or
project-owned docs instead of machine-specific absolute paths.

## Applied Findings From Latest Pass

- Feature state is a primitive, not a memo. Generated feature records now carry
  behavior, verification, status, and evidence fields.
- Clean session exit is part of done. Generated harnesses include
  `clean-state-checklist.md`.
- Structural audit is not proof of product quality. Generated harnesses include
  `evaluator-rubric.md` and `quality-document.md` for output and codebase
  review.
- Audit scoring should expose weak domains. The overall score now applies a
  bottleneck penalty instead of using only a simple average.
- Harness docs should be navigable and portable. The audit now checks local
  Markdown links and rejects absolute local-path links.
- Dependency and workflow changes need latest-stable evidence plus hard pins.
  This repo now checks exact Python build pins and SHA-pinned GitHub Actions.
- A world-class harness needs reviewed self-healing, not silent mutation. This
  repo now has a scheduled research refresh and safe-update PR loop.
- Sensitive or external-service data flows need machine-readable classification.
  Generated harnesses now include placeholder privacy labels and a security
  boundary map for project-specific completion.
- Monorepos and multi-component repos need explicit routing boundaries.
  Generated harnesses now include `component-inventory.md` and record detected
  package/runtime component manifests.
- Workspace roots and leaf components are different boundaries. Detection now
  records workspace/orchestrator markers separately from nested package
  manifests, including JavaScript workspaces, uv/Cargo/Go workspaces,
  Gradle/Maven/.NET multi-project roots, and Bazel/Pants/Buck roots.
- Some monorepos have no root workspace tool. Detection now records inferred
  multi-component layouts, repo routing markers such as GitHub workflow path
  filters and `working-directory`, local Actions, devcontainers, Harness IDP
  folders, and existing agent-instruction files.
- Infrastructure monorepos often use Terraform roots and nested modules as the
  practical ownership boundary. Detection now treats standard Terraform root
  files as component markers without adding Terraform-specific dependencies.
- Personal-machine trust requires fail-closed filesystem behavior. `init`
  rejects unsafe instruction filenames, preflights generated destinations, and
  refuses writes that resolve outside the target repo.
- Audit and detection reads must respect the same trust boundary. Discovery now
  skips symlinked directories, ignores root manifest symlinks that resolve
  outside the target repo, and audit reads only known files that resolve inside
  the target repo.
- Action startup should not let caller-controlled files shadow the Action
  library. The reusable Action now sets `PYTHONSAFEPATH=1` and `PYTHONPATH` to
  the action checkout.
- Action report paths should be easy to reason about and not write outside the
  audited repository by accident. The reusable Action now accepts only
  target-relative report paths that resolve inside `target`, and emits
  slash-separated target-relative report outputs on every runner.
- Package metadata should make legal files explicit. `pyproject.toml` now uses
  PEP 639 `license-files` metadata for `LICENSE`.
- Durable output should hide home paths across common personal-machine shapes.
  Redaction now covers home paths with spaces and the current user's home path.
- Research refresh is a metadata check for the fixed `research-sources.json`
  allowlist, not a general URL fetcher or latest-research discovery job. The
  refresh script now rejects non-HTTPS URLs, embedded credentials, non-default
  HTTPS ports, localhost, literal non-public IP targets, hostnames that resolve
  to non-public addresses, and redirects to unsafe targets before fetching.
- Agentic-security sources now include OWASP LLM, OWASP Agentic Applications,
  OWASP Agentic Skills, the Microsoft AGT prompt-injection benchmark, and
  user-supplied agentic Top 10 commentary. The control imported from those
  sources is conservative: public/retrieved content is untrusted, prompt
  injection and data poisoning metadata is withheld, scanners are advisory, and
  human review remains the promotion gate.
- OWASP CheatSheetSeries added concrete harness controls for AI coding agents,
  MCP, RAG, CI/CD, GitHub Actions, supply chain, SBOM, secrets, secure review,
  threat modeling, and logging. Imported controls remain bounded: least
  privilege, exact approval for high-impact actions, untrusted tool/retrieval
  output, review of rules/build/workflow files, scanner-as-signal treatment,
  test integrity review, and CI cost discipline through local-first checks.
- OWASP Security Shepherd reinforces that intentionally vulnerable training,
  demo, or fixture code is a scoped exception. Harness instructions now require
  owner/path/risk context and must not auto-remediate accepted vulnerable
  examples unless the user asks for that work.
- OWASP pytm reinforces threat model freshness. Material AI/RAG/agent, tool,
  external-service, auth, secret, data-flow, and deployment changes now require
  boundary docs, evidence updates, and focused abuse-case checks.
- OWASP SAMM provides the maturity lens for keeping harness controls tied to
  governance, design, implementation, verification, and operations instead of
  standalone checklists. Policies should resolve to runnable checks, review
  evidence, defect records, or explicit risk acceptance.
- Suspicious research metadata now withholds invisible Unicode and
  Markdown/HTML exfiltration markers in addition to direct instruction and
  credential-exfiltration patterns.
- Remote CI is useful but not free. Agents should do local checks and local
  commits during active work, then push only at an explicit batch boundary,
  release point, or user request.
- Read-only CI jobs should not keep checkout credentials available to later
  steps. The main CI checkout now opts out of persisted credentials; the
  self-heal workflow keeps credentials because it intentionally pushes a
  review branch.
- Compatibility instruction files are source-backed. `CLAUDE.md`,
  `GEMINI.md`, and `.github/copilot-instructions.md` route to `AGENTS.md`
  without duplicating the project manual.
- Local agent-platform best-practice and memory notes reinforced the same
  pattern: one canonical checked-in instruction file, short platform routers,
  local override files ignored, and platform auto-memory treated as personal
  state until stable facts are promoted into reviewed harness docs.
- The OpenAI Codex AI-native engineering guide reinforced SDLC-specific
  ownership boundaries. Generated harnesses now spell out what agents may
  draft, what humans must review, and what maintainers still own across
  planning, design/build, testing, review/docs, and deploy/maintain work.
- Agent-written tests need test-integrity review, not only successful execution.
  Harness guidance now prefers a separate test-design step for behavior changes,
  rejects stubbed or assertion-free tests, and asks maintainers to confirm new
  tests fail before implementation when practical.
- Agent-assisted code review should stay high-signal. The evaluator now points
  reviews toward correctness, security, data integrity, migration risk,
  scalability, test integrity, and architecture instead of style noise.
- Research provenance is part of the product surface. Public source URLs live
  in `research-sources.json`, refresh metadata lives in
  `research-sources.lock.json`, and local sibling references are recorded in
  this file.
- Harness docs and reports should use repo-relative paths. Machine-local
  absolute paths need an explicit user request and reviewable evidence.
- The root README is treated as the project landing page, not the full manual.
  It now gives the fastest safe path, clear trust boundaries, Action usage,
  verification, source provenance, and links to deeper harness docs.
- Deeper Walking Labs resource, project, and harness-creator skill review
  reinforced generated-harness quality gates, initializer baseline commits,
  explicit optional workflow scaffolds, structural benchmark caveats, release
  evidence, and release rollback controls. The imported controls are local and
  reviewable: generated pin checking, generated release controls, optional
  manual workflow scaffolds, manifest drift tests, and a generated-harness
  `100/100` quality gate.
- Deferred heavier Walking Labs ideas for project-specific opt-ins rather than
  default generation: architecture/layer scanners, memory index cap checks,
  memory topic cleanup, and agent-specific tool-permission config validation.
  These need repo ownership and false-positive review before becoming generic
  harness output.
- Local sibling harness comparison covered macos-container-agents,
  Bluepeak-AI, persona, pi-harness, WormsWMD-macOS-Fix, unifi-configs,
  JobSentinel, and cboyd0319. Imported controls are deliberately generic:
  root-agnostic init execution, PowerShell native exit-code enforcement,
  optional credential-free local verification, broader advisory pin signals,
  entropy promotion/evidence/stop rules, explicit completion bars, isolated
  release-artifact smoke-test guidance, and root scratch-report ignore patterns.
  App telemetry headers, model routing rules, public wiki mapping, file-size
  budgets, pre-commit lockfile hooks, and credential-backup test wrappers remain
  project-specific opt-ins.
- Local Harness Forge and the Meta-Harness paper reinforced that real
  harness-effectiveness claims need candidate-sensitive metrics, held-out
  validation, anti-leakage checks, worst-case quality, do-no-harm floors, and
  queryable run logs. Imported controls are limited to eval guidance and
  advisory detection of skill, plugin, and installer surfaces.
- The Code as Agent Harness paper catalog and additional harness-eval papers
  reinforced a bounded eval contract: name the changed harness layer, keep
  candidate snapshots versioned, require adapter/workspace/runtime contracts,
  separate success from safety and trajectory quality, and treat synthesized or
  evolved harnesses as proposals until reviewed.
- A deeper pass over the Code as Agent Harness catalog reinforced surface-level
  eval classification: reasoning, action, environment, mechanism, and scaling
  changes need different feedback channels. Multi-agent or adaptive harnesses
  also need explicit roles, interaction mode, topology, shared representation,
  synchronization rule, and convergence rule before results are comparable.
  Source catalogs should keep canonical URLs, missing-citation records, stale
  venue checks, dedup policy, and optional broken-link checks.
- Source-ledger hygiene is now an offline gate, not only a research-refresh
  side effect. The gate checks duplicate source IDs and URLs, required source
  fields, placeholder text, local-path leakage, canonical source URL shape,
  arXiv `/abs/` links, and lock-file consistency before any network fetch.
- Effectiveness eval guidance now has a machine-readable evidence schema and
  example payload. The schema keeps harness-effectiveness claims separate from
  structural audit and project verification by requiring baseline/candidate
  snapshots, held-out task controls, replay type, feedback channels, runtime
  and adapter contracts, candidate-sensitive metrics, worst-case quality,
  trajectory safety, result artifacts, rollback, and human approval.
