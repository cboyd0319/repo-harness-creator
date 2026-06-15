from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audit import audit_target
from .detect import MISSING_VERIFICATION_COMMAND, detect_project
from .generate import create_harness
from .indexer import build_index_report

SCHEMA_VERSION = "harnessforge.publicRepoCorpus.v1"
SOURCE_REVIEW_DATE = "2026-06-15"
REQUIRED_CATEGORIES = (
    "python-package",
    "typescript-app",
    "go-service",
    "rust-cli",
    "jvm-project",
    "dotnet-project",
    "swift-package",
    "c-cpp-project",
    "container-heavy",
    "monorepo",
    "docs-research",
    "spec-driven",
    "security-sensitive",
)
LOCAL_ABSOLUTE_PATH_RE = re.compile(
    r"/Users/|/home/[A-Za-z0-9_.-]+|C:\\Users\\", re.IGNORECASE
)
GENERATED_TEXT_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    "docs/harness/README.md",
    "docs/harness/component-inventory.md",
    "docs/harness/quality-document.md",
)


@dataclass(frozen=True)
class FixtureFile:
    path: str
    content: str


@dataclass(frozen=True)
class PublicRepoFixture:
    id: str
    repository: str
    url: str
    pinned_ref: str
    categories: tuple[str, ...]
    expected_stack: str
    expected_languages: tuple[str, ...]
    expected_package_managers: tuple[str, ...]
    expected_runtime_files: tuple[str, ...]
    expected_workspace_markers: tuple[str, ...]
    expected_routing_markers: tuple[str, ...]
    expected_component_paths: tuple[str, ...]
    expected_source_of_truth: tuple[str, ...]
    expected_verification_fragments: tuple[str, ...]
    files: tuple[FixtureFile, ...]
    rationale: str


PUBLIC_REPO_CORPUS: tuple[PublicRepoFixture, ...] = (
    PublicRepoFixture(
        id="pallets-flask",
        repository="pallets/flask",
        url="https://github.com/pallets/flask",
        pinned_ref="36e4a824f340fdee7ed50937ba8e7f6bc7d17f81",
        categories=("python-package",),
        expected_stack="python",
        expected_languages=("python",),
        expected_package_managers=(),
        expected_runtime_files=("pyproject.toml",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("python -m compileall .", "python -m pytest"),
        files=(
            FixtureFile(
                "pyproject.toml",
                "[project]\n"
                "name = 'flask'\n"
                "\n"
                "[tool.pytest.ini_options]\n"
                "testpaths = ['tests']\n",
            ),
            FixtureFile("src/flask/__init__.py", "__version__ = 'fixture'\n"),
            FixtureFile("tests/test_basic.py", "def test_fixture():\n    assert True\n"),
            FixtureFile("README.md", "# Flask\n\nPython web framework.\n"),
            FixtureFile("docs/index.rst", "Flask documentation\n===================\n"),
        ),
        rationale="Python package with docs and pytest metadata.",
    ),
    PublicRepoFixture(
        id="vercel-next-js",
        repository="vercel/next.js",
        url="https://github.com/vercel/next.js",
        pinned_ref="83852116ae9e8a9d0a3c50e333ee4c33fb0cb24c",
        categories=("typescript-app", "monorepo"),
        expected_stack="typescript-react",
        expected_languages=("javascript", "typescript"),
        expected_package_managers=("pnpm",),
        expected_runtime_files=("package.json", "pnpm-workspace.yaml", "tsconfig.json"),
        expected_workspace_markers=("package.json workspaces", "pnpm-workspace.yaml"),
        expected_routing_markers=(),
        expected_component_paths=(".", "packages/next"),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("pnpm run lint", "pnpm run test"),
        files=(
            FixtureFile(
                "package.json",
                "{\n"
                '  "name": "next",\n'
                '  "packageManager": "pnpm@10.0.0",\n'
                '  "workspaces": ["packages/*", "examples/*"],\n'
                '  "scripts": {"lint": "eslint .", "test": "node test.js"} ,\n'
                '  "dependencies": {"next": "canary", "react": "latest"}\n'
                "}\n",
            ),
            FixtureFile("pnpm-workspace.yaml", "packages:\n  - packages/*\n"),
            FixtureFile("tsconfig.json", '{"compilerOptions": {"strict": true}}\n'),
            FixtureFile("app/page.tsx", "export default function Page() { return null }\n"),
            FixtureFile(
                "packages/next/package.json",
                '{"name": "next", "scripts": {"test": "node test.js"}}\n',
            ),
            FixtureFile("packages/next/src/server.ts", "export const server = true\n"),
            FixtureFile("README.md", "# Next.js\n\nReact framework.\n"),
        ),
        rationale="TypeScript React monorepo with package-manager precedence.",
    ),
    PublicRepoFixture(
        id="prometheus-prometheus",
        repository="prometheus/prometheus",
        url="https://github.com/prometheus/prometheus",
        pinned_ref="121eaa1778f363ebde6a3613143885fc8d654332",
        categories=("go-service",),
        expected_stack="go",
        expected_languages=("go",),
        expected_package_managers=("go",),
        expected_runtime_files=("go.mod",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("make test", "go test ./..."),
        files=(
            FixtureFile("go.mod", "module github.com/prometheus/prometheus\n\ngo 1.24\n"),
            FixtureFile("cmd/prometheus/main.go", "package main\n\nfunc main() {}\n"),
            FixtureFile("Makefile", "test:\n\t@go test ./...\n"),
            FixtureFile("README.md", "# Prometheus\n\nMonitoring system.\n"),
        ),
        rationale="Go service with Makefile and module verification signals.",
    ),
    PublicRepoFixture(
        id="sharkdp-bat",
        repository="sharkdp/bat",
        url="https://github.com/sharkdp/bat",
        pinned_ref="af1f53d9a977154216d01435991fe33631b74713",
        categories=("rust-cli",),
        expected_stack="rust",
        expected_languages=("rust",),
        expected_package_managers=("cargo",),
        expected_runtime_files=("Cargo.toml",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("cargo fmt", "cargo clippy", "cargo test"),
        files=(
            FixtureFile(
                "Cargo.toml",
                "[package]\nname = 'bat'\nversion = '0.0.0'\nedition = '2024'\n",
            ),
            FixtureFile(
                "rust-toolchain.toml",
                "[toolchain]\ncomponents = ['rustfmt', 'clippy']\n",
            ),
            FixtureFile("src/main.rs", "fn main() {}\n"),
            FixtureFile("tests/cli.rs", "#[test]\nfn fixture() { assert!(true); }\n"),
            FixtureFile("README.md", "# bat\n\nRust command-line tool.\n"),
        ),
        rationale="Rust CLI with rustfmt, clippy, and test expectations.",
    ),
    PublicRepoFixture(
        id="spring-petclinic",
        repository="spring-projects/spring-petclinic",
        url="https://github.com/spring-projects/spring-petclinic",
        pinned_ref="a2c2ef994340d3970eb6db51247456a51bb161f8",
        categories=("jvm-project",),
        expected_stack="java",
        expected_languages=("java",),
        expected_package_managers=("maven",),
        expected_runtime_files=("pom.xml",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("mvn test",),
        files=(
            FixtureFile(
                "pom.xml",
                "<project><modelVersion>4.0.0</modelVersion>"
                "<groupId>org.springframework.samples</groupId>"
                "<artifactId>spring-petclinic</artifactId>"
                "<version>0.0.0</version></project>\n",
            ),
            FixtureFile(
                "src/main/java/org/example/App.java",
                "package org.example; public class App {}\n",
            ),
            FixtureFile("README.md", "# Spring PetClinic\n\nJVM sample app.\n"),
        ),
        rationale="Maven/JVM project with root build contract.",
    ),
    PublicRepoFixture(
        id="dotnet-aspnetcore",
        repository="dotnet/aspnetcore",
        url="https://github.com/dotnet/aspnetcore",
        pinned_ref="aa5493528640932601bb82ef3295e4d8ca7e11c5",
        categories=("dotnet-project", "monorepo"),
        expected_stack="dotnet",
        expected_languages=("dotnet",),
        expected_package_managers=(),
        expected_runtime_files=("global.json",),
        expected_workspace_markers=("multiple nested component manifests",),
        expected_routing_markers=(),
        expected_component_paths=(".", "src/Http", "src/Mvc"),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("dotnet test",),
        files=(
            FixtureFile("aspnetcore.slnx", "<Solution></Solution>\n"),
            FixtureFile("global.json", '{"sdk": {"version": "10.0.100"}}\n'),
            FixtureFile(
                "src/Http/Http.csproj",
                "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
            ),
            FixtureFile(
                "src/Mvc/Mvc.csproj",
                "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
            ),
            FixtureFile("README.md", "# ASP.NET Core\n\n.NET platform repo.\n"),
        ),
        rationale=".NET repository with nested project boundaries.",
    ),
    PublicRepoFixture(
        id="apple-swift-nio",
        repository="apple/swift-nio",
        url="https://github.com/apple/swift-nio",
        pinned_ref="3263350c88b44704a90b4d9bc0fda4828d470df5",
        categories=("swift-package",),
        expected_stack="swift",
        expected_languages=("swift",),
        expected_package_managers=("swiftpm",),
        expected_runtime_files=("Package.swift",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("swift test",),
        files=(
            FixtureFile(
                "Package.swift",
                "// swift-tools-version:6.0\n"
                "import PackageDescription\n"
                "let package = Package(name: \"NIO\", targets: [])\n",
            ),
            FixtureFile("Sources/NIO/EventLoop.swift", "public struct EventLoop {}\n"),
            FixtureFile("Tests/NIOTests/EventLoopTests.swift", "import Testing\n"),
            FixtureFile("README.md", "# SwiftNIO\n\nSwift server framework.\n"),
        ),
        rationale="Swift Package Manager project with test target.",
    ),
    PublicRepoFixture(
        id="curl-curl",
        repository="curl/curl",
        url="https://github.com/curl/curl",
        pinned_ref="5687d211c48b38facb9e77c59b233dc25dadb330",
        categories=("c-cpp-project",),
        expected_stack="cpp",
        expected_languages=("cpp",),
        expected_package_managers=(),
        expected_runtime_files=("Makefile",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("make check", "make test"),
        files=(
            FixtureFile("Makefile", "check:\n\t@true\n\ntest:\n\t@true\n"),
            FixtureFile("src/tool_main.c", "int main(void) { return 0; }\n"),
            FixtureFile("include/curl/curl.h", "#pragma once\n"),
            FixtureFile("README.md", "# curl\n\nC command-line project.\n"),
        ),
        rationale="C project with Makefile checks.",
    ),
    PublicRepoFixture(
        id="devcontainers-templates",
        repository="devcontainers/templates",
        url="https://github.com/devcontainers/templates",
        pinned_ref="95f7406a57fc5f0798964a5853c5ac04added322",
        categories=("container-heavy", "typescript-app"),
        expected_stack="node",
        expected_languages=("javascript",),
        expected_package_managers=("npm",),
        expected_runtime_files=("package.json", ".devcontainer/devcontainer.json"),
        expected_workspace_markers=(),
        expected_routing_markers=(".devcontainer",),
        expected_component_paths=(".",),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=("npm test",),
        files=(
            FixtureFile(
                "package.json",
                '{"name": "devcontainer-templates", "scripts": {"test": "node test.js"}}\n',
            ),
            FixtureFile(
                ".devcontainer/devcontainer.json",
                '{"name": "templates", "image": "mcr.microsoft.com/devcontainers/base"}\n',
            ),
            FixtureFile(
                "src/debian/devcontainer-template.json",
                '{"id": "debian", "name": "Debian"}\n',
            ),
            FixtureFile("test.js", "process.exit(0)\n"),
            FixtureFile("README.md", "# Dev Container Templates\n"),
        ),
        rationale="Container-oriented repository with devcontainer routing.",
    ),
    PublicRepoFixture(
        id="kubernetes-kubernetes",
        repository="kubernetes/kubernetes",
        url="https://github.com/kubernetes/kubernetes",
        pinned_ref="82c23b419e779e02128f1ee38dff923dd687f19f",
        categories=("go-service", "monorepo", "security-sensitive", "container-heavy"),
        expected_stack="go",
        expected_languages=("go",),
        expected_package_managers=("go",),
        expected_runtime_files=("go.mod", "go.work", "Makefile", "Dockerfile"),
        expected_workspace_markers=("go.work", "multiple nested component manifests"),
        expected_routing_markers=(),
        expected_component_paths=(".", "cmd/kube-apiserver", "staging/src/k8s.io/api"),
        expected_source_of_truth=("README.md", "docs/security.md"),
        expected_verification_fragments=("make test", "go test ./..."),
        files=(
            FixtureFile("go.mod", "module k8s.io/kubernetes\n\ngo 1.24\n"),
            FixtureFile(
                "go.work",
                "go 1.24\n\nuse (\n  .\n  ./staging/src/k8s.io/api\n)\n",
            ),
            FixtureFile("cmd/kube-apiserver/go.mod", "module k8s.io/apiserver\n\ngo 1.24\n"),
            FixtureFile("cmd/kube-apiserver/main.go", "package main\n\nfunc main() {}\n"),
            FixtureFile("staging/src/k8s.io/api/go.mod", "module k8s.io/api\n\ngo 1.24\n"),
            FixtureFile("staging/src/k8s.io/api/types.go", "package api\n"),
            FixtureFile("Makefile", "test:\n\t@go test ./...\n"),
            FixtureFile("Dockerfile", "FROM scratch\n"),
            FixtureFile("docs/security.md", "# Security\n\nSecurity reporting.\n"),
            FixtureFile("README.md", "# Kubernetes\n\nContainer orchestration.\n"),
        ),
        rationale="Large Go monorepo with security and container boundaries.",
    ),
    PublicRepoFixture(
        id="rust-lang-rfcs",
        repository="rust-lang/rfcs",
        url="https://github.com/rust-lang/rfcs",
        pinned_ref="7160a96b584ddd8b80128d90f0cf41b0eaa26a3e",
        categories=("docs-research",),
        expected_stack="docs",
        expected_languages=("docs",),
        expected_package_managers=(),
        expected_runtime_files=(),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(),
        expected_source_of_truth=("README.md",),
        expected_verification_fragments=(MISSING_VERIFICATION_COMMAND,),
        files=(
            FixtureFile("README.md", "# RFCs\n\nDesign process.\n"),
            FixtureFile("text/0000-template.md", "# RFC Template\n"),
            FixtureFile("text/0001-example.md", "# Example RFC\n"),
            FixtureFile("CONTRIBUTING.md", "# Contributing\n"),
        ),
        rationale="Docs and design-process repo with no runnable check detected.",
    ),
    PublicRepoFixture(
        id="github-spec-kit",
        repository="github/spec-kit",
        url="https://github.com/github/spec-kit",
        pinned_ref="1b0556c711b633a6d50b2e2f5f8db0e6717489d3",
        categories=("spec-driven", "python-package"),
        expected_stack="python",
        expected_languages=("python", "docs"),
        expected_package_managers=(),
        expected_runtime_files=("pyproject.toml",),
        expected_workspace_markers=("structured project specs", "Spec Kit SDD"),
        expected_routing_markers=("structured project specs", "Spec Kit SDD"),
        expected_component_paths=(".",),
        expected_source_of_truth=(".specify/memory/constitution.md", "specs/001-demo/spec.md"),
        expected_verification_fragments=("python -m compileall .", "python -m pytest"),
        files=(
            FixtureFile(
                "pyproject.toml",
                "[project]\nname = 'spec-kit'\n\n[tool.pytest.ini_options]\ntestpaths = ['tests']\n",
            ),
            FixtureFile("src/spec_kit/__init__.py", "VALUE = 1\n"),
            FixtureFile("tests/test_cli.py", "def test_fixture():\n    assert True\n"),
            FixtureFile(
                ".specify/feature.json",
                '{"feature_directory": "specs/001-demo"}\n',
            ),
            FixtureFile(
                ".specify/memory/constitution.md",
                "# Constitution\n\nProject principles.\n",
            ),
            FixtureFile("specs/001-demo/spec.md", "# Spec\n\n## Requirements\n- FR-001: Demo.\n"),
            FixtureFile("specs/001-demo/plan.md", "# Plan\n\nImplementation plan.\n"),
            FixtureFile("specs/001-demo/tasks.md", "# Tasks\n\n- [ ] T001 Build demo.\n"),
            FixtureFile("README.md", "# Spec Kit\n\nSpec-driven development toolkit.\n"),
        ),
        rationale="Spec-driven repo with .specify and active feature state.",
    ),
    PublicRepoFixture(
        id="owasp-cheatsheetseries",
        repository="OWASP/CheatSheetSeries",
        url="https://github.com/OWASP/CheatSheetSeries",
        pinned_ref="bebeb7061cc046ee8ba1557d42fe23b418cfee26",
        categories=("docs-research", "security-sensitive"),
        expected_stack="docs",
        expected_languages=("docs",),
        expected_package_managers=(),
        expected_runtime_files=("Makefile",),
        expected_workspace_markers=(),
        expected_routing_markers=(),
        expected_component_paths=(".",),
        expected_source_of_truth=("docs/security.md", "README.md"),
        expected_verification_fragments=("make validate",),
        files=(
            FixtureFile("Makefile", "validate:\n\t@true\n"),
            FixtureFile("mkdocs.yml", "site_name: OWASP Cheat Sheet Series\n"),
            FixtureFile("README.md", "# OWASP Cheat Sheet Series\n"),
            FixtureFile("docs/security.md", "# Security\n\nSecurity guidance.\n"),
            FixtureFile("cheatsheets/Authentication_Cheat_Sheet.md", "# Authentication\n"),
            FixtureFile("cheatsheets/Input_Validation_Cheat_Sheet.md", "# Input Validation\n"),
        ),
        rationale="Security-sensitive docs repo with explicit validation target.",
    ),
)


def build_public_repo_corpus_report() -> dict[str, Any]:
    fixtures = [_assess_fixture(fixture) for fixture in PUBLIC_REPO_CORPUS]
    categories = sorted({category for fixture in PUBLIC_REPO_CORPUS for category in fixture.categories})
    missing_categories = [
        category for category in REQUIRED_CATEGORIES if category not in categories
    ]
    scores = [fixture["quality"]["score"] for fixture in fixtures]
    failing = [
        fixture
        for fixture in fixtures
        if fixture["quality"]["score"] < 90 or fixture["quality"]["failedChecks"]
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "offline_fixture_quality",
        "sourceReview": {
            "reviewedAt": SOURCE_REVIEW_DATE,
            "pinSource": "git ls-remote <repository> HEAD",
            "networkRequiredForNormalCheck": False,
        },
        "execution": {
            "networkAccess": False,
            "targetWritesPerformed": False,
            "commandsExecuted": False,
            "temporaryFixtureWritesPerformed": True,
        },
        "summary": {
            "fixtures": len(fixtures),
            "minimumScore": min(scores) if scores else 0,
            "averageScore": round(sum(scores) / len(scores), 1) if scores else 0.0,
            "failingFixtures": len(failing),
        },
        "coverage": {
            "requiredCategories": list(REQUIRED_CATEGORIES),
            "categories": categories,
            "missingCategories": missing_categories,
        },
        "fixtures": fixtures,
    }


def format_public_repo_corpus_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    coverage = payload["coverage"]
    lines = [
        "Public repo quality corpus",
        "Mode: offline fixture quality",
        f"Fixtures: {summary['fixtures']}",
        f"Minimum score: {summary['minimumScore']}",
        f"Average score: {summary['averageScore']}",
        f"Failing fixtures: {summary['failingFixtures']}",
        "Missing categories: "
        + (", ".join(coverage["missingCategories"]) or "none"),
        "",
        "Fixtures:",
    ]
    for fixture in payload["fixtures"]:
        categories = ", ".join(fixture["categories"])
        lines.append(
            f"  - {fixture['id']}: {fixture['quality']['score']} "
            f"({fixture['detectedStack']}; {categories})"
        )
        if fixture["quality"]["failedChecks"]:
            lines.append(
                "    failed checks: "
                + ", ".join(fixture["quality"]["failedChecks"])
            )
    return "\n".join(lines) + "\n"


def _assess_fixture(fixture: PublicRepoFixture) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="harnessforge-corpus-") as tmp:
        root = Path(tmp) / fixture.id
        root.mkdir()
        _write_fixture_files(root, fixture.files)
        profile = detect_project(root)
        index = build_index_report(profile)
        _, writes = create_harness(root)
        audit = audit_target(root)
        generated_text = _read_generated_text(root)
        root_instruction_lines = _line_count(root / "AGENTS.md")

    commands = list(profile.verification_commands)
    source_paths = {item["path"] for item in index["sourceOfTruth"]}
    component_paths = {
        component.split(" (", 1)[0] for component in profile.components
    }
    checks = [
        _check(
            "expected_stack",
            profile.stack == fixture.expected_stack,
            f"expected {fixture.expected_stack}, detected {profile.stack}",
        ),
        _check_subset(
            "expected_languages",
            fixture.expected_languages,
            profile.languages,
        ),
        _check_subset(
            "expected_package_managers",
            fixture.expected_package_managers,
            profile.package_managers,
        ),
        _check_subset(
            "expected_runtime_files",
            fixture.expected_runtime_files,
            profile.runtime_files,
        ),
        _check_subset(
            "expected_workspace_markers",
            fixture.expected_workspace_markers,
            profile.workspace_markers,
        ),
        _check_subset(
            "expected_routing_markers",
            fixture.expected_routing_markers,
            profile.routing_markers,
        ),
        _check_subset(
            "expected_component_paths",
            fixture.expected_component_paths,
            tuple(sorted(component_paths)),
        ),
        _check_subset(
            "expected_source_of_truth",
            fixture.expected_source_of_truth,
            tuple(sorted(source_paths)),
        ),
        _check_verification_fragments(
            fixture.expected_verification_fragments,
            commands,
        ),
        _check(
            "harness_audit_high",
            audit.overall >= 90,
            f"audit score {audit.overall}",
        ),
        _check(
            "no_local_absolute_paths",
            LOCAL_ABSOLUTE_PATH_RE.search(generated_text) is None,
            "generated text contains a local absolute path",
        ),
        _check(
            "no_unrendered_template_tokens",
            "{{" not in generated_text and "}}" not in generated_text,
            "generated text contains an unrendered template token",
        ),
        _check(
            "specific_project_context",
            f"Detected stack: {fixture.expected_stack}" in generated_text
            and "Detected stack: generic" not in generated_text,
            "generated instructions do not carry the expected detected stack",
        ),
        _check(
            "root_instruction_within_budget",
            root_instruction_lines <= 240,
            "AGENTS.md exceeded root instruction budget",
        ),
        _check(
            "bounded_review_markers",
            generated_text.count("REVIEW REQUIRED") <= 90,
            "generated artifacts contain too many review markers",
        ),
        _check(
            "generated_files_written",
            any(write.status == "written" for write in writes),
            "harness generation did not write generated files",
        ),
    ]
    passed = sum(1 for check in checks if check["passed"])
    score = round((passed / len(checks)) * 100) if checks else 0
    failed_checks = [check["name"] for check in checks if not check["passed"]]
    return {
        "id": fixture.id,
        "repository": fixture.repository,
        "url": fixture.url,
        "pinnedRef": fixture.pinned_ref,
        "categories": list(fixture.categories),
        "rationale": fixture.rationale,
        "detectedStack": profile.stack,
        "detectedLanguages": list(profile.languages),
        "packageManagers": list(profile.package_managers),
        "verificationCommands": commands,
        "quality": {
            "score": score,
            "failedChecks": failed_checks,
            "checks": checks,
        },
    }


def _write_fixture_files(root: Path, files: tuple[FixtureFile, ...]) -> None:
    for item in files:
        relative = Path(item.path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"invalid corpus fixture path: {item.path}")
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item.content, encoding="utf-8", newline="\n")


def _read_generated_text(root: Path) -> str:
    chunks: list[str] = []
    for relative in GENERATED_TEXT_PATHS:
        path = root / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 9999


def _check(name: str, passed: bool, detail: str = "") -> dict[str, Any]:
    return {"name": name, "passed": passed, "detail": "" if passed else detail}


def _check_subset(
    name: str,
    expected: tuple[str, ...],
    actual: tuple[str, ...],
) -> dict[str, Any]:
    missing = [item for item in expected if item not in actual]
    return _check(
        name,
        not missing,
        "missing " + ", ".join(missing) if missing else "",
    )


def _check_verification_fragments(
    expected_fragments: tuple[str, ...],
    commands: list[str],
) -> dict[str, Any]:
    missing = [
        fragment
        for fragment in expected_fragments
        if not any(fragment in command for command in commands)
    ]
    return _check(
        "expected_verification_commands",
        not missing,
        "missing " + ", ".join(missing) if missing else "",
    )
