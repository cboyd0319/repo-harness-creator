# Release Controls

Status: live

Use this file before release tags, public Action adoption, package publishing,
or other externally visible release steps.

## Release Gate

- Run `./init.sh` and `pwsh -NoProfile -File ./init.ps1`.
- Run `harnessforge verify --target . --run --json-report
  docs/harness/evidence/verify-<date>.json`, or record why runnable project
  verification could not run.
- Review any failed, timed_out, or blocked check with owner, risk, and next
  action before promotion.
- Run `python scripts/check_pins.py --root .`.
- Run `python -m harnessforge audit --target . --min-score 85`.
- Run the manual macOS and Windows `workflow_dispatch` platform CI check when
  release changes touch shell behavior, paths, packaging, or GitHub Action
  behavior.
- Before publishing a package or Action release, build the release artifact and
  smoke test it from an isolated directory outside this repository so local
  source files cannot hide missing package data or broken entry points.
- Record SBOM, provenance, artifact, package, and tag evidence when release
  artifacts are published.
- Confirm rollback: tag deletion policy, package yanking policy, feature flag,
  or revert path.

## Evidence To Record

| Item | Evidence |
| --- | --- |
| Local verification | Command, date, result |
| Verify run review | Report path, verdict, owner, risk, and next action for unresolved checks |
| Manual platform check | Runner or host, command, result |
| SBOM | Path, generator, or reason not applicable |
| Provenance | Signing, attestation, or reason not applicable |
| Artifact integrity | Hash, signature, or registry digest |
| Rollback | Concrete command or documented decision |

## Release Notes

- Separate structural harness score, audit score, runnable check evidence, and
  real-agent effectiveness.
- Link representative agent/session results when release claims depend on agent
  behavior.
- Keep deferred release controls in `progress.md` or the active plan with owner,
  reason, and risk.
