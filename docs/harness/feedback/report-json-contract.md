# Report JSON Contract

Status: implemented

`harnessforge report --json` emits `harnessforge.report.v1`. The report is
read-only: it does not run target commands, install dependencies, apply
updates, publish artifacts, or write files unless the caller supplies a
target-relative `--json-report` or `--markdown-report` path.

## Stable Fields

Downstream tools and GitHub Action summaries may rely on these fields:

| Field | Purpose |
| --- | --- |
| `schemaVersion` | Current value: `harnessforge.report.v1` |
| `target` | Target name with local root omitted |
| `mode` | Current value: `read_only` |
| `execution` | `commandsExecuted` and `writesPerformed`, both `false` |
| `detectedStack` | Detected primary stack label |
| `readiness` | Verdict, warnings, blockers, review surfaces, and high-risk acceptance summary |
| `reviewWork` | Separates unresolved actionable review work from accepted advisory inventory |
| `audit` | Structural score, bottleneck, failed checks, and recommendations |
| `drift` | Generated-file drift summary and recommended actions |
| `index` | Structural index summary, compact repo map, file coverage, SBOM evidence, and source-of-truth docs |
| `nestedInstructionPlan` | Review-required nested `AGENTS.md` candidates for monorepos; never default writes |
| `verifyEvidence` | Stored full or compact verify evidence inventory |
| `effectiveness` | Stored real-agent or benchmark evidence assessment summary |
| `instructionQuality` | Startup instruction signal, budget, and section-quality summary |
| `skillWiring` | Repo-local harness skill wiring status |
| `firstAgentTask` | First-agent lifecycle status and evidence path |
| `platform` | Platform contract and source-review metadata |
| `policyPresets` | Available, applied, and recommended policy presets |
| `sbomAdapter` | Existing SBOM status and explicit opt-in generation boundary |
| `releaseControls` | Release-control document presence |
| `docsFanout` | Authoritative fact map, changed-surface budget, and duplicate fact summary |
| `featureState` | Feature/task state alignment, scope-drift signals, and an advisory `summary.verifiedCompletionRate` (verified-with-evidence over activated features) |
| `observability` | Runtime and process signal coverage |
| `indexAdapters` | Optional index-adapter availability and explicit opt-in status |
| `maturity` | Evidence-gated maturity level |
| `nextActions` | Deduplicated human-readable next actions |

## Review Work

`reviewWork.unresolvedActionable` counts pending review surfaces and readiness
blockers that should be resolved before relying on the harness.

`reviewWork.acceptedAdvisory` lists surfaces that were detected as high-risk
but accepted by target-contained evidence, such as
`docs/harness/evidence/first-agent-review.json`.

`reviewWork.advisoryInventory` keeps warning-only inventory separate from
actionable review work. Do not treat accepted advisory surfaces as unresolved
work unless the target repo changes the underlying workflow, instruction,
container, hook, or tool boundary.

## File Coverage

`index.fileCoverage` has schema `harnessforge.fileCoverage.v1`. It reports the
bounded scan limit, scanned file count, total tracked file count when known,
inventory source, category coverage, omitted examples, and warnings.

For git checkouts, `inventorySource` is `git_tracked` and `totalFileCount` is
based on `git ls-files`. For non-git targets, `inventorySource` is
`filesystem_scan`; `totalFileCount` is `null` when the filesystem scan was
truncated.

Do not treat `index.summary.fileCount` as total repository size when
`index.fileCoverage.coverageComplete` is `false`.

## Source And Local Docs

`index.sourceOfTruth` is intentionally narrow. It includes root instruction
files, root project docs, high-signal global docs, and structured spec-system
files. Nested component README files and local documentation stay under
`index.localDocs` and `index.repoMap.localDocs`.

Use `sourceOfTruth` for startup routing and repo-wide instruction quality.
Use `localDocs` for component-specific review, nested instruction candidates,
and scoped implementation context.

## Nested Instruction Plan

`nestedInstructionPlan` has schema `harnessforge.nestedInstructionPlan.v1`.
It is advisory and `writeByDefault` is always `false`.

Candidate records include:

- `rank`: review priority within the bounded candidate list.
- `rankSignals`: compact reasons such as verification source files, workflow
  routing files, local docs, and boundary markers.
- `reviewFocus`: machine-readable areas the nested instruction review should
  cover, such as `verification`, `workflow-routing`, `local-docs`, and
  `boundary-markers`.

When component detection is capped, overflow-derived candidates stay separate
under `omittedCandidateComponents` with `omittedCandidateCount`,
`omittedCandidateListTruncated`, and `omittedGuidance`. This keeps the normal
candidate list stable while telling maintainers when to raise
`--component-limit` or manually review omitted paths.

Ranking uses detected component boundaries, existing nested instruction files,
component-local docs, verification command attribution, and workflow path or
working-directory signals. It does not parse private source text, execute
target commands, or write nested `AGENTS.md` files.

## Verification Commands

`index.verificationCommands` has schema
`harnessforge.verificationCommands.v1`. It keeps the existing command strings
but adds command class, scope, source type, source path, source detail, and
confidence for each detected command.

Command classes are currently `test`, `build`, `static-analysis`, `format`,
`aggregate`, `other`, or `missing`. Source types identify the attribution
surface, such as `package-script`, `makefile-target`, `justfile-recipe`,
`python-project`, `script`, `bazel-workspace`, or explicit `cli` input.

This is structural attribution only. `report` and `index` do not execute the
commands, install dependencies, or prove the command is sufficient for a
specific change.

## Verify Evidence

`verifyEvidence.reports[*].schemaVersion` may be either:

- `harnessforge.verify.v1` for full reports with capped stdout/stderr previews.
- `harnessforge.verifySummary.v1` for compact summaries without stdout/stderr
  previews.

Release gates require the latest valid evidence to be fresh, run-mode, passed,
and free of blocked, failed, timed-out, or error summary counts.
