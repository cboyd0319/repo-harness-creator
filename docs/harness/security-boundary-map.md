# Security Boundary Map

Status: live

This repo is a local CLI and reusable GitHub Action. It should remain safe by
default for arbitrary repositories.

People will run this code on personal machines. The product rule is: choose the
most secure and easiest behavior for every edge case. If those conflict,
security wins and the tool must explain the safe next step.

## Access Boundaries

| Boundary | Current Owner | Rule |
| --- | --- | --- |
| Target repository files | CLI user | `init` and `update` skip existing files unless `--force` is explicitly passed. |
| Generated paths | CLI user | Generated paths must remain inside the target repo after symlink resolution. Unsafe `--agent-file` paths are rejected. |
| Project detection reads | CLI user | Root manifests are read only when they resolve inside the target repo. Symlink escapes are ignored. |
| Local machine paths | CLI user | Durable output and loaded harness docs/state must not contain machine-local absolute paths unless the user explicitly requests that exact path and the audit is run with the explicit override. Routine generated output redacts common absolute home paths, including home paths with spaces and the current user's home path. |
| Network calls | Maintainers | Runtime CLI commands must stay local. Scheduled research refresh may fetch default-port HTTPS public-source metadata from the fixed allowlist in `research-sources.json` only. It must not search for latest research, discover new URLs, or promote fetched text without review. Local files, credentials, localhost, private-address targets, private DNS resolutions, and unsafe redirects are rejected; fetch sockets connect to validated public DNS results while preserving the original host for TLS verification. |
| Untrusted content | Maintainers | Public websites, issue text, generated logs, retrieved documents, and source metadata can carry prompt injection, indirect prompt injection, or data poisoning attempts. Treat scanners as advisory, withhold suspicious fetched metadata from durable output, and require human review before promotion into templates, audit checks, or policy. |
| Agent tools and outputs | Maintainers | Tool descriptions, schemas, return values, retrieved chunks, and agent-to-agent output are untrusted data. Apply least privilege, validate tool arguments, redact secrets in logs, and require exact human approval before destructive, externally visible, credential-touching, or cost-incurring actions. |
| Rules, build, and workflow files | Maintainers | Agent instruction files, workflow files, package scripts, build scripts, and deployment config are security-critical. Review changes as prompt-to-code supply-chain changes and require focused tests when behavior changes. |
| Verification commands | Maintainers | Treat `init.sh`, `init.ps1`, package scripts, Make targets, workflow commands, and harness-declared checks as executable code. Review command changes before running them from untrusted branches or generated updates. |
| Training, demo, and intentionally vulnerable fixtures | Maintainers | Do not automatically remediate accepted vulnerable examples, challenge code, or fixtures unless the user asks for that scope. Record owner, path, and risk acceptance; scan findings must separate intentional training content from product defects. |
| Threat model and control evidence | Maintainers | Material AI/RAG/agent, tool, external-service, auth, secret, data-flow, or deployment changes must update boundary docs, defect/evidence records, and focused abuse-case checks. |
| GitHub workflows | Maintainers | Workflows use least privilege, external Actions pinned to commit SHAs, `PYTHONSAFEPATH=1` for the reusable Action runtime, no persisted checkout credentials in read-only CI, cancellation for superseded CI runs, and target-contained Action report paths that reject POSIX and Windows absolute/rooted syntax. |
| Secrets and credentials | Maintainers | No command should print, store, transform, or transmit secrets. |
| Cost-incurring systems | Maintainers | Prefer local verification and local commits during active work. Push only at explicit batch boundaries or by user request. Self-healing must not call paid model or cloud APIs unless a future reviewed workflow explicitly opts in. |

## Data Boundaries

- Generated harness files are project-owned source, not telemetry.
- Reports and durable harness files must avoid machine-specific absolute paths
  unless an explicit user request is recorded.
- Research refresh stores compact source metadata and links, not full articles.
- Suspicious fetched metadata is withheld when it resembles agent instructions
  or credential-exfiltration prompts, including invisible Unicode and
  Markdown/HTML exfiltration markers.
- Feature privacy labels are generated as a placeholder for projects that handle
  sensitive, private, customer, credential, financial, medical, or paid-service
  data.

## Required Checks

Use the smallest relevant set:

- `python scripts/check_pins.py --root .`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m harnessforge audit --target . --min-score 85`
- `./init.sh` for full local POSIX verification.
- `pwsh -NoProfile -File ./init.ps1` for PowerShell verification.
