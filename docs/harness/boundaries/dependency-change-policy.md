# Dependency Change Policy

Status: live

## Rule

Default to the latest stable or supported release. Do not guess. Verify the
current date and a current primary source before changing package, CLI, vendor
API, workflow action, Python, Node, npm, PowerShell, or security-tool versions.

Use exact pins for direct package dependencies and immutable commit SHAs for
external GitHub Actions. If the newest stable release has a known reachable
security issue, pin the newest supported clean release and record the reason.
When `pins.toml` is present, `scripts/check_pins.py` ties Python package pins,
`package.json` direct package versions, `package-lock.json` integrity values,
Containerfile base image tags and digests, and profile image tags back to that
reviewed ledger.

## Decision Order

1. Use the standard library when it is enough.
2. Use a native platform feature when it covers the need.
3. Use an already-installed dependency when it removes real complexity.
4. Add the smallest new dependency only when the value is clear.

## Required Evidence

Record:

- Current date checked.
- Primary source used for the latest stable version.
- Why standard library, native platform, or installed dependencies were not
  enough.
- Pin or lockfile update.
- Focused test, build, audit, or smoke command.
- Python 3.13+, macOS 15+, Windows 11+, and Ubuntu 22.04+ impact.

## Current Pins

- Reviewed package and runtime pins are recorded in `pins.toml`.
- `setuptools==82.0.1` in `pyproject.toml`, verified against PyPI on
  2026-06-14.
- GitHub Actions use full-length commit SHAs with version comments.
- CI tests Python `3.13.14` and `3.14.6`, the current 3.13 and 3.14 bugfix
  releases checked on 2026-06-14.

## GitHub Actions

External Actions must use full-length commit SHAs plus version comments:

```yaml
uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6
```

Refresh pins only after verifying the upstream tag or release from the action
repository.
