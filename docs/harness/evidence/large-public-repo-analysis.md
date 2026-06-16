# Large Public Repo Analysis

Generated: 2026-06-16T18:45:45+00:00

## Boundary

- This is repo-local field evidence for HarnessForge.
- Checkouts live under the ignored `.harnessforge/large-public-repos/` tree.
- Normal HarnessForge generation, tests, and the GitHub Action do not clone public repositories.
- Nested `AGENTS.md` entries are review-required candidates, not default writes.

## Summary

- Configured corpus repos: 13
- Selected repos: 3
- Analyzed repos: 3
- Missing checkouts: 0
- Failed repos: 0
- Repos with nested `AGENTS.md` candidates: 3

## Cross-Repo Findings

- `nested_agents_plan`: large monorepos produce review-required nested AGENTS.md candidates; keep them advisory and improve ranking before any explicit write mode.
- `file_discovery_priority`: file coverage now distinguishes eligible from intentionally skipped files, and some sampled large repos still show budget-limited eligible categories; improve deeper deterministic ranking for Kubernetes-scale scans.

## Repository Results

`Docs` is `sourceOfTruth/localDocs`.

| Repo | Status | Stack | Tracked | Eligible | Scanned | Skipped | Coverage | Components | Docs | Verification | Nested Plan | Top Gaps |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | --- |
| `kubernetes-kubernetes` | `analyzed` | `go` | 30513 | 30461 | 20000 | 52 | `budget_limited` | 44/44 | 2/103 | 21 test | 43 candidates | file_scan_truncated, file_coverage_budget_limited, nested_agents_review_needed, no_existing_sbom_detected |
| `microsoft-vscode` | `analyzed` | `typescript-react` | 15783 | 15407 | 15407 | 376 | `budget_limited` | 80/145 | 4/67 | 17 build,static-analysis,test | 77 candidates | file_coverage_budget_limited, component_scan_truncated, nested_agents_review_needed, no_existing_sbom_detected |
| `bazelbuild-bazel` | `analyzed` | `bazel` | 13265 | 8333 | 8333 | 4932 | `complete` | 80/186 | 3/79 | 1 test | 79 candidates | component_scan_truncated, nested_agents_review_needed |

## Nested Instruction Candidate Examples

### `kubernetes-kubernetes`

- `hack/tools`
- `hack/tools/golangci-lint`
- `hack/tools/instrumentation`
- `cluster/addons/addon-manager`
- `cluster/images/etcd-version-monitor`
- `cluster/images/kubemark`
- `cluster/addons/dns/coredns`
- `cluster/addons/dns/kube-dns`
- ... 35 more candidates in JSON report

### `microsoft-vscode`

- `src/vs/sessions/test/e2e`
- `src/vs/sessions/test/e2e/extensions/sessions-e2e-mock`
- `scripts`
- `test`
- `test/automation`
- `test/mcp`
- `test/monaco`
- `test/sanity`
- ... 69 more candidates in JSON report

### `bazelbuild-bazel`

- `src`
- `src/conditions`
- `src/java_tools/buildjar`
- `src/java_tools/import_deps_checker`
- `src/java_tools/junitrunner`
- `src/java_tools/singlejar`
- `src/main/cpp`
- `src/main/native`
- ... 71 more candidates in JSON report
