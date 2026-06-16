# Large Public Repo Analysis

Generated: 2026-06-16T17:42:48+00:00

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
- `file_discovery_priority`: file coverage is now visible, and sampled large repos still show budget-limited categories; improve deterministic priority ordering before representative source/test scanning.

## Repository Results

| Repo | Status | Stack | Tracked | Scanned | Coverage | Components | Nested Plan | Top Gaps |
| --- | --- | --- | ---: | ---: | --- | ---: | --- | --- |
| `kubernetes-kubernetes` | `analyzed` | `go` | 30513 | 20000 | `budget_limited` | 44 | 43 candidates | file_scan_truncated, file_coverage_budget_limited, nested_agents_review_needed, no_existing_sbom_detected |
| `microsoft-vscode` | `analyzed` | `typescript-react` | 15783 | 15407 | `budget_limited` | 80 | 77 candidates | file_coverage_budget_limited, component_scan_truncated, nested_agents_review_needed, no_existing_sbom_detected |
| `bazelbuild-bazel` | `analyzed` | `bazel` | 13265 | 8333 | `budget_limited` | 80 | 79 candidates | file_coverage_budget_limited, component_scan_truncated, nested_agents_review_needed |

## Nested Instruction Candidate Examples

### `kubernetes-kubernetes`

- `hack/tools`
- `cluster/addons/addon-manager`
- `cluster/images/etcd-version-monitor`
- `cluster/images/kubemark`
- `hack/tools/golangci-lint`
- `hack/tools/instrumentation`
- `cluster/addons/dns/coredns`
- `cluster/addons/dns/kube-dns`
- ... 35 more candidates in JSON report

### `microsoft-vscode`

- `.devcontainer`
- `.eslint-plugin-local`
- `cli`
- `remote`
- `scripts`
- `test`
- `extensions/bat`
- `extensions/clojure`
- ... 69 more candidates in JSON report

### `bazelbuild-bazel`

- `docs`
- `examples`
- `scripts`
- `site`
- `src`
- `third_party`
- `tools`
- `examples/cpp`
- ... 71 more candidates in JSON report
