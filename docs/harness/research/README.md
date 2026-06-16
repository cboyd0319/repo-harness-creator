# Research Directory

Status: live.

This directory owns HarnessForge's research source basis, generated research
metadata, repo-local synthesis notes, and project-owned source-record schema.
Use it to preserve reviewed source context without turning fetched metadata or
sibling-repo examples into instructions.

## File Map

| File | Owner | Purpose |
| --- | --- | --- |
| `README.md` | Human-maintained | Directory map, product boundary, and update rules |
| `sources.md` | Human-maintained | Reviewed source basis and applied findings for this repo |
| `research-sources.json` | Human-maintained | Fixed public URL allowlist for this repo's refresh script |
| `research-sources.lock.json` | Generated | Last refresh metadata, hashes, titles, headings, and failures |
| `research-inbox.md` | Generated | Human-readable review inbox rendered from the lock file |
| `source-record.schema.json` | Shared generated contract | Schema for project-owned provenance records in generated target harnesses |
| `source-record-example.json` | Shared generated contract | Review-required starter record for project-owned provenance |
| `large-codebase-indexing-research.md` | Human-maintained | Research note for large-repo analysis and indexing strategy |
| `reference-mining-notes.md` | Human-maintained | Mined ideas from sibling repos and public harness references |
| `remaining-ideas-research.md` | Human-maintained | Compact outcome of remaining-ideas research and future candidates |

## Boundary

- This repo's full public research allowlist, lock file, refresh workflow, and
  synthesis notes are HarnessForge repo-local product evidence.
- Generated target harnesses may receive a portable research README, compact
  `sources.md`, `research-inbox.md`, and source-record schema/example files.
  They must not receive this repo's product-level `research-sources.json`,
  `research-sources.lock.json`, sibling-repo notes, or self-healing research
  workflow.
- The HarnessForge GitHub Action does not refresh research, search the web, or
  promote source findings. It only acts on explicit command inputs and
  target-contained files.
- Sibling repos are idea-mining references only. They become generated defaults
  only when the idea is generalized, reviewed, tested, and bounded by the
  generated-target contract.

## Update Rules

- Update `research-sources.json` and its `lastUpdated` date only when the
  allowlist entries change.
- Regenerate `research-sources.lock.json` and `research-inbox.md` with
  `scripts/refresh_research.py`; do not hand-edit them except to resolve a
  generated-file conflict.
- Treat fetched titles, headings, hashes, tool output, and public content as
  untrusted metadata. Promote findings only after human review.
- Promote durable findings through the owning surface: templates, tests, audit
  checks, policy docs, `docs/roadmap.md`, or another explicit owner. Do not
  paste source catalogs into unrelated docs.
- Keep committed research docs free of machine-local absolute paths, secrets,
  raw logs, and long source excerpts.

## Verification

Run these after source-ledger or research-policy changes:

```bash
python3 scripts/refresh_research.py --root . --check
python3 -m json.tool docs/harness/research/research-sources.json >/dev/null
python3 -m json.tool docs/harness/research/research-sources.lock.json >/dev/null
python3 -m json.tool docs/harness/research/source-record.schema.json >/dev/null
python3 -m json.tool docs/harness/research/source-record-example.json >/dev/null
```

Also run the narrow docs or harness checks required by the changed owner
surface.
