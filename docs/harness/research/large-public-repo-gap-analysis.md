# Large Public Repo Gap Analysis

Reviewed: 2026-06-16 UTC.

Status: repo-local field analysis.

Inputs:

- `docs/harness/evidence/large-public-repo-analysis.json`
- `docs/harness/evidence/large-public-repo-analysis.md`
- `docs/harness/research/large-public-repo-corpus.json`
- `docs/harness/research/large-codebase-indexing-research.md`

## Boundary

This analysis is HarnessForge repo-local field evidence. It is not copied into
generated target harnesses, does not define GitHub Action behavior, and does
not prove real-agent effectiveness. The field runner did not execute target
project commands. Public repo checkouts live under ignored `.harnessforge/`.

Nested `AGENTS.md` handling remains review-required. HarnessForge should detect
candidate scopes and existing nested instruction files, but it should not write
nested instruction files by default.

## Evidence Summary

| Repo | Stack | Tracked Files | Scanned Files | Components | Observed Gaps |
| --- | --- | ---: | ---: | ---: | --- |
| `kubernetes-kubernetes` | Go | 30,513 | 20,000 | 44 | file scan truncation, nested instruction plan needed, no existing SBOM |
| `microsoft-vscode` | TypeScript/React | 15,783 | 15,407 | 80 | component scan truncation, nested instruction plan needed, no existing SBOM |
| `bazelbuild-bazel` | Bazel | 13,265 | 8,333 | 80 | component scan truncation, nested instruction plan needed |

Cross-repo signals:

- Dry-run generation now uses the requested 20,000-file scan limit in all
  three analyzed repos.
- All three repos produce `harnessforge.nestedInstructionPlan.v1`
  review-required nested instruction-scope candidates.
- VS Code already has nested `AGENTS.md` files, proving the pattern exists in a
  large public monorepo and should be detected as project-owned guidance.
- Kubernetes exceeded the 20,000-file field scan limit.
- VS Code and Bazel reached the 80-component inventory cap.

## Gap Classes

### 1. Generation Uses A Different Scan Than Analysis

Severity: high. Status: implemented for explicit scan limits; persisted index
reuse remains an optional optimization.

Observed in the initial field run: field analysis used `--max-files 20000`,
but dry-run generation still called `create_harness(checkout, dry_run=True)`
with the default 4,000-file scan. That made the preview weaker than the
analysis that preceded it.

Implemented deterministic fix:

- `create_harness` accepts `max_files` and records generated manifest scan
  coverage.
- `quickstart`, `init`, and applied `update` accept `--max-files`.
- The GitHub Action exposes `generation-max-files` for `command: init` and
  applied `command: update`, separate from `report-max-files`.
- `quickstart --json` and `init --dry-run --json` report scan count, limit, and
  truncation status.
- The field analyzer passes its requested `--max-files` into dry-run
  generation and only reports `generator_default_scan_limit` if that requested
  limit is ignored.

Remaining optimization:

- Reuse a single detected `ProjectProfile` or persisted structural index across
  quickstart, dry-run generation, report, and enhance planning when repeated
  scans become a measurable cost.

Definition of done:

- `init --dry-run --json --max-files 20000` reports the same scan limit used by
  `index --max-files 20000`.
- Large-repo corpus evidence no longer reports `generator_default_scan_limit`.

Verification: the 2026-06-16 field refresh across Kubernetes, VS Code, and
Bazel shows dry-run generation using the requested 20,000-file scan limit for
all three repositories. Remaining cross-repo findings are nested instruction
planning and deterministic file-discovery priority ordering.

### 2. File Discovery Needs Large-Repo Coverage Signals

Severity: high.

Observed: Kubernetes has 30,513 tracked files and still hit the 20,000-file
scan limit. The current scanner reports truncation, but it cannot yet tell the
user which high-signal categories were definitely covered.

Implemented deterministic fix:

- Use git tracked-file inventory when available as a read-only file count and
  coverage source.
- Keep the standard-library filesystem walk for non-git targets.
- `index --json`, `report --json`, `quickstart --json`, and
  `init --dry-run --json` expose `harnessforge.fileCoverage.v1` with scanned
  count, total tracked count when known, inventory source, category coverage,
  omitted examples, and warnings.
- The GitHub Action report summary includes file coverage.
- The large-public-repo field analyzer records file-coverage status and reports
  `file_coverage_budget_limited` when a capped scan misses tracked categories.
- Keep target-relative paths only.

Remaining optimization:

- Split future discovery into deterministic priority passes:
  root instruction/runtime files, workflow files, manifests, source-of-truth
  docs, SBOM files, then remaining files up to budget.

Definition of done:

- Large-repo reports can say which categories were fully scanned and which were
  budget-limited.
- `index`, `report`, `quickstart`, and `init --dry-run --json` expose the same
  coverage model.

Verification: the 2026-06-16 field refresh across Kubernetes, VS Code, and
Bazel reports `harnessforge.fileCoverage.v1` for all three repositories. All
three remain `budget_limited`, which confirms reporting is implemented and the
next improvement is deterministic priority ordering before representative
source/test scanning; the field report tracks that remaining work as
`file_discovery_priority`.

### 3. Component Inventory Needs Ranking And Overflow

Severity: high.

Observed: VS Code and Bazel reached the 80-component cap. The cap prevents
unbounded output, but today the omitted components are not ranked or grouped
well enough for harness design.

Deterministic fix:

- Add component ranking:
  root and workspace manifests, workflow working directories, path-filtered CI
  directories, existing nested instruction scopes, package manifests with test
  scripts, then leaf examples/docs/vendor areas.
- Add component groups:
  root, packages/apps/services, language/runtime, tooling, docs/site, examples,
  vendor/third-party, generated.
- Expose `componentOverflow` with omitted count, top omitted examples, and
  recommended review action.
- Add an explicit `--component-limit` option for index/report/dry-run paths.

Definition of done:

- Component caps remain bounded, but reports show why chosen components were
  chosen and what kind of work was omitted.

### 4. Nested Instruction Planning Is A Product Feature

Severity: high for large monorepo quality; medium for default generation
safety. Status: initial product implementation for report and dry-run flows;
index and enhance integration remain follow-up work.

Observed: all three repos produced nested instruction candidates. VS Code also
has existing nested `AGENTS.md` files.

Implemented deterministic fix:

- Add a `nestedInstructionPlan` model outside the repo-local field script.
- Feed it from deterministic signals:
  existing nested `AGENTS.md`, component manifests, workspace markers, and
  component inventory truncation.
- Surface the plan in `report`, `quickstart --json`, and
  `init --dry-run --json`.
- Never write nested `AGENTS.md` by default.

Remaining deterministic follow-up:

- Add workflow path filters, workflow working directories, verification command
  prefixes, top-level package directories, and source-of-truth docs to the
  signal model.
- Surface the plan in `index` and `enhance`.
- When writes are later supported, require explicit path selection and
  confirmation.

Definition of done:

- Large monorepo dry-runs produce a compact review-required nested instruction
  plan.
- Existing nested `AGENTS.md` files are treated as project-owned guidance and
  skipped when producing new candidate paths.

### 5. Verification Command Detection Needs Classification

Severity: medium-high.

Observed: Kubernetes produced multiple nested `go test` commands; VS Code
produced a mix of npm, Cargo, and extension-specific commands; Bazel produced a
root `bazel test //...` command. HarnessForge can detect commands, but it does
not yet classify cost, scope, or safety clearly enough for large repos.

Deterministic fix:

- Classify commands as root smoke, component smoke, full suite, expensive, or
  review-required.
- Prefer small safe commands in generated startup guidance.
- Put expensive all-repo checks in verification matrix or report evidence, not
  root instructions.
- Record the source for each command: manifest script, build file, workflow, or
  fallback heuristic.

Definition of done:

- Generated root instructions pick the smallest reliable detected checks.
- Reports keep full-suite commands visible without making them first-run
  defaults.

### 6. Source-Of-Truth Ranking Needs Noise Control

Severity: medium.

Observed: all repos detected root `README.md` and `AGENTS.md`, but Kubernetes
and VS Code also surfaced many nested README files under third-party, generated,
or highly local directories. That is useful inventory, not necessarily root
source-of-truth.

Deterministic fix:

- Rank root and docs/architecture/spec files above nested package README files.
- Downrank third-party, vendor, generated, fixture, and example docs unless the
  task scope is inside those directories.
- Separate `sourceOfTruth` from `localDocs`.
- Cite why a document is recommended as a source of truth.

Definition of done:

- `repoMap.sourceOfTruth` stays small and high-signal.
- Local component docs remain discoverable without polluting root startup
  guidance.

### 7. Existing Instruction Enhancement Needs Large-Repo Awareness

Severity: medium.

Observed: all three selected repos already had root `AGENTS.md`; VS Code had
nested `AGENTS.md` files. Plain generation skips project-owned instruction
files, but the quality work is in reviewing and improving what already exists.

Deterministic fix:

- Make `enhance` consume the large-repo index and nested instruction plan.
- Report instruction coverage by scope: root, platform routers, nested agents,
  component docs, and verification routing.
- Propose review-only addenda that improve routing and verification without
  taking ownership of project files.

Definition of done:

- `enhance --json` can say whether root instructions route to nested
  instructions, source-of-truth docs, and component-specific verification.

### 8. SBOM Absence Should Stay Advisory

Severity: low for harness generation.

Observed: Kubernetes and VS Code had no detected SPDX or CycloneDX SBOM in the
bounded scan. That is useful release/security context, not a blocker for
normal harness generation.

Deterministic fix:

- Keep existing SBOM detection in index/report.
- Treat missing SBOM as advisory unless a policy preset or release-check flag
  requires it.
- Do not generate SBOMs by default.

Definition of done:

- Large-repo gap reports do not overstate missing SBOMs as harness failures.

## Recommended Build Order

1. Done for explicit scan limits: add `max_files` plumbing to generation
   dry-runs. Shared profile/index reuse remains an optional optimization.
2. Add deterministic file coverage reporting using git inventory when
   available.
3. Add component ranking, grouping, overflow, and `--component-limit`.
4. Done for initial product surfaces: promote nested instruction planning from
   the field script into product code.
5. Done for report and dry-run flows: surface nested plans in report,
   quickstart, and init dry-run JSON. Enhance and index integration remain
   follow-up work.
6. Add verification command classification and source attribution.
7. Split source-of-truth ranking from local component docs.
8. Expand the real public corpus run after each deterministic slice.

## Optional Adapters

These should remain explicit opt-ins:

- ctags for symbol inventory;
- tree-sitter or ast-grep for structural patterns;
- existing SCIP, LSIF, Kythe, Glean, CodeQL, or Semgrep artifacts when present;
- existing local code-search indexes.

Adapters should improve ranking and confidence. They should not be required for
normal `init`, `quickstart`, `report`, or `enhance`.

## Release-Prep Evidence Needed

Before release prep resumes, run a broader field pass:

- at least five repos from the large public corpus, including one very large C
  or C++ repo, one ML repo, one TypeScript monorepo, one Go repo, and one
  build-system repo;
- one local product repo with an already-reviewed harness;
- one repo with existing nested `AGENTS.md`;
- one repo with no instruction files.

Record for each:

- scan coverage;
- component overflow;
- nested instruction plan status;
- generated dry-run write plan;
- verification command classes;
- source-of-truth ranking;
- advisory versus actionable gaps.
