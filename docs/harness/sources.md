# Harness Sources

Reviewed: 2026-06-14 UTC.

This file records the source basis for this repo. Refresh before major harness,
packaging, CI, or platform support changes.

## Primary Sources

| Source | Current use |
| --- | --- |
| OpenAI, "Harness engineering: leveraging Codex in an agent-first world" | Repo-as-spec framing, environment design, intent, feedback loops |
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
| GitHub Actions hosted runner docs | Ubuntu 22.04, macOS 15, and Windows 2025 runner labels |
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
  target-relative report paths that resolve inside `target`.
- Package metadata should make legal files explicit. `pyproject.toml` now uses
  PEP 639 `license-files` metadata for `LICENSE`.
- Durable output should hide home paths across common personal-machine shapes.
  Redaction now covers home paths with spaces and the current user's home path.
- Research refresh is a metadata check for public sources, not a general URL
  fetcher. The refresh script now rejects non-HTTPS URLs, embedded
  credentials, localhost, and literal non-public IP targets before fetching.
- Compatibility instruction files are source-backed. `CLAUDE.md`,
  `GEMINI.md`, and `.github/copilot-instructions.md` route to `AGENTS.md`
  without duplicating the project manual.
- Research provenance is part of the product surface. Public source URLs live
  in `research-sources.json`, refresh metadata lives in
  `research-sources.lock.json`, and local sibling references are recorded in
  this file.
- The root README is treated as the project landing page, not the full manual.
  It now gives the fastest safe path, clear trust boundaries, Action usage,
  verification, source provenance, and links to deeper harness docs.
