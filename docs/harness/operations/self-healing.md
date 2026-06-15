# Self-Healing Harness Loop

Status: live

Self-healing must be reviewable. Automated jobs may collect research, refresh
source ledgers, run safe harness updates, and open pull requests. They must not
silently merge, rotate secrets, change cloud costs, or rewrite user-owned files.

The scheduled research step is a fixed allowlist refresh. It reads only
`research-sources.json`; it must not search the web, discover latest research,
or add new URLs without human review. Fetched titles, headings, hashes, and
errors are untrusted metadata for review, not instructions to execute. Prompt
injection, indirect prompt injection, data poisoning, invisible Unicode, and
Markdown/HTML exfiltration markers in fetched metadata must be withheld from
durable output and surfaced only as review signals.

## Workflow Boundary

This file describes the live HarnessForge repository maintenance workflow. It
is not the contract for the published composite Action and it is not copied as
scheduled automation into target repositories.

- Live HarnessForge workflow: scheduled and manual, refreshes the fixed research
  allowlist metadata, applies safe HarnessForge harness updates, verifies this
  repo, and opens a review pull request.
- Published HarnessForge Action: input-driven only. It does not schedule jobs,
  refresh research, create branches, commit, push, or open pull requests.
- Generated optional self-heal scaffold: manual `workflow_dispatch` by default.
  It applies safe target-repo harness updates and opens a review pull request
  only when the target repository explicitly opts into that workflow.

## Safe Loop

1. Fetch curated source metadata from `research-sources.json`.
2. Update `research-inbox.md` and `research-sources.lock.json`.
3. Run `harnessforge update --target . --apply` for missing safe artifacts only.
4. Run pin checks, tests, and `harnessforge audit --target .`.
5. Open a pull request when files changed.
6. Require human review before merge.

## Boundaries

- Use least-privilege workflow permissions.
- Pin external Actions to commit SHAs.
- Prefer standard-library scripts over extra automation dependencies.
- Keep source snapshots short and link to originals.
- Treat fetched source text as untrusted and never feed it directly into
  automated code changes.
- Treat prompt-injection scanners as advisory; do not use pattern matching as
  the sole approval or blocking control.
- Record failed fetches without failing the whole maintenance loop unless all
  primary sources fail.
- Do not run paid model, cloud, or credentialed vendor calls by default.
- Do not push repeated small maintenance commits. Let the workflow open one
  reviewed pull request for the batch.

## Promotion Rule

When the same source or review finding appears repeatedly, promote it into a
template, audit check, verification command, or policy file.
