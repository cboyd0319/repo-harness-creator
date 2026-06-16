#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from harnessforge.assessment.audit import audit_target, audit_to_dict
from harnessforge.core.redact import redact_local_paths
from harnessforge.generation.generate import create_harness
from harnessforge.project.detect import MISSING_VERIFICATION_COMMAND, detect_project
from harnessforge.project.indexer import build_index_report
from harnessforge.project.readiness import inspect_readiness, readiness_to_dict

SCHEMA_VERSION = "harnessforge.largePublicRepoAnalysis.v1"
LIST_SCHEMA_VERSION = "harnessforge.largePublicRepoCorpusList.v1"
CORPUS_SCHEMA_VERSION = "harnessforge.largePublicRepoCorpus.v1"
DEFAULT_CORPUS = Path("docs/harness/research/large-public-repo-corpus.json")
DEFAULT_WORKDIR = Path(".harnessforge/large-public-repos")
DEFAULT_JSON_REPORT = Path("docs/harness/evidence/large-public-repo-analysis.json")
DEFAULT_MARKDOWN_REPORT = Path("docs/harness/evidence/large-public-repo-analysis.md")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
LOCAL_PATH_RE = re.compile(
    "|".join((r"/" + "Users/", r"/" + "home/", "C:" + r"\\Users\\")),
    re.IGNORECASE,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze real large public repositories against HarnessForge."
    )
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-files", type=int, default=20_000)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument(
        "--clone",
        action="store_true",
        help="clone missing repositories into the ignored checkout root",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=DEFAULT_JSON_REPORT,
        help="write the compact JSON evidence report",
    )
    parser.add_argument(
        "--markdown-report",
        type=Path,
        default=DEFAULT_MARKDOWN_REPORT,
        help="write the compact Markdown evidence report",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list configured corpus repositories without cloning or analysis",
    )
    parser.add_argument("--json", action="store_true", help="print JSON to stdout")
    args = parser.parse_args(argv)

    if args.max_files <= 0:
        parser.error("--max-files must be greater than 0")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be greater than 0")

    root = Path.cwd().resolve()
    corpus = load_corpus(args.corpus)
    errors = validate_corpus(corpus)
    if args.list:
        payload = build_list_payload(corpus, errors)
        emit_payload(payload, args.json)
        return 0 if not errors else 1
    if errors:
        payload = {
            "schemaVersion": SCHEMA_VERSION,
            "mode": "corpus_validation",
            "summary": {"errors": len(errors)},
            "errors": errors,
        }
        emit_payload(payload, args.json)
        return 1

    selected = select_repos(corpus["repos"], ids=tuple(args.repo), limit=args.limit)
    payload = analyze_repos(
        selected,
        corpus=corpus,
        root=root,
        workdir=args.workdir,
        clone_missing=args.clone,
        max_files=args.max_files,
        timeout_seconds=args.timeout_seconds,
    )
    write_report(args.json_report, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_report(args.markdown_report, format_markdown_report(payload))
    emit_payload(payload, args.json)
    return 0 if payload["summary"]["failed"] == 0 else 1


def load_corpus(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_corpus(corpus: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if corpus.get("schemaVersion") != CORPUS_SCHEMA_VERSION:
        errors.append("invalid schemaVersion")
    repos = corpus.get("repos")
    if not isinstance(repos, list) or not repos:
        errors.append("repos must be a non-empty list")
        return errors
    ids: set[str] = set()
    urls: set[str] = set()
    for index, repo in enumerate(repos):
        prefix = f"repos[{index}]"
        repo_id = repo.get("id")
        url = repo.get("url")
        pinned = repo.get("pinnedRef")
        categories = repo.get("categories")
        if not isinstance(repo_id, str) or not repo_id:
            errors.append(f"{prefix}.id is required")
        elif repo_id in ids:
            errors.append(f"duplicate repo id: {repo_id}")
        else:
            ids.add(repo_id)
        if not isinstance(url, str) or not url.startswith("https://github.com/"):
            errors.append(f"{prefix}.url must be a public GitHub HTTPS URL")
        elif url in urls:
            errors.append(f"duplicate repo url: {url}")
        else:
            urls.add(url)
        if not isinstance(pinned, str) or not SHA_RE.match(pinned):
            errors.append(f"{prefix}.pinnedRef must be a 40-character SHA")
        if not isinstance(categories, list) or not categories:
            errors.append(f"{prefix}.categories must be a non-empty list")
    serialized = json.dumps(corpus, sort_keys=True)
    if LOCAL_PATH_RE.search(serialized):
        errors.append("corpus contains a machine-local absolute path")
    return errors


def build_list_payload(corpus: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    return {
        "schemaVersion": LIST_SCHEMA_VERSION,
        "summary": {
            "repos": len(corpus.get("repos", [])),
            "errors": len(errors),
        },
        "errors": errors,
        "repos": [
            {
                "id": repo["id"],
                "repository": repo["repository"],
                "pinnedRef": repo["pinnedRef"],
                "categories": repo["categories"],
            }
            for repo in corpus.get("repos", [])
        ],
    }


def select_repos(
    repos: list[dict[str, Any]], *, ids: tuple[str, ...], limit: int | None
) -> list[dict[str, Any]]:
    selected = repos
    if ids:
        wanted = set(ids)
        selected = [repo for repo in repos if repo["id"] in wanted]
        missing = sorted(wanted - {repo["id"] for repo in selected})
        if missing:
            raise SystemExit(f"unknown repo id(s): {', '.join(missing)}")
    if limit is not None:
        if limit <= 0:
            raise SystemExit("--limit must be greater than 0")
        selected = selected[:limit]
    return selected


def analyze_repos(
    repos: list[dict[str, Any]],
    *,
    corpus: dict[str, Any],
    root: Path,
    workdir: Path,
    clone_missing: bool,
    max_files: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    checkout_root = workdir / "checkouts"
    checkout_root.mkdir(parents=True, exist_ok=True)
    results = [
        analyze_repo(
            repo,
            root=root,
            checkout_root=checkout_root,
            clone_missing=clone_missing,
            max_files=max_files,
            timeout_seconds=timeout_seconds,
        )
        for repo in repos
    ]
    gap_counts = Counter(
        gap["code"]
        for result in results
        for gap in result.get("qualityGaps", [])
    )
    statuses = Counter(result["status"] for result in results)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "mode": "real_public_repo_field_analysis",
        "corpus": {
            "schemaVersion": corpus["schemaVersion"],
            "lastReviewed": corpus.get("lastReviewed"),
            "configuredRepos": len(corpus.get("repos", [])),
            "analysisFocus": corpus.get("analysisFocus", []),
        },
        "execution": {
            "networkAccess": clone_missing,
            "commandsExecuted": True,
            "targetWritesPerformed": False,
            "checkoutRoot": display_path(checkout_root, root),
            "missingReposAreCloned": clone_missing,
            "normalHarnessGenerationNetworkAccess": False,
            "maxFiles": max_files,
        },
        "summary": {
            "selected": len(results),
            "analyzed": statuses.get("analyzed", 0),
            "missing": statuses.get("missing_checkout", 0),
            "failed": statuses.get("failed", 0) + statuses.get("clone_failed", 0),
            "withNestedAgents": sum(
                1
                for result in results
                if result.get("nestedInstructionPlan", {}).get("existingNestedAgents")
            ),
            "withNestedAgentCandidates": sum(
                1
                for result in results
                if result.get("nestedInstructionPlan", {}).get("candidateCount", 0) > 0
            ),
            "qualityGapCounts": dict(sorted(gap_counts.items())),
        },
        "crossRepoFindings": cross_repo_findings(results),
        "repositories": results,
    }


def analyze_repo(
    repo: dict[str, Any],
    *,
    root: Path,
    checkout_root: Path,
    clone_missing: bool,
    max_files: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    checkout = checkout_root / repo["id"]
    checkout_result = ensure_checkout(
        repo,
        checkout=checkout,
        root=root,
        clone_missing=clone_missing,
        timeout_seconds=timeout_seconds,
    )
    base = {
        "id": repo["id"],
        "repository": repo["repository"],
        "url": repo["url"],
        "pinnedRef": repo["pinnedRef"],
        "categories": repo["categories"],
        "analysisFocus": repo.get("analysisFocus", []),
        "checkout": checkout_result,
    }
    if checkout_result["status"] != "available":
        return {
            **base,
            "status": checkout_result["status"],
            "qualityGaps": [
                {
                    "code": checkout_result["status"],
                    "severity": "blocked",
                    "message": checkout_result["message"],
                }
            ],
        }

    try:
        head = git_output(root, ["git", "-C", str(checkout), "rev-parse", "HEAD"], timeout_seconds)
        tracked_files = git_output(
            root,
            ["git", "-C", str(checkout), "ls-files"],
            timeout_seconds,
        ).splitlines()
        profile = detect_project(checkout, max_files=max_files)
        index = build_index_report(profile)
        readiness = readiness_to_dict(inspect_readiness(profile))
        audit = audit_to_dict(audit_target(checkout))
        dry_run = dry_run_generation(checkout, max_files=max_files)
        nested_plan = nested_instruction_plan(profile, repo)
        gaps = quality_gaps(
            profile=profile,
            index=index,
            readiness=readiness,
            dry_run=dry_run,
            nested_plan=nested_plan,
            tracked_count=len(tracked_files),
            max_files=max_files,
        )
        return {
            **base,
            "status": "analyzed",
            "head": head.strip(),
            "headMatchesPinnedRef": head.strip() == repo["pinnedRef"],
            "trackedFileCount": len(tracked_files),
            "detected": {
                "stack": profile.stack,
                "languages": list(profile.languages),
                "packageManagers": list(profile.package_managers),
                "runtimeFiles": list(profile.runtime_files[:20]),
                "verificationCommands": list(profile.verification_commands[:12]),
                "workspaceMarkers": list(profile.workspace_markers),
                "routingMarkers": list(profile.routing_markers),
                "fileScanLimit": profile.file_scan_limit,
                "fileScanTruncated": profile.file_scan_truncated,
                "componentCount": len(profile.components),
                "componentScanLimit": profile.component_scan_limit,
                "componentScanTruncated": profile.component_scan_truncated,
            },
            "indexSummary": index["summary"],
            "repoMap": {
                "primaryLanguages": index["repoMap"]["summary"]["primaryLanguages"],
                "components": index["repoMap"]["components"][:12],
                "sourceOfTruth": index["repoMap"]["sourceOfTruth"][:12],
                "unknowns": index["repoMap"]["unknowns"][:12],
            },
            "readiness": {
                "verdict": readiness["verdict"],
                "warnings": readiness["warnings"][:12],
                "blockedReasons": readiness["blockedReasons"][:12],
                "runnableChecks": readiness["runnableChecks"][:12],
                "reviewStatusSummary": readiness["reviewStatusSummary"],
            },
            "audit": {
                "overall": audit["overall"],
                "bottleneck": audit["bottleneck"],
                "failedCheckCount": sum(
                    1
                    for domain in audit["domains"].values()
                    for check in domain["checks"]
                    if not check["passed"]
                ),
            },
            "dryRunGeneration": dry_run,
            "nestedInstructionPlan": nested_plan,
            "qualityGaps": gaps,
        }
    except Exception as exc:  # pragma: no cover - defensive field-run boundary
        return {
            **base,
            "status": "failed",
            "qualityGaps": [
                {
                    "code": "analysis_failed",
                    "severity": "blocked",
                    "message": sanitize(str(exc)),
                }
            ],
        }


def ensure_checkout(
    repo: dict[str, Any],
    *,
    checkout: Path,
    root: Path,
    clone_missing: bool,
    timeout_seconds: int,
) -> dict[str, Any]:
    if checkout.exists():
        return {
            "status": "available",
            "message": "existing checkout reused",
            "clonedThisRun": False,
        }
    if not clone_missing:
        return {
            "status": "missing_checkout",
            "message": "checkout missing; rerun with --clone to fetch it",
            "clonedThisRun": False,
        }
    try:
        result = subprocess.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                repo["url"],
                str(checkout),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        if result.returncode != 0:
            return clone_failed(result.stderr or result.stdout)
        fetch = subprocess.run(
            ["git", "-C", str(checkout), "fetch", "--depth=1", "origin", repo["pinnedRef"]],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        if fetch.returncode != 0:
            return clone_failed(fetch.stderr or fetch.stdout)
        checkout_result = subprocess.run(
            ["git", "-C", str(checkout), "checkout", "--detach", repo["pinnedRef"]],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        if checkout_result.returncode != 0:
            return clone_failed(checkout_result.stderr or checkout_result.stdout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return clone_failed(str(exc))
    return {
        "status": "available",
        "message": "cloned pinned revision",
        "clonedThisRun": True,
    }


def clone_failed(output: str) -> dict[str, Any]:
    line = sanitize(output).splitlines()
    return {
        "status": "clone_failed",
        "message": line[0] if line else "git clone failed",
        "clonedThisRun": False,
    }


def git_output(root: Path, command: list[str], timeout_seconds: int) -> str:
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_seconds,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(sanitize(detail or f"{command[0]} failed"))
    return result.stdout


def dry_run_generation(checkout: Path, *, max_files: int) -> dict[str, Any]:
    try:
        profile, writes = create_harness(checkout, dry_run=True, max_files=max_files)
    except Exception as exc:  # pragma: no cover - defensive field-run boundary
        return {
            "status": "failed",
            "error": sanitize(str(exc)),
            "writeStatusCounts": {},
            "usesRequestedFileScanLimit": False,
            "usesDefaultFileScanLimit": False,
            "requestedFileScanLimit": max_files,
            "fileScanLimit": 4000,
        }
    counts = Counter(write.status for write in writes)
    return {
        "status": "planned",
        "writeStatusCounts": dict(sorted(counts.items())),
        "plannedWriteCount": sum(counts.values()),
        "usesRequestedFileScanLimit": profile.file_scan_limit == max_files,
        "usesDefaultFileScanLimit": (
            profile.file_scan_limit == 4000 and max_files != 4000
        ),
        "requestedFileScanLimit": max_files,
        "fileScanLimit": profile.file_scan_limit,
        "fileScanTruncated": profile.file_scan_truncated,
    }


def nested_instruction_plan(
    profile: Any, repo: dict[str, Any]
) -> dict[str, Any]:
    existing = sorted(
        file
        for file in profile.files
        if PurePosixPath(file).name == "AGENTS.md" and file != "AGENTS.md"
    )
    component_roots = [
        component_path(component)
        for component in profile.components
        if component_path(component) not in {"", "."}
    ]
    monorepo_signal = (
        "monorepo" in repo.get("categories", [])
        or "multiple nested component manifests" in profile.workspace_markers
        or len(component_roots) >= 4
    )
    candidates = []
    if monorepo_signal:
        for path in component_roots:
            if len(candidates) >= 20:
                break
            if has_nested_agent(existing, path):
                continue
            candidates.append(
                {
                    "path": path,
                    "reason": "component has its own manifest or boundary signal",
                    "recommendedAction": "review_required",
                }
            )
    return {
        "status": "review_required" if candidates else "no_action",
        "writeByDefault": False,
        "rootAgentsPresent": "AGENTS.md" in profile.files,
        "existingNestedAgents": existing[:20],
        "existingNestedAgentCount": len(existing),
        "candidateComponents": candidates,
        "candidateCount": len(candidates),
        "guidance": (
            "Use root AGENTS.md as a short repo-wide router. Add nested "
            "AGENTS.md only for meaningful components whose stack, commands, "
            "ownership, constraints, or verification differ."
        ),
    }


def component_path(component: str) -> str:
    return component.split(" (", 1)[0].strip()


def has_nested_agent(existing: list[str], component: str) -> bool:
    prefix = component.rstrip("/") + "/"
    return any(path.startswith(prefix) for path in existing)


def quality_gaps(
    *,
    profile: Any,
    index: dict[str, Any],
    readiness: dict[str, Any],
    dry_run: dict[str, Any],
    nested_plan: dict[str, Any],
    tracked_count: int,
    max_files: int,
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if tracked_count > max_files or profile.file_scan_truncated:
        gaps.append(
            {
                "code": "file_scan_truncated",
                "severity": "high",
                "message": (
                    f"structural scan covered {len(profile.files)} files with "
                    f"max-files {max_files}, while git tracks {tracked_count}"
                ),
            }
        )
    if profile.component_scan_truncated:
        gaps.append(
            {
                "code": "component_scan_truncated",
                "severity": "high",
                "message": "component inventory reached the bounded component limit",
            }
        )
    if dry_run.get("usesDefaultFileScanLimit"):
        gaps.append(
            {
                "code": "generator_default_scan_limit",
                "severity": "high",
                "message": "dry-run generation ignored the requested max-files scan limit",
            }
        )
    if not index["sourceOfTruth"]:
        gaps.append(
            {
                "code": "missing_source_of_truth",
                "severity": "medium",
                "message": "no high-signal source-of-truth document was detected",
            }
        )
    if readiness["runnableChecks"] == [] or profile.verification_commands == (
        MISSING_VERIFICATION_COMMAND,
    ):
        gaps.append(
            {
                "code": "missing_runnable_verification",
                "severity": "high",
                "message": "no runnable verification command was detected",
            }
        )
    if nested_plan["candidateCount"] > 0:
        gaps.append(
            {
                "code": "nested_agents_review_needed",
                "severity": "medium",
                "message": (
                    "monorepo-style component boundaries should receive a "
                    "reviewed nested instruction plan"
                ),
            }
        )
    if not index["sbom"]:
        gaps.append(
            {
                "code": "no_existing_sbom_detected",
                "severity": "low",
                "message": "no SPDX or CycloneDX SBOM file was detected",
            }
        )
    return gaps


def cross_repo_findings(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if any(
        gap["code"] == "generator_default_scan_limit"
        for result in results
        for gap in result.get("qualityGaps", [])
    ):
        findings.append(
            {
                "code": "generator_max_files_option",
                "message": (
                    "init and dry-run generation need an explicit max-files or "
                    "index-reuse path for very large repositories."
                ),
            }
        )
    if any(
        result.get("nestedInstructionPlan", {}).get("candidateCount", 0) > 0
        for result in results
    ):
        findings.append(
            {
                "code": "nested_agents_plan",
                "message": (
                    "large monorepos should get a review-required nested "
                    "AGENTS.md plan instead of only a root instruction file."
                ),
            }
        )
    if any(
        gap["code"] == "missing_runnable_verification"
        for result in results
        for gap in result.get("qualityGaps", [])
    ):
        findings.append(
            {
                "code": "verification_detection",
                "message": (
                    "verification detection needs stronger stack-specific "
                    "defaults for large projects with custom build tools."
                ),
            }
        )
    return findings


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def emit_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if payload.get("schemaVersion") == LIST_SCHEMA_VERSION:
            print(format_list(payload), end="")
        elif payload.get("schemaVersion") == SCHEMA_VERSION and "repositories" in payload:
            print(format_text_summary(payload), end="")
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))


def format_list(payload: dict[str, Any]) -> str:
    lines = [
        "Large public repo corpus",
        f"Repos: {payload['summary']['repos']}",
        f"Errors: {payload['summary']['errors']}",
        "",
        "Repositories:",
    ]
    lines.extend(
        f"  - {repo['id']}: {repo['repository']}" for repo in payload["repos"]
    )
    return "\n".join(lines).rstrip() + "\n"


def format_text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "Large public repo analysis",
        f"Selected: {summary['selected']}",
        f"Analyzed: {summary['analyzed']}",
        f"Missing checkouts: {summary['missing']}",
        f"Failed: {summary['failed']}",
        "",
        "Repositories:",
    ]
    for repo in payload["repositories"]:
        lines.append(
            f"  - {repo['id']}: {repo['status']}"
            + (
                f", stack={repo['detected']['stack']}, gaps={len(repo['qualityGaps'])}"
                if repo["status"] == "analyzed"
                else ""
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def format_markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Large Public Repo Analysis",
        "",
        f"Generated: {payload['generatedAt']}",
        "",
        "## Boundary",
        "",
        "- This is repo-local field evidence for HarnessForge.",
        "- Checkouts live under the ignored `.harnessforge/large-public-repos/` tree.",
        "- Normal HarnessForge generation, tests, and the GitHub Action do not clone public repositories.",
        "- Nested `AGENTS.md` entries are review-required candidates, not default writes.",
        "",
        "## Summary",
        "",
        f"- Configured corpus repos: {payload['corpus']['configuredRepos']}",
        f"- Selected repos: {payload['summary']['selected']}",
        f"- Analyzed repos: {payload['summary']['analyzed']}",
        f"- Missing checkouts: {payload['summary']['missing']}",
        f"- Failed repos: {payload['summary']['failed']}",
        f"- Repos with nested `AGENTS.md` candidates: {payload['summary']['withNestedAgentCandidates']}",
        "",
        "## Cross-Repo Findings",
        "",
    ]
    if payload["crossRepoFindings"]:
        lines.extend(
            f"- `{item['code']}`: {item['message']}"
            for item in payload["crossRepoFindings"]
        )
    else:
        lines.append("- No cross-repo product findings in this run.")
    lines.extend(
        [
            "",
            "## Repository Results",
            "",
            "| Repo | Status | Stack | Tracked | Scanned | Components | Nested Plan | Top Gaps |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for repo in payload["repositories"]:
        if repo["status"] != "analyzed":
            lines.append(
                f"| `{repo['id']}` | `{repo['status']}` | n/a | 0 | 0 | 0 | n/a | "
                f"{repo['qualityGaps'][0]['message']} |"
            )
            continue
        gaps = ", ".join(gap["code"] for gap in repo["qualityGaps"][:4]) or "none"
        lines.append(
            f"| `{repo['id']}` | `analyzed` | `{repo['detected']['stack']}` | "
            f"{repo['trackedFileCount']} | "
            f"{repo['indexSummary']['fileCount']} | "
            f"{repo['detected']['componentCount']} | "
            f"{repo['nestedInstructionPlan']['candidateCount']} candidates | "
            f"{gaps} |"
        )
    lines.extend(["", "## Nested Instruction Candidate Examples", ""])
    for repo in payload["repositories"]:
        if repo["status"] != "analyzed":
            continue
        candidates = repo["nestedInstructionPlan"]["candidateComponents"][:8]
        if not candidates:
            continue
        lines.append(f"### `{repo['id']}`")
        lines.append("")
        lines.extend(f"- `{candidate['path']}`" for candidate in candidates)
        if repo["nestedInstructionPlan"]["candidateCount"] > len(candidates):
            remaining = repo["nestedInstructionPlan"]["candidateCount"] - len(candidates)
            lines.append(f"- ... {remaining} more candidates in JSON report")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return "<external-checkout-root>"


def sanitize(text: str) -> str:
    return redact_local_paths(text).replace(str(Path.cwd()), "<repo-root>")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
