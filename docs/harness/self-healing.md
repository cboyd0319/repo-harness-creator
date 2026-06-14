# Self-Healing Harness Loop

Status: live

Self-healing must be reviewable. Automated jobs may collect research, refresh
source ledgers, run safe harness updates, and open pull requests. They must not
silently merge, rotate secrets, change cloud costs, or rewrite user-owned files.

The scheduled research step is a fixed allowlist refresh. It reads only
`research-sources.json`; it must not search the web, discover latest research,
or add new URLs without human review. Fetched titles, headings, hashes, and
errors are untrusted metadata for review, not instructions to execute. Prompt
injection, indirect prompt injection, and data poisoning patterns in fetched
metadata must be withheld from durable output and surfaced only as review
signals.

## Safe Loop

1. Fetch curated source metadata from `research-sources.json`.
2. Update `research-inbox.md` and `research-sources.lock.json`.
3. Run `repo-harness update --target . --apply` for missing safe artifacts only.
4. Run pin checks, tests, and `repo-harness audit --target .`.
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

## Promotion Rule

When the same source or review finding appears repeatedly, promote it into a
template, audit check, verification command, or policy file.
