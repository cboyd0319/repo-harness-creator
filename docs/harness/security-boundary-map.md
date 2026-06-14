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
| Local machine paths | CLI user | Durable output must redact common absolute home paths, including home paths with spaces and the current user's home path. |
| Network calls | Maintainers | Runtime CLI commands must stay local. Scheduled research refresh may fetch default-port HTTPS public-source metadata only. Local files, credentials, localhost, private-address targets, private DNS resolutions, and unsafe redirects are rejected; fetch sockets connect to validated public DNS results while preserving the original host for TLS verification. |
| GitHub workflows | Maintainers | Workflows use least privilege, external Actions pinned to commit SHAs, `PYTHONSAFEPATH=1` for the reusable Action runtime, no persisted checkout credentials in read-only CI, and target-contained Action report paths. |
| Secrets and credentials | Maintainers | No command should print, store, transform, or transmit secrets. |
| Cost-incurring systems | Maintainers | Self-healing must not call paid model or cloud APIs unless a future reviewed workflow explicitly opts in. |

## Data Boundaries

- Generated harness files are project-owned source, not telemetry.
- Reports must avoid machine-specific absolute paths.
- Research refresh stores compact source metadata and links, not full articles.
- Feature privacy labels are generated as a placeholder for projects that handle
  sensitive, private, customer, credential, financial, medical, or paid-service
  data.

## Required Checks

Use the smallest relevant set:

- `python scripts/check_pins.py --root .`
- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m repo_harness_creator audit --target . --min-score 85`
- `./init.sh` for full local POSIX verification.
- `pwsh -NoProfile -File ./init.ps1` for PowerShell verification.
