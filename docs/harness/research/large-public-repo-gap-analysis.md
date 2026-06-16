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
| `kubernetes-kubernetes` | Go | 30,513 | 20,000 | 44 | file scan truncation, generator default scan limit, nested instruction plan needed, no existing SBOM |
| `microsoft-vscode` | TypeScript/React | 15,783 | 15,407 | 80 | component scan truncation, generator default scan limit, nested instruction plan needed, no existing SBOM |
| `bazelbuild-bazel` | Bazel | 13,265 | 8,333 | 80 | component scan truncation, generator default scan limit, nested instruction plan needed |

Cross-repo signals:

- `create_harness(..., dry_run=True)` used the default 4,000-file scan for all
  three repos, even when field analysis used `--max-files 20000`.
- All three repos produced nested instruction-scope candidates.
- VS Code already has nested `AGENTS.md` files, proving the pattern exists in a
  large public monorepo and should be detected as project-owned guidance.
- Kubernetes exceeded the 20,000-file field scan limit.
- VS Code and Bazel reached the 80-component inventory cap.

## Gap Classes

### 1. Generation Uses A Different Scan Than Analysis

Severity: high.

Observed: field analysis used `--max-files 20000`, but dry-run generation still
called `create_harness(checkout, dry_run=True)` with the default 4,000-file
scan. That makes the preview weaker than the analysis that preceded it.

Deterministic fix:

- Add `max_files` to `create_harness`.
- Add `--max-files` to `init`, `quickstart`, and any dry-run path that renders
  generation plans.
- Reuse a single detected `ProjectProfile` or persisted structural index across
  quickstart, dry-run generation, report, and enhance planning when the caller
  requests deeper analysis.
- Include scan coverage in generated manifests and dry-run JSON:
  scanned files, tracked files when git is available, scan limit, and
  truncation status.

Definition of done:

- `init --dry-run --json --max-files 20000` reports the same scan limit used by
  `index --max-files 20000`.
- Large-repo corpus evidence no longer reports `generator_default_scan_limit`.

### 2. File Discovery Needs Large-Repo Coverage Signals

Severity: high.

Observed: Kubernetes has 30,513 tracked files and still hit the 20,000-file
scan limit. The current scanner reports truncation, but it cannot yet tell the
user which high-signal categories were definitely covered.

Deterministic fix:

- Use git tracked-file inventory when available as a read-only file count and
  coverage source.
- Keep the standard-library filesystem walk for non-git targets.
- Split discovery into deterministic passes:
  root instruction/runtime files, workflow files, manifests, source-of-truth
  docs, SBOM files, then remaining files up to budget.
- Report coverage by category rather than only one truncation boolean.
- Keep target-relative paths only.

Definition of done:

- Large-repo reports can say which categories were fully scanned and which were
  budget-limited.
- `index`, `report`, `quickstart`, and `init --dry-run --json` expose the same
  coverage model.

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
safety.

Observed: all three repos produced nested instruction candidates. VS Code also
has existing nested `AGENTS.md` files.

Deterministic fix:

- Add a `nestedInstructionPlan` model outside the repo-local field script.
- Feed it from deterministic signals:
  existing nested `AGENTS.md`, component manifests, workspace markers,
  workflow path filters, workflow working directories, verification command
  prefixes, top-level package directories, and source-of-truth docs.
- Surface the plan in `index`, `report`, `quickstart`, `init --dry-run --json`,
  and `enhance`.
- Never write nested `AGENTS.md` by default.
- When writes are later supported, require explicit path selection and
  confirmation.

Definition of done:

- Large monorepo dry-runs produce a compact review-required nested instruction
  plan.
- Existing nested `AGENTS.md` files are treated as project-owned guidance and
  routed from the root instruction plan.

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

1. Add `max_files` plumbing and shared profile/index reuse to generation
   dry-runs.
2. Add deterministic file coverage reporting using git inventory when
   available.
3. Add component ranking, grouping, overflow, and `--component-limit`.
4. Promote nested instruction planning from the field script into product code.
5. Surface nested plans in report, quickstart, init dry-run JSON, and enhance.
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
