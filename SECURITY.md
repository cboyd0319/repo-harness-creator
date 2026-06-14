# Security Policy

## Reporting Vulnerabilities

Do not report active vulnerabilities through public GitHub issues.

Use GitHub private vulnerability reporting if it is enabled for this repository.
If private reporting is unavailable, open a minimal public issue asking for a
private contact path without including exploit details, secrets, private
repository data, or proof-of-concept payloads.

## Local Execution Threat Model

HarnessForge runs on personal machines and private repositories. The
safe default is to preserve existing files, keep writes inside the requested
target repository, redact common local home paths, and avoid network access
during normal local harness generation.

Primary trust boundaries:

| Boundary | Expected control |
| --- | --- |
| Target repository writes | Existing files are preserved unless `--force` is explicit. |
| Generated paths | Traversal, absolute instruction filenames, and symlink escapes are rejected. |
| Project detection | Root manifest symlinks resolving outside the target repository are ignored. |
| Reports and durable output | Common local home paths are redacted; Action report paths must stay target-relative. |
| Research refresh | Network access is explicit, public HTTPS only, and rejects private/local targets and unsafe redirects. |
| GitHub Action runtime | `PYTHONSAFEPATH=1` prevents caller workspace modules from shadowing the Action library. |

The scheduled research refresh path is the exception to the normal no-network
rule. It accepts default-port HTTPS public-source URLs only, rejects unsafe
redirect targets, and connects fetch sockets to validated public DNS results
while preserving the original host for TLS verification.

## In-Scope Reports

Security reports are in scope when they affect:

- unsafe writes outside a target repository
- overwrite behavior that bypasses the explicit `--force` requirement
- path traversal, symlink escape, or absolute-path handling
- secret exposure in command output, reports, generated files, or logs
- GitHub Action behavior that writes outside the checked-out target
- research refresh behavior that can fetch local, private, credentialed, or
  redirected unsafe URLs

## Severity Guide

| Severity | Examples |
| --- | --- |
| Critical | Reliable arbitrary file overwrite outside the target repository or credential disclosure from private local files. |
| High | Path containment bypass, symlink escape, or Action report write outside the target repository. |
| Medium | Redaction failure for common local home paths or unsafe research-refresh redirect handling. |
| Low | Defense-in-depth hardening, unclear safe-error messaging, or non-sensitive information disclosure. |

## Supported Versions

Until release tags exist, security fixes target the current `main` branch.
After tagged releases begin, this file should list supported release lines.
