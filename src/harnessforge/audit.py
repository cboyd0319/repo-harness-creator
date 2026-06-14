from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .models import AuditResult, CheckResult, DomainScore
from .paths import is_absolute_path_text, is_inside_root, path_from_relative_text
from .redact import redact_local_paths

DOMAIN_ORDER = (
    "instructions",
    "tools",
    "environment",
    "state",
    "feedback",
    "scope",
    "lifecycle",
)

LOCAL_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_:/.-])("
    r"(?:[A-Za-z]:[\\/][^\s`'\"<>)]*)|"
    r"(?:/(?:Users|home|tmp|private/tmp|var/folders|Volumes)[^\s`'\"<>)]*)"
    r")"
)


def audit_target(
    target: Path, *, allow_local_absolute_paths: bool = False
) -> AuditResult:
    root = target.resolve()
    files = _load_known_files(root)
    manifest = _load_manifest(root)
    manifest_failures = _manifest_failures(root, manifest)
    link_failures = _local_markdown_link_failures(root, files)
    local_path_failures = (
        []
        if allow_local_absolute_paths
        else _local_absolute_path_failures(files)
    )
    domains = (
        _score("instructions", _instruction_checks(files)),
        _score("tools", _tool_checks(files)),
        _score("environment", _environment_checks(files)),
        _score("state", _state_checks(files)),
        _score("feedback", _feedback_checks(files, link_failures)),
        _score(
            "scope",
            _scope_checks(
                files,
                local_path_failures,
                allow_local_absolute_paths=allow_local_absolute_paths,
            ),
        ),
        _score("lifecycle", _lifecycle_checks(files)),
    )
    total = sum(domain.score for domain in domains)
    average = (total / (len(domains) * 5)) * 100
    weakest = min(domain.score for domain in domains)
    overall = max(0, min(100, round(average - ((5 - weakest) * 4))))
    bottleneck = min(domains, key=lambda item: (item.score, DOMAIN_ORDER.index(item.name))).name
    recommendations = _recommendations(
        domains,
        manifest_failures,
        link_failures,
        local_path_failures,
    )
    return AuditResult(
        target_name=root.name,
        overall=overall,
        bottleneck=bottleneck,
        domains=domains,
        recommendations=recommendations,
        manifest_failures=tuple(manifest_failures),
    )


def audit_to_dict(result: AuditResult) -> dict[str, Any]:
    return {
        "target": result.target_name,
        "overall": result.overall,
        "bottleneck": result.bottleneck,
        "domains": {
            domain.name: {
                "score": domain.score,
                "passed": domain.passed,
                "total": domain.total,
                "checks": [
                    {
                        "passed": check.passed,
                        "message": check.message,
                        "detail": check.detail,
                    }
                    for check in domain.checks
                ],
            }
            for domain in result.domains
        },
        "manifestFailures": list(result.manifest_failures),
        "recommendations": list(result.recommendations),
    }


def format_audit(result: AuditResult) -> str:
    lines = [
        f"Harness audit for {result.target_name}",
        f"Overall: {result.overall}/100",
        f"Bottleneck: {result.bottleneck}",
        "",
    ]
    for domain in result.domains:
        lines.append(f"{domain.name}: {domain.score}/5 ({domain.passed}/{domain.total})")
        for check in domain.checks:
            status = "PASS" if check.passed else "FAIL"
            detail = f" ({check.detail})" if check.detail else ""
            lines.append(f"  {status} {check.message}{detail}")
        lines.append("")
    if result.manifest_failures:
        lines.append("Manifest failures:")
        for failure in result.manifest_failures:
            lines.append(f"  - {failure}")
        lines.append("")
    if result.recommendations:
        lines.append("Recommended next actions:")
        for recommendation in result.recommendations:
            lines.append(f"  - {recommendation}")
    return redact_local_paths("\n".join(lines))


def render_html_report(result: AuditResult) -> str:
    domain_html = []
    for domain in result.domains:
        checks = "\n".join(
            "<li class='{cls}'><strong>{status}</strong> {message}{detail}</li>".format(
                cls="pass" if check.passed else "fail",
                status="PASS" if check.passed else "FAIL",
                message=html.escape(check.message),
                detail=f" <span>{html.escape(check.detail)}</span>" if check.detail else "",
            )
            for check in domain.checks
        )
        domain_html.append(
            f"""
      <section>
        <h2>{html.escape(domain.name)} <span>{domain.score}/5</span></h2>
        <ul>{checks}</ul>
      </section>"""
        )
    recs = "".join(f"<li>{html.escape(item)}</li>" for item in result.recommendations)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Harness Audit: {html.escape(result.target_name)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #172026; background: #f7f8fa; }}
    main {{ max-width: 960px; margin: 0 auto; }}
    header, section {{ background: #fff; border: 1px solid #d9dee5; border-radius: 8px; padding: 18px; margin-bottom: 14px; }}
    h1 {{ margin: 0 0 8px; }}
    h2 {{ display: flex; justify-content: space-between; gap: 20px; margin: 0 0 10px; }}
    .summary {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .metric {{ border: 1px solid #d9dee5; border-radius: 8px; padding: 12px 14px; min-width: 160px; }}
    .metric strong {{ display: block; font-size: 28px; }}
    li {{ margin: 6px 0; }}
    .pass {{ color: #126c43; }}
    .fail {{ color: #a23020; }}
    span {{ color: #56616b; }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Harness Audit: {html.escape(result.target_name)}</h1>
      <div class="summary">
        <div class="metric">Overall<strong>{result.overall}/100</strong></div>
        <div class="metric">Bottleneck<strong>{html.escape(result.bottleneck)}</strong></div>
      </div>
    </header>
    {''.join(domain_html)}
    <section>
      <h2>Recommended Next Actions</h2>
      <ul>{recs}</ul>
    </section>
  </main>
</body>
</html>
"""


def _load_known_files(root: Path) -> dict[str, str]:
    candidates = [
        "AGENTS.md",
        "CLAUDE.md",
        ".github/copilot-instructions.md",
        "README.md",
        "action.yml",
        "docs/action.md",
        "pyproject.toml",
        "package.json",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "global.json",
        "composer.json",
        "Gemfile",
        "Makefile",
        ".python-version",
        ".nvmrc",
        ".tool-versions",
        "Dockerfile",
        ".devcontainer/devcontainer.json",
        "feature_list.json",
        "feature-list.json",
        "progress.md",
        "session-handoff.md",
        "init.sh",
        "init.ps1",
        "scripts/check_pins.py",
        "scripts/refresh_research.py",
        ".github/workflows/ci.yml",
        ".github/workflows/harness-self-heal.yml",
        "docs/harness/README.md",
        "docs/harness/change-contract.md",
        "docs/harness/verification-matrix.md",
        "docs/harness/component-inventory.md",
        "docs/harness/dependency-change-policy.md",
        "docs/harness/security-boundary-map.md",
        "docs/harness/feature-privacy-labels.json",
        "docs/harness/evidence-log.md",
        "docs/harness/clean-state-checklist.md",
        "docs/harness/evaluator-rubric.md",
        "docs/harness/quality-document.md",
        "docs/harness/release-controls.md",
        "docs/harness/self-healing.md",
        "docs/harness/manifest.json",
        "docs/harness/sources.md",
        "docs/harness/research-sources.json",
        "docs/harness/research-sources.lock.json",
        "docs/harness/research-inbox.md",
        "docs/harness/entropy-control.md",
        "docs/harness/agent-operating-model.md",
        "docs/harness/multi-agent-orchestration.md",
        "docs/harness/feature-list.schema.json",
    ]
    loaded: dict[str, str] = {}
    for candidate in candidates:
        path = root / candidate
        text = _read_text_inside_root(path, root)
        if text is None:
            continue
        loaded[candidate] = text
    return loaded


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / "docs/harness/manifest.json"
    text = _read_text_inside_root(path, root)
    if text is None:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"_invalid": "docs/harness/manifest.json is not valid JSON"}
    return parsed if isinstance(parsed, dict) else {}


def _manifest_failures(root: Path, manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not manifest:
        return failures
    if "_invalid" in manifest:
        return [str(manifest["_invalid"])]
    for required in manifest.get("requiredFiles", []):
        if not isinstance(required, str):
            continue
        path = root / path_from_relative_text(required)
        if is_absolute_path_text(required) or not is_inside_root(path, root):
            failures.append(f"Required file from manifest points outside repo: {required}")
        elif not path.exists():
            failures.append(f"Missing required file from manifest: {required}")
    snippets = manifest.get("requiredHarnessSnippets", {})
    if isinstance(snippets, dict):
        for file_name, required_snippets in snippets.items():
            if not isinstance(file_name, str) or not isinstance(required_snippets, list):
                continue
            path = root / path_from_relative_text(file_name)
            if is_absolute_path_text(file_name) or not is_inside_root(path, root):
                failures.append(
                    f"Required snippet file from manifest points outside repo: {file_name}"
                )
                continue
            text = _read_text_inside_root(path, root)
            if text is None:
                continue
            for snippet in required_snippets:
                if isinstance(snippet, str) and snippet not in text:
                    failures.append(f"Missing required snippet in {file_name}: {snippet}")
    return failures


def _local_markdown_link_failures(root: Path, files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for file_name, text in files.items():
        if not file_name.endswith(".md"):
            continue
        source = root / file_name
        for raw_target in re.findall(
            r"(?<!!)\[[^\]]+\]\(([^)]+)\)", _strip_markdown_code_blocks(text)
        ):
            target = raw_target.strip()
            if " " in target and not target.startswith("<"):
                target = target.split(" ", 1)[0]
            target = target.strip("<>")
            lower = target.lower()
            if (
                not target
                or lower.startswith(("http://", "https://", "mailto:", "tel:"))
            ):
                continue

            path_text, _, fragment = target.partition("#")
            path_text = unquote(path_text.split("?", 1)[0])
            fragment = unquote(fragment.split("?", 1)[0])
            if not path_text and not fragment:
                continue

            if not path_text:
                destination = source
            elif is_absolute_path_text(path_text):
                failures.append(f"{file_name} links to absolute local path: {path_text}")
                continue
            else:
                destination = source.parent / path_from_relative_text(path_text)

            if not is_inside_root(destination, root):
                failures.append(f"{file_name} links outside the repository: {target}")
                continue
            if not destination.exists():
                failures.append(f"{file_name} links to missing local file: {path_text}")
                continue
            if (
                fragment
                and destination.suffix.lower() in {".md", ".markdown"}
                and not _markdown_anchor_exists(root, destination, files, fragment)
            ):
                failures.append(f"{file_name} links to missing local anchor: {target}")
    return failures


def _local_absolute_path_failures(files: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for file_name, text in files.items():
        for match in LOCAL_ABSOLUTE_PATH_RE.finditer(text):
            failures.append(f"{file_name}: {redact_local_paths(match.group(1))}")
            if len(failures) >= 10:
                return failures
    return failures


def _strip_markdown_code_blocks(text: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None and (
            stripped.startswith("```") or stripped.startswith("~~~")
        ):
            fence = stripped[:3]
            lines.append("")
            continue
        if fence is not None:
            lines.append("")
            if stripped.startswith(fence):
                fence = None
            continue
        lines.append(line)
    return "\n".join(lines)


def _markdown_anchor_exists(
    root: Path, destination: Path, files: dict[str, str], fragment: str
) -> bool:
    target_text = _markdown_target_text(root, destination, files)
    if target_text is None:
        return True
    return fragment.strip().lower() in _markdown_anchors(target_text)


def _markdown_target_text(
    root: Path, destination: Path, files: dict[str, str]
) -> str | None:
    try:
        relative = destination.resolve(strict=False).relative_to(
            root.resolve(strict=False)
        )
    except ValueError:
        return None
    return files.get(relative.as_posix()) or _read_text_inside_root(destination, root)


def _markdown_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    heading_counts: dict[str, int] = {}
    stripped = _strip_markdown_code_blocks(text)
    for line in stripped.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = _github_heading_anchor(match.group(1))
        if not base:
            continue
        count = heading_counts.get(base, 0)
        heading_counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    for match in re.finditer(
        r"<a\s+[^>]*(?:id|name)=['\"]([^'\"]+)['\"]",
        stripped,
        flags=re.IGNORECASE,
    ):
        anchors.add(match.group(1).strip().lower())
    return anchors


def _github_heading_anchor(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = html.unescape(text).strip().lower()
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def _read_text_inside_root(path: Path, root: Path) -> str | None:
    if not is_inside_root(path, root) or not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _score(name: str, checks: list[CheckResult]) -> DomainScore:
    passed = sum(1 for check in checks if check.passed)
    total = len(checks)
    if total == 0:
        score = 0
    elif passed == total:
        score = 5
    else:
        score = max(1, (passed * 5) // total)
    return DomainScore(
        name=name,
        score=score,
        passed=passed,
        total=total,
        checks=tuple(checks),
    )


def _instruction_checks(files: dict[str, str]) -> list[CheckResult]:
    instruction = files.get("AGENTS.md") or files.get("CLAUDE.md") or ""
    return [
        _check(bool(instruction), "Root agent instruction file exists"),
        _contains(instruction, ("Startup", "Before writing code"), "Startup path is documented"),
        _contains(instruction, ("Definition Of Done", "Definition of Done", "done only when"), "Definition of done is explicit"),
        _contains(instruction, ("init.sh", "init.ps1", "Verification"), "Verification route is discoverable"),
        _contains(instruction, ("feature_list.json", "progress.md"), "State files are routed from instructions"),
        _check(_line_count(instruction) <= 300 if instruction else False, "Instruction file is short enough to act as a map", f"{_line_count(instruction)} lines"),
    ]


def _tool_checks(files: dict[str, str]) -> list[CheckResult]:
    init_sh = files.get("init.sh", "")
    init_ps1 = files.get("init.ps1", "")
    all_text = "\n".join(files.values())
    return [
        _check("init.sh" in files, "POSIX verification entrypoint exists"),
        _check("init.ps1" in files, "PowerShell verification entrypoint exists"),
        _check("scripts/check_pins.py" in files, "Pin check script exists"),
        _contains(init_sh, ("set -e", "set -euo pipefail"), "POSIX entrypoint fails fast"),
        _contains(init_ps1, ("$ErrorActionPreference = 'Stop'",), "PowerShell entrypoint fails fast"),
        _contains(all_text, ("destructive", "--force", "overwrite"), "Tool safety and overwrite behavior are documented"),
        _contains(all_text, ("40-char SHA", "commit SHA", "exact pins"), "Dependency and Action pin policy is documented"),
    ]


def _environment_checks(files: dict[str, str]) -> list[CheckResult]:
    runtime_files = (
        "pyproject.toml",
        "package.json",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "global.json",
        "composer.json",
        "Gemfile",
        ".python-version",
        ".nvmrc",
        ".tool-versions",
        "Dockerfile",
        ".devcontainer/devcontainer.json",
    )
    manifest_text = files.get("docs/harness/manifest.json", "")
    explicit_generic_profile = '"detectedStack": "generic"' in manifest_text
    environment_text = "\n".join(
        files.get(name, "")
        for name in (
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "action.yml",
            "docs/action.md",
            "pyproject.toml",
            ".github/workflows/ci.yml",
            ".github/workflows/harness-self-heal.yml",
            "docs/harness/README.md",
            "docs/harness/component-inventory.md",
            "docs/harness/manifest.json",
            "docs/harness/dependency-change-policy.md",
        )
    )
    return [
        _check(
            any(name in files for name in runtime_files) or explicit_generic_profile,
            "Runtime manifest or explicit generic profile is discoverable",
        ),
        _contains(environment_text, ("Python 3.13", "python 3.13"), "Python 3.13+ floor is documented"),
        _contains_all(environment_text, ("macOS 15", "Windows 11", "Ubuntu 22.04"), "Supported OS floor is documented"),
        _contains(environment_text, ("pathlib", "cross-platform", "PowerShell"), "Cross-platform handling is called out"),
        _check("docs/harness/component-inventory.md" in files, "Component inventory exists"),
        _check("docs/harness/manifest.json" in files, "Machine-readable harness manifest exists"),
    ]


def _state_checks(files: dict[str, str]) -> list[CheckResult]:
    feature = files.get("feature_list.json") or files.get("feature-list.json") or ""
    privacy = files.get("docs/harness/feature-privacy-labels.json", "")
    progress = files.get("progress.md", "")
    handoff = files.get("session-handoff.md", "")
    return [
        _check(bool(feature), "Feature state file exists"),
        _check(_valid_feature_list(feature), "Feature state JSON has usable feature records"),
        _check(_feature_list_has_gates(feature), "Feature records include behavior, verification, state, and evidence"),
        _check(_feature_list_has_one_active(feature), "Feature state allows at most one active item"),
        _check(_valid_privacy_labels(privacy), "Feature privacy labels are machine-readable"),
        _check(bool(progress), "Progress file exists"),
        _contains_all(progress, ("Last Updated", "Current Objective", "Recommended Next Step"), "Progress file supports restart"),
        _contains_all(handoff or progress, ("Blockers", "Files", "Next Session"), "Handoff captures blockers, files, and next step"),
    ]


def _feedback_checks(files: dict[str, str], link_failures: list[str]) -> list[CheckResult]:
    all_text = "\n".join(files.values())
    init_text = files.get("init.sh", "") + files.get("init.ps1", "")
    return [
        _contains(init_text, ("test", "unittest", "pytest", "cargo test", "go test", "dotnet test", "build", "compileall"), "Runnable verification command is present"),
        _check("docs/harness/verification-matrix.md" in files, "Verification matrix exists"),
        _check("docs/harness/evidence-log.md" in files, "Evidence log exists"),
        _check("docs/harness/evaluator-rubric.md" in files, "Evaluator rubric exists for output review"),
        _contains(all_text, ("Verification Evidence", "Evidence", "command output"), "Evidence recording is requested"),
        _contains(all_text, ("audit", "assess", "score"), "Regular assessment loop is documented"),
        _contains_all(
            all_text,
            ("local checks", "push", "remote CI"),
            "Remote CI cost control is documented",
        ),
        _check(not link_failures, "Local Markdown links resolve", "; ".join(link_failures[:3])),
        _check(".github/workflows/ci.yml" in files or "init.sh" in files, "At least one local or CI feedback entrypoint exists"),
    ]


def _scope_checks(
    files: dict[str, str],
    local_path_failures: list[str],
    *,
    allow_local_absolute_paths: bool,
) -> list[CheckResult]:
    contract = files.get("docs/harness/change-contract.md", "")
    feature = files.get("feature_list.json") or files.get("feature-list.json") or ""
    all_text = "\n".join(files.values())
    local_path_detail = (
        "explicitly allowed for this audit"
        if allow_local_absolute_paths
        else "; ".join(local_path_failures[:3])
    )
    return [
        _check(bool(contract), "Change contract exists"),
        _check("docs/harness/security-boundary-map.md" in files, "Security boundary map exists"),
        _check("docs/harness/dependency-change-policy.md" in files, "Dependency change policy exists"),
        _contains(all_text, ("personal machines", "security wins"), "Personal-machine trust boundary is documented"),
        _contains_all(
            all_text,
            ("prompt injection", "data poisoning", "untrusted"),
            "Prompt-injection and data-poisoning boundary is documented",
        ),
        _contains_all(
            all_text,
            ("least privilege", "human approval", "cost-incurring"),
            "Agent tool approval boundary is documented",
        ),
        _contains_all(
            all_text,
            ("intentionally vulnerable", "risk", "product defects"),
            "Intentional vulnerability fixture boundary is documented",
        ),
        _contains_all(
            all_text,
            ("threat model", "AI/RAG/agent", "evidence"),
            "AI/agent threat-model evidence loop is documented",
        ),
        _check(
            allow_local_absolute_paths or not local_path_failures,
            "Durable harness text avoids local absolute paths",
            local_path_detail,
        ),
        _contains(contract, ("Problem", "Scope", "Non-goals"), "Change contract captures scope"),
        _contains(contract, ("Acceptance Criteria", "Acceptance criteria"), "Acceptance criteria are explicit"),
        _contains_all(contract, ("Verification", "Rollback"), "Verification and rollback are captured"),
        _contains(feature + all_text, ("dependencies", "one objective", "one feature", "Current Objective"), "Work dependencies or one-objective rule are present"),
    ]


def _lifecycle_checks(files: dict[str, str]) -> list[CheckResult]:
    handoff = files.get("session-handoff.md", "")
    instructions = files.get("AGENTS.md") or files.get("CLAUDE.md") or ""
    lifecycle_text = "\n".join(
        files.get(name, "")
        for name in (
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "progress.md",
            "session-handoff.md",
            "docs/harness/README.md",
            "docs/harness/clean-state-checklist.md",
            "docs/harness/entropy-control.md",
            "docs/harness/quality-document.md",
            "docs/harness/self-healing.md",
            "docs/harness/research-inbox.md",
        )
    )
    return [
        _check(bool(handoff), "Session handoff file exists"),
        _contains(instructions, ("End Of Session", "End of Session", "Before ending"), "End-of-session routine is documented"),
        _contains(lifecycle_text, ("restart", "restartable", "Next Session"), "Clean restart path is documented"),
        _check("docs/harness/clean-state-checklist.md" in files, "Clean-state checklist exists"),
        _check("docs/harness/quality-document.md" in files, "Quality document exists for periodic reassessment"),
        _contains_all(
            files.get("docs/harness/release-controls.md", ""),
            ("Release Controls", "SBOM", "provenance", "Rollback"),
            "Release controls are documented",
        ),
        _check("docs/harness/self-healing.md" in files, "Self-healing loop is documented"),
        _check("docs/harness/research-sources.json" in files, "Research source list exists"),
        _check("docs/harness/entropy-control.md" in files, "Harness drift or entropy control doc exists"),
        _contains(lifecycle_text, ("update", "correction", "regular assessment", "audit"), "Ongoing update loop is documented"),
    ]


def _recommendations(
    domains: tuple[DomainScore, ...],
    manifest_failures: list[str],
    link_failures: list[str],
    local_path_failures: list[str],
) -> tuple[str, ...]:
    recs: list[str] = []
    for domain in sorted(domains, key=lambda item: item.score):
        failures = [check for check in domain.checks if not check.passed]
        if failures:
            recs.append(f"Improve {domain.name}: {failures[0].message}.")
        if len(recs) >= 3:
            break
    if manifest_failures:
        recs.append("Resolve manifest failures so local policy matches actual files.")
    if link_failures:
        recs.append("Fix local Markdown links so harness docs remain navigable.")
    if local_path_failures:
        recs.append(
            "Remove local absolute paths from durable harness text or rerun audit "
            "with an explicit override."
        )
    return tuple(recs)


def _check(passed: bool, message: str, detail: str = "") -> CheckResult:
    return CheckResult(passed=bool(passed), message=message, detail=detail)


def _contains(text: str, needles: tuple[str, ...], message: str) -> CheckResult:
    lower = text.lower()
    passed = any(needle.lower() in lower for needle in needles)
    return _check(passed, message)


def _contains_all(text: str, needles: tuple[str, ...], message: str) -> CheckResult:
    lower = text.lower()
    passed = all(needle.lower() in lower for needle in needles)
    return _check(passed, message)


def _line_count(text: str) -> int:
    return 0 if not text else len(text.splitlines())


def _feature_records(text: str) -> list[dict[str, Any]] | None:
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    features = parsed.get("features") if isinstance(parsed, dict) else None
    if not isinstance(features, list):
        return None
    if not all(isinstance(feature, dict) for feature in features):
        return None
    return features


def _valid_feature_list(text: str) -> bool:
    features = _feature_records(text)
    if not features:
        return False
    return all(
        isinstance(feature.get("id"), str)
        and isinstance(_feature_title(feature), str)
        and isinstance(_feature_behavior(feature), str)
        and isinstance(feature.get("status"), str)
        and isinstance(feature.get("dependencies", []), list)
        for feature in features
    )


def _feature_list_has_gates(text: str) -> bool:
    features = _feature_records(text)
    if not features:
        return False
    return all(
        isinstance(_feature_behavior(feature), str)
        and _has_verification(feature)
        and isinstance(feature.get("status"), str)
        and "evidence" in feature
        and _passing_has_evidence(feature)
        for feature in features
    )


def _feature_list_has_one_active(text: str) -> bool:
    features = _feature_records(text)
    if not features:
        return False
    statuses = [str(feature.get("status", "")).lower() for feature in features]
    allowed = {"not_started", "active", "in_progress", "blocked", "passing", "planned", "done"}
    if any(status not in allowed for status in statuses):
        return False
    return sum(1 for status in statuses if status in {"active", "in_progress"}) <= 1


def _valid_privacy_labels(text: str) -> bool:
    if not text:
        return False
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return False
    if not isinstance(parsed, dict):
        return False
    labels = parsed.get("labels")
    features = parsed.get("features")
    if not isinstance(labels, list) or not isinstance(features, list):
        return False
    required = {"Local only", "External AI optional", "Sensitive", "Public-data only"}
    if not required.issubset({label for label in labels if isinstance(label, str)}):
        return False
    return all(
        isinstance(feature, dict)
        and isinstance(feature.get("id"), str)
        and isinstance(feature.get("name"), str)
        and isinstance(feature.get("labels"), list)
        and isinstance(feature.get("externalAi"), dict)
        for feature in features
    )


def _feature_title(feature: dict[str, Any]) -> Any:
    return feature.get("title") or feature.get("name")


def _feature_behavior(feature: dict[str, Any]) -> Any:
    return (
        feature.get("user_visible_behavior")
        or feature.get("behavior")
        or feature.get("description")
    )


def _has_verification(feature: dict[str, Any]) -> bool:
    verification = feature.get("verification")
    if isinstance(verification, str):
        return bool(verification.strip())
    if isinstance(verification, list):
        return bool(verification) and all(isinstance(item, str) for item in verification)
    acceptance = feature.get("acceptance")
    return bool(acceptance) and isinstance(acceptance, list)


def _passing_has_evidence(feature: dict[str, Any]) -> bool:
    status = str(feature.get("status", "")).lower()
    if status not in {"passing", "done"}:
        return True
    evidence = feature.get("evidence")
    if isinstance(evidence, str):
        return bool(evidence.strip())
    if isinstance(evidence, list):
        return bool(evidence)
    return False
