from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from harnessforge.cli import main


def _python_command(script: str) -> str:
    executable = "python" if os.name == "nt" else "python3"
    return f"{executable} -c {json.dumps(script)}"


def _write_verify_report(
    root: Path,
    relative_path: str,
    *,
    verdict: str = "passed",
    mode: str = "run",
    recorded_at: str = "2026-06-15T05:00:00Z",
    summary: dict[str, int] | None = None,
) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": "harnessforge.verify.v1",
        "target": {"name": "demo", "root": None},
        "mode": mode,
        "verdict": verdict,
        "platform": {"os": "darwin", "python": "3.14.6", "runner": "local"},
        "execution": {
            "commandsExecuted": mode == "run",
            "startedAt": recorded_at,
            "endedAt": recorded_at,
            "durationMs": 1.0,
        },
        "summary": summary
        or {
            "total": 1,
            "planned": 0,
            "skipped": 0,
            "blocked": 0,
            "passed": 1 if verdict == "passed" else 0,
            "failed": 1 if verdict == "failed" else 0,
            "timedOut": 0,
            "errors": 0,
        },
        "checks": [],
        "blockedReasons": [],
        "warnings": [],
        "artifacts": [],
    }
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return path


def _write_verify_summary(
    root: Path,
    relative_path: str,
    *,
    verdict: str = "passed",
    mode: str = "run",
    recorded_at: str = "2026-06-15T05:00:00Z",
) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": "harnessforge.verifySummary.v1",
        "target": {"name": "demo", "root": None},
        "mode": mode,
        "verdict": verdict,
        "recordedAt": recorded_at,
        "platform": {"os": "darwin", "python": "3.14.6", "runner": "local"},
        "execution": {
            "commandsExecuted": mode == "run",
            "startedAt": recorded_at,
            "endedAt": recorded_at,
            "durationMs": 1.0,
        },
        "summary": {
            "total": 1,
            "planned": 0,
            "skipped": 0,
            "blocked": 0,
            "passed": 1 if verdict == "passed" else 0,
            "failed": 1 if verdict == "failed" else 0,
            "timedOut": 0,
            "errors": 0,
        },
        "checks": [
            {
                "id": "project.explicit.0",
                "label": "Project verification",
                "command": "python -m unittest",
                "source": "explicit",
                "workingDirectory": ".",
                "required": True,
                "status": "passed" if verdict == "passed" else "failed",
                "exitCode": 0 if verdict == "passed" else 1,
                "durationMs": 1.0,
                "message": "Command passed." if verdict == "passed" else "Command failed.",
            }
        ],
        "blockedReasons": [],
        "warnings": [],
        "artifacts": [],
        "privacy": {
            "stdoutStderrCaptured": False,
            "outputPreviewPolicy": "omitted",
        },
    }
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return path


def _write_first_agent_review(
    root: Path,
    *,
    status: str = "completed",
    high_risk_surfaces: list[dict[str, str]] | None = None,
) -> Path:
    path = root / "docs/harness/evidence/first-agent-review.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": "harnessforge.firstAgentReview.v1",
        "status": status,
        "reviewedAt": "2026-06-15T05:00:00Z",
        "reviewedBy": ["maintainer"],
        "taskPath": "docs/harness/state/first-agent-task.md",
        "freshSession": {
            "purpose": "verified",
            "organization": "verified",
            "startup": "verified",
            "verification": "verified",
            "currentWork": "verified",
            "sourceOfTruth": "verified",
        },
        "updatedSurfaces": [
            "AGENTS.md",
            "docs/harness/feedback/verification-matrix.md",
        ],
        "verification": {
            "commands": ["python -m compileall ."],
            "evidenceRefs": ["docs/harness/evidence/verify-2026-06-15.json"],
        },
        "remainingReview": [],
        "retirement": {
            "taskRetired": True,
            "reason": "Project-specific harness guidance was accepted.",
        },
    }
    if high_risk_surfaces is not None:
        payload["highRiskSurfaceReview"] = {
            "status": "accepted_advisory",
            "reviewedAt": "2026-06-15T05:00:00Z",
            "surfaces": high_risk_surfaces,
            "evidenceRefs": [
                "docs/harness/boundaries/component-inventory.md",
                "docs/harness/evidence/evidence-log.md",
            ],
        }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_review_finalize_fixture(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        "[project]\nname='demo'\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
    (root / "AGENTS.md").write_text(
        "# AGENTS.md\n\n"
        "## Project overview\n"
        "This project is a Python repository with repo-owned harness docs.\n\n"
        "## Startup\n"
        "Read `README.md`, `feature_list.json`, and `current-state.md`.\n\n"
        "## Verification\n"
        "Run `python -m unittest discover -s tests` before completion.\n\n"
        "## Constraints\n"
        "Do not expose secrets. Preserve security boundaries and "
        "project docs.\n\n"
        "## State\n"
        "Use `current-state.md` and `docs/roadmap.md` for current work.\n\n"
        "## Routing\n"
        "See `docs/harness/README.md` for harness maintenance guidance.\n",
        encoding="utf-8",
    )
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\n"
        "on:\n"
        "  push:\n"
        "jobs:\n"
        "  test:\n"
        "    steps:\n"
        "      - run: python -m unittest discover -s tests\n"
        "        env:\n"
        "          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n",
        encoding="utf-8",
    )


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class CliTests(unittest.TestCase):
    def test_help_returns_zero(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--help"])

        self.assertEqual(code, 0)
        self.assertIn("harnessforge", stdout.getvalue())

    def test_missing_subcommand_returns_usage_error(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([])

        self.assertEqual(code, 2)
        self.assertIn("harnessforge", stdout.getvalue())

    def test_init_and_audit_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                init_code = main(["init", "--target", str(root)])
            with contextlib.redirect_stdout(io.StringIO()):
                audit_code = main(["audit", "--target", str(root), "--min-score", "85"])

        self.assertEqual(init_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertIn("Detected stack", stdout.getvalue())

    def test_init_force_requires_yes_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("# Existing\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                code = main(["init", "--target", str(root), "--force"])

            agents_text = agents.read_text(encoding="utf-8")

        self.assertEqual(code, 2)
        self.assertEqual(agents_text, "# Existing\n")
        self.assertIn("requires --yes", stderr.getvalue())

    def test_init_force_dry_run_does_not_require_yes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Existing\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--force",
                        "--dry-run",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["mode"], "dry_run")

    def test_inspect_command_reports_profile_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root)])

            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertIn("Detected stack: python", stdout.getvalue())
        self.assertIn("Verification commands:", stdout.getvalue())

    def test_inspect_json_reports_detected_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[workspace]\nmembers = ['crates/*']\n",
                encoding="utf-8",
            )
            (root / "justfile").write_text(
                "ci:\n\tcargo test --workspace\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["detectedStack"], "rust")
        self.assertIn("just", payload["packageManagers"])
        self.assertIn("just ci", payload["verificationCommands"])
        self.assertIn("justfile", payload["routingMarkers"])

    def test_index_json_reports_structural_repo_map_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Instructions\n\nStart here.\n",
                encoding="utf-8",
            )
            (root / "src" / "demo").mkdir(parents=True)
            (root / "src" / "demo" / "__init__.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            (root / "src" / "demo" / "README.md").write_text(
                "# Demo package\n",
                encoding="utf-8",
            )
            (root / "src" / "demo" / "generated_client.py").write_text(
                "# Generated by demo tool. DO NOT EDIT.\nVALUE = 2\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text(
                "import unittest\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir()
            (root / "docs" / "architecture.md").write_text(
                "# Architecture\n",
                encoding="utf-8",
            )
            (root / "docs" / "sbom.cdx.json").write_text(
                '{"bomFormat": "CycloneDX", "specVersion": "1.6"}\n',
                encoding="utf-8",
            )
            (root / "docs" / "harness" / "research").mkdir(parents=True)
            (
                root
                / "docs"
                / "harness"
                / "research"
                / "source-record-example.json"
            ).write_text(
                '{"review": "REVIEW REQUIRED"}\n',
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "name: CI\n",
                encoding="utf-8",
            )
            (root / "third_party" / "lib").mkdir(parents=True)
            (root / "third_party" / "lib" / "shim.js").write_text(
                "module.exports = {}\n",
                encoding="utf-8",
            )
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["index", "--target", str(root), "--json"])
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            raw_payload = stdout.getvalue()
            payload = json.loads(raw_payload)

        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        self.assertNotIn(str(root), raw_payload)
        self.assertEqual(payload["schemaVersion"], "harnessforge.index.v1")
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["detectedStack"], "python")
        self.assertEqual(
            payload["nestedInstructionPlan"]["schemaVersion"],
            "harnessforge.nestedInstructionPlan.v1",
        )
        self.assertEqual(payload["nestedInstructionPlan"]["status"], "no_action")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertFalse(payload["execution"]["writesPerformed"])
        self.assertGreaterEqual(payload["summary"]["fileCount"], 9)
        class_examples = {
            item["class"]: item["examples"] for item in payload["fileClasses"]
        }
        self.assertIn("src/demo/__init__.py", class_examples["source"])
        self.assertIn("tests/test_demo.py", class_examples["test"])
        self.assertIn("docs/architecture.md", class_examples["docs"])
        self.assertIn("src/demo/generated_client.py", class_examples["generated"])
        self.assertIn("third_party/lib/shim.js", class_examples["vendor"])
        self.assertIn(".github/workflows/ci.yml", class_examples["workflow"])
        self.assertIn("docs/sbom.cdx.json", class_examples["sbom"])
        self.assertIn("pyproject.toml", {item["path"] for item in payload["manifests"]})
        self.assertIn("AGENTS.md", {item["path"] for item in payload["sourceOfTruth"]})
        self.assertNotIn(
            "src/demo/README.md",
            {item["path"] for item in payload["sourceOfTruth"]},
        )
        self.assertIn(
            "src/demo/README.md",
            {item["path"] for item in payload["localDocs"]},
        )
        self.assertEqual(
            payload["repoMap"]["summary"]["localDocCount"],
            payload["summary"]["localDocCount"],
        )
        self.assertEqual(payload["summary"]["sbomCount"], 1)
        self.assertEqual(payload["sbom"][0]["format"], "cyclonedx")
        verification = payload["verificationCommands"]
        self.assertEqual(
            verification["schemaVersion"],
            "harnessforge.verificationCommands.v1",
        )
        self.assertGreaterEqual(verification["summary"]["commandCount"], 2)
        commands = {item["command"]: item for item in verification["commands"]}
        self.assertEqual(
            commands["python -m compileall ."]["sourcePath"],
            "pyproject.toml",
        )
        self.assertEqual(
            commands["python -m unittest discover"]["commandClass"],
            "test",
        )
        self.assertEqual(
            payload["repoMap"]["verification"]["schemaVersion"],
            "harnessforge.verificationCommands.v1",
        )
        self.assertEqual(
            payload["repoMap"]["verification"]["commands"][0]["sourceType"],
            "python-project",
        )
        self.assertEqual(payload["repoMap"]["summary"]["sbomCount"], 1)
        self.assertTrue(
            any(item["class"] == "sbom" for item in payload["repoMap"]["boundaries"])
        )
        self.assertIn("Structural map only", payload["repoMap"]["notes"][0])
        self.assertIn(
            "docs/harness/research/source-record-example.json",
            {item["path"] for item in payload["reviewRequired"]},
        )
        self.assertTrue(
            any(item["language"] == "python" for item in payload["languageBreakdown"])
        )

    def test_index_json_reports_nested_instruction_overflow_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "workspaces": ["packages/*"],
                        "scripts": {"test": "node --test"},
                    }
                ),
                encoding="utf-8",
            )
            for package in ("api", "web"):
                package_root = root / "packages" / package
                package_root.mkdir(parents=True)
                (package_root / "package.json").write_text(
                    json.dumps(
                        (
                            {
                                "name": package,
                                "scripts": {"test": "vitest"},
                            }
                            if package == "web"
                            else {"name": package}
                        )
                    ),
                    encoding="utf-8",
                )
            (root / "packages" / "web" / "README.md").write_text(
                "# Web\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "web.yml").write_text(
                "name: web\n"
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - packages/web/**\n"
                "jobs:\n"
                "  web:\n"
                "    defaults:\n"
                "      run:\n"
                "        working-directory: packages/web\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "index",
                        "--target",
                        str(root),
                        "--json",
                        "--component-limit",
                        "2",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        plan = payload["nestedInstructionPlan"]
        self.assertEqual(code, 0)
        self.assertEqual(plan["status"], "review_required")
        self.assertFalse(plan["writeByDefault"])
        self.assertEqual(plan["candidateCount"], 1)
        self.assertEqual(plan["candidateComponents"][0]["path"], "packages/api")
        self.assertEqual(plan["omittedCandidateCount"], 1)
        omitted = plan["omittedCandidateComponents"][0]
        self.assertEqual(omitted["path"], "packages/web")
        self.assertEqual(
            omitted["recommendedAction"],
            "raise_component_limit_or_review_manually",
        )
        self.assertIn(
            "verification source: packages/web/package.json",
            omitted["rankSignals"],
        )
        self.assertIn(
            "workflow routing: .github/workflows/web.yml",
            omitted["rankSignals"],
        )
        self.assertIn("Raise --component-limit", plan["omittedGuidance"])

    def test_index_json_accepts_explicit_file_scan_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(5):
                (root / f"doc-{index}.md").write_text("# Doc\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "index",
                        "--target",
                        str(root),
                        "--max-files",
                        "3",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["fileCount"], 3)
        self.assertTrue(payload["summary"]["truncated"])
        self.assertEqual(payload["limits"]["maxFiles"], 3)
        self.assertIn("3-file detection limit", " ".join(payload["warnings"]))

    def test_index_json_reports_git_tracked_file_coverage_when_scan_limited(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "package.json").write_text('{"scripts":{"test":"node --test"}}\n', encoding="utf-8")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_app.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
            _git(root, "init")
            _git(root, "add", ".")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "index",
                        "--target",
                        str(root),
                        "--max-files",
                        "3",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        coverage = payload["fileCoverage"]
        categories = {item["id"]: item for item in coverage["categories"]}
        self.assertEqual(code, 0)
        self.assertEqual(coverage["schemaVersion"], "harnessforge.fileCoverage.v1")
        self.assertEqual(coverage["inventorySource"], "git_tracked")
        self.assertEqual(coverage["fileScanLimit"], 3)
        self.assertEqual(coverage["scannedFileCount"], 3)
        self.assertEqual(coverage["totalFileCount"], 5)
        self.assertFalse(coverage["coverageComplete"])
        self.assertEqual(categories["runtime_manifests"]["totalFiles"], 1)
        self.assertEqual(categories["workflows"]["totalFiles"], 1)
        self.assertTrue(any(item["budgetLimited"] for item in coverage["categories"]))
        self.assertIn("budget-limited", "\n".join(payload["warnings"]))

    def test_index_json_distinguishes_intentionally_skipped_tracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "build").mkdir()
            (root / "build" / "package.json").write_text("{}\n", encoding="utf-8")
            try:
                os.symlink("README.md", root / "Makefile")
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            _git(root, "init")
            _git(root, "add", ".")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "index",
                        "--target",
                        str(root),
                        "--max-files",
                        "20",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        coverage = payload["fileCoverage"]
        categories = {item["id"]: item for item in coverage["categories"]}
        manifests = categories["runtime_manifests"]
        self.assertEqual(code, 0)
        self.assertTrue(coverage["coverageComplete"])
        self.assertEqual(coverage["scanEligibleFileCount"], 1)
        self.assertEqual(manifests["totalFiles"], 2)
        self.assertEqual(manifests["scanEligibleFiles"], 0)
        self.assertEqual(manifests["skippedFiles"], 2)
        self.assertFalse(manifests["budgetLimited"])
        self.assertEqual(
            {item["reason"] for item in manifests["skippedExamples"]},
            {"ignored_dir:build", "symlink"},
        )

    def test_init_dry_run_json_accepts_explicit_file_scan_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(5):
                (root / f"doc-{index}.md").write_text("# Doc\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--dry-run",
                        "--json",
                        "--max-files",
                        "3",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["repositoryScan"]["maxFiles"], 3)
        self.assertEqual(payload["repositoryScan"]["fileCount"], 3)
        self.assertTrue(payload["repositoryScan"]["truncated"])
        self.assertEqual(
            payload["repositoryScan"]["coverage"]["schemaVersion"],
            "harnessforge.fileCoverage.v1",
        )
        self.assertEqual(
            payload["repositoryScan"]["coverage"]["inventorySource"],
            "filesystem_scan",
        )

    def test_init_dry_run_json_reports_nested_instruction_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "workspaces": ["packages/*"],
                        "scripts": {"test": "node --test"},
                    }
                ),
                encoding="utf-8",
            )
            for package in ("api", "web"):
                package_root = root / "packages" / package
                package_root.mkdir(parents=True)
                (package_root / "package.json").write_text(
                    json.dumps({"name": package}),
                    encoding="utf-8",
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["init", "--target", str(root), "--dry-run", "--json"])
            payload = json.loads(stdout.getvalue())

        plan = payload["nestedInstructionPlan"]
        instruction_paths = {
            item["instructionPath"] for item in plan["candidateComponents"]
        }
        self.assertEqual(code, 0)
        self.assertEqual(plan["schemaVersion"], "harnessforge.nestedInstructionPlan.v1")
        self.assertEqual(plan["status"], "review_required")
        self.assertFalse(plan["writeByDefault"])
        self.assertIn("package.json workspaces", plan["monorepoSignals"])
        self.assertIn("packages/api/AGENTS.md", instruction_paths)
        self.assertIn("packages/web/AGENTS.md", instruction_paths)
        self.assertFalse((root / "packages" / "api" / "AGENTS.md").exists())

    def test_index_ignores_harnessforge_scratch_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            scratch = root / ".harnessforge" / "large-public-repos"
            scratch.mkdir(parents=True)
            for index in range(10):
                (scratch / f"external-{index}.md").write_text(
                    "# External\n",
                    encoding="utf-8",
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    ["index", "--target", str(root), "--max-files", "3", "--json"]
                )
            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["fileCount"], 1)
        self.assertFalse(payload["summary"]["truncated"])
        self.assertEqual(
            [item["path"] for item in payload["sourceOfTruth"]],
            ["README.md"],
        )

    def test_index_json_reports_component_inventory_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(85):
                component = root / f"pkg-{index:02d}"
                component.mkdir()
                (component / "package.json").write_text("{}", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["index", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["componentCount"], 80)
        self.assertEqual(payload["summary"]["componentTotalCount"], 85)
        self.assertEqual(payload["summary"]["componentOmittedCount"], 5)
        self.assertTrue(payload["summary"]["componentsTruncated"])
        self.assertEqual(payload["limits"]["maxComponents"], 80)
        self.assertEqual(payload["componentOverflow"]["omittedCount"], 5)
        self.assertTrue(payload["componentOverflow"]["omittedExamples"])
        self.assertIn("selected 80 of 85", " ".join(payload["warnings"]))

    def test_index_json_accepts_explicit_component_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(5):
                component = root / f"pkg-{index:02d}"
                component.mkdir()
                (component / "package.json").write_text("{}", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "index",
                        "--target",
                        str(root),
                        "--component-limit",
                        "3",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["componentCount"], 3)
        self.assertEqual(payload["summary"]["componentTotalCount"], 5)
        self.assertEqual(payload["summary"]["componentOmittedCount"], 2)
        self.assertEqual(payload["componentOverflow"]["limit"], 3)

    def test_index_json_preserves_trailing_space_file_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Exit: ").write_text("diagnostic output\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["index", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        class_examples = {
            item["class"]: item["examples"] for item in payload["fileClasses"]
        }
        self.assertIn("Exit: ", class_examples["other"])
        self.assertIn(
            {"class": "other", "files": 1, "bytes": 18, "examples": ["Exit: "]},
            payload["fileClasses"],
        )
        self.assertFalse(
            any("Could not stat file" in warning for warning in payload["warnings"])
        )

    def test_index_json_ignores_common_os_metadata_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".DS_Store").write_bytes(b"metadata")
            (root / "Thumbs.db").write_bytes(b"metadata")
            (root / "desktop.ini").write_text("[ViewState]\n", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["index", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        examples = {
            example
            for item in payload["fileClasses"]
            for example in item["examples"]
        }
        self.assertIn("README.md", examples)
        self.assertNotIn(".DS_Store", examples)
        self.assertNotIn("Thumbs.db", examples)
        self.assertNotIn("desktop.ini", examples)
        self.assertEqual(payload["summary"]["fileCount"], 1)

    def test_effectiveness_json_assesses_reviewable_evidence_without_writing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            evidence_dir = root / "docs" / "harness" / "evidence"
            evidence_dir.mkdir(parents=True)
            (evidence_dir / "effectiveness-context.json").write_text(
                json.dumps(
                    {
                        "schemaVersion": "harnessforge.effectivenessEvidence.v1",
                        "claim": {
                            "id": "context-router-heldout",
                            "summary": "Candidate improves held-out task success.",
                            "scope": "Instruction-router harness surface.",
                            "verdict": "candidate_better",
                        },
                        "target": {"name": "demo", "root": None},
                        "candidate": {
                            "id": "candidate-v1",
                            "description": "Candidate router.",
                            "changedSurfaces": ["mechanism"],
                            "snapshot": {
                                "snapshotId": "candidate-v1",
                                "artifactRefs": ["AGENTS.md"],
                            },
                        },
                        "baseline": {
                            "id": "baseline-v1",
                            "description": "Baseline router.",
                            "changedSurfaces": [],
                            "snapshot": {
                                "snapshotId": "baseline-v1",
                                "artifactRefs": ["AGENTS.md"],
                            },
                        },
                        "evaluation": {
                            "id": "heldout-context-routing",
                            "replayType": "live",
                            "feedbackChannels": ["test", "trajectory"],
                            "taskSet": {
                                "id": "heldout-routing",
                                "description": "Held-out repo tasks.",
                                "sampleCount": 6,
                                "heldOut": True,
                                "contaminationControls": ["held-out prompts"],
                            },
                            "runtimeBudget": {
                                "wallClockSeconds": 1800,
                                "modelCalls": 40,
                                "tokens": 120000,
                                "toolCalls": 80,
                                "retries": 1,
                            },
                            "workspaceContract": {
                                "state": "Fresh checkout.",
                                "dependencies": "Repo-owned setup only.",
                                "networkAccess": "Disabled.",
                                "cleanup": "Discard workspace after run.",
                                "scoringEntrypoint": "python -m unittest discover",
                            },
                            "adapterContract": {
                                "normalization": "Same model and tool policy.",
                                "agents": ["codex-cli"],
                                "modelPolicy": "Same supported model.",
                            },
                            "reproductionCommand": (
                                "python scripts/run_effectiveness_eval.py "
                                "--config evals/context.json"
                            ),
                        },
                        "metrics": {
                            "primary": {
                                "name": "task_success_rate",
                                "candidateSensitive": True,
                                "direction": "higher_is_better",
                                "baselineValue": 0.5,
                                "candidateValue": 0.75,
                                "unit": "rate",
                            },
                            "worstCase": {
                                "name": "lowest_task_score",
                                "candidateSensitive": True,
                                "direction": "higher_is_better",
                                "baselineValue": 0.3,
                                "candidateValue": 0.4,
                                "unit": "score",
                            },
                            "doNoHarmFloor": {
                                "metric": "lowest_task_score",
                                "minimum": 0.3,
                                "met": True,
                            },
                            "secondary": [],
                        },
                        "safety": {
                            "trajectoryReviewed": True,
                            "permissionBoundaryReviewed": True,
                            "violations": [],
                        },
                        "cost": {
                            "optimized": False,
                            "dimensions": [
                                {
                                    "name": "tokens",
                                    "unit": "tokens",
                                    "baselineValue": 100000,
                                    "candidateValue": 95000,
                                }
                            ],
                        },
                        "evidence": {
                            "resultArtifacts": [
                                {
                                    "path": "evals/results/context.json",
                                    "kind": "result-log",
                                    "redacted": True,
                                }
                            ],
                            "reviewedBy": ["maintainer"],
                            "reviewedAt": "2026-06-15T00:00:00Z",
                            "notes": ["Reviewed held-out run."],
                        },
                        "promotion": {
                            "status": "promoted",
                            "humanApproved": True,
                            "rollback": "Revert candidate router.",
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["effectiveness", "--target", str(root), "--json"])
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            raw_payload = stdout.getvalue()
            payload = json.loads(raw_payload)

        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        self.assertNotIn(str(root), raw_payload)
        self.assertEqual(
            payload["schemaVersion"], "harnessforge.effectivenessAssessment.v1"
        )
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["verdict"], "reviewable")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertFalse(payload["execution"]["writesPerformed"])
        self.assertEqual(payload["summary"]["reports"], 1)
        self.assertEqual(payload["summary"]["reviewableReports"], 1)
        self.assertEqual(payload["blockedReasons"], [])
        report = payload["reports"][0]
        self.assertEqual(
            report["path"], "docs/harness/evidence/effectiveness-context.json"
        )
        self.assertTrue(report["schemaValid"])
        self.assertEqual(report["assessmentStatus"], "reviewable")
        self.assertEqual(report["claim"]["verdict"], "candidate_better")
        self.assertEqual(report["primaryMetric"]["delta"], 0.25)
        self.assertEqual(report["blockers"], [])

    def test_effectiveness_json_blocks_without_representative_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["effectiveness", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertEqual(payload["summary"]["reports"], 0)
        self.assertEqual(payload["summary"]["reviewableReports"], 0)
        self.assertTrue(
            any("No effectiveness evidence" in item for item in payload["blockedReasons"])
        )
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertFalse(payload["execution"]["writesPerformed"])

    def test_effectiveness_rejects_absolute_evidence_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(
                    [
                        "effectiveness",
                        "--target",
                        str(root),
                        "--evidence",
                        str(root / "evidence.json"),
                    ]
                )

            error = stderr.getvalue()

        self.assertEqual(code, 2)
        self.assertIn("--evidence must be a target-relative path", error)
        self.assertNotIn(str(root), error)

    def test_effectiveness_trims_explicit_evidence_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            evidence_dir = root / "docs" / "harness" / "evidence"
            evidence_dir.mkdir(parents=True)
            (evidence_dir / "effectiveness-context.json").write_text(
                json.dumps({"schemaVersion": "bad"}),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "effectiveness",
                        "--target",
                        str(root),
                        "--evidence",
                        " docs/harness/evidence/effectiveness-context.json ",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(
            payload["reports"][0]["path"],
            "docs/harness/evidence/effectiveness-context.json",
        )

    def test_inspect_readiness_json_reports_ready_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text(
                "import unittest\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    ["inspect", "--target", str(root), "--readiness", "--json"]
                )

            payload = json.loads(stdout.getvalue())
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["blockedReasons"], [])
        self.assertEqual(payload["warnings"], [])
        for key in (
            "nextActions",
            "sourceOfTruth",
            "runnableChecks",
            "generatedDrift",
            "reviewRequired",
            "workflowInventory",
            "workItemInventory",
            "contextBudget",
            "governanceInventory",
            "effectivenessInventory",
            "instructionQuality",
            "verifyEvidence",
        ):
            self.assertIn(key, payload)
        self.assertEqual(payload["instructionQuality"]["summary"]["status"], "absent")
        self.assertIsNone(payload["verifyEvidence"]["latest"])
        self.assertEqual(payload["verifyEvidence"]["reports"], [])
        self.assertIn("python -m unittest discover", payload["runnableChecks"])

    def test_session_json_reports_restart_snapshot_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            with contextlib.redirect_stdout(stdout):
                code = main(["session", "--target", str(root), "--json"])
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        self.assertEqual(payload["schemaVersion"], "harnessforge.session.v1")
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["detectedStack"], "python")
        self.assertEqual(payload["readiness"]["verdict"], "ready")
        self.assertEqual(payload["harnessAudit"]["overall"], 100)
        state = {item["path"]: item["present"] for item in payload["stateFiles"]}
        self.assertTrue(state["feature_list.json"])
        self.assertTrue(state["current-state.md"])
        self.assertNotIn("progress.md", state)
        self.assertNotIn("session-handoff.md", state)
        self.assertIn("docs/harness/evidence/evidence-log.md", state)
        self.assertIn("git", payload)

    def test_session_text_reports_snapshot_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["session", "--target", str(root)])

            text = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Session snapshot:", text)
        self.assertIn("Git: unavailable", text)
        self.assertIn("Detected stack: python", text)
        self.assertIn("Readiness: ready", text)
        self.assertIn("Harness audit: 100/100", text)
        self.assertIn("State files:", text)
        self.assertIn("Next actions:", text)

    def test_report_json_composes_readiness_audit_index_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root), "--command", command])
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-2026-06-15.json",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            marker_exists = marker.exists()

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertFalse(marker_exists)
        self.assertEqual(payload["schemaVersion"], "harnessforge.report.v1")
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["execution"]["commandsExecuted"], False)
        self.assertEqual(payload["readiness"]["verdict"], "ready")
        self.assertEqual(
            payload["reviewWork"]["schemaVersion"],
            "harnessforge.reviewWork.v1",
        )
        self.assertEqual(
            payload["reviewWork"]["unresolvedActionable"]["count"],
            0,
        )
        self.assertEqual(payload["reviewWork"]["acceptedAdvisory"]["count"], 0)
        self.assertEqual(payload["audit"]["overall"], 100)
        self.assertEqual(payload["drift"]["summary"]["actionable"], 0)
        self.assertIn("fileCount", payload["index"]["summary"])
        self.assertIn("repoMap", payload["index"])
        self.assertEqual(
            payload["index"]["fileCoverage"]["schemaVersion"],
            "harnessforge.fileCoverage.v1",
        )
        self.assertIn("sbomCount", payload["index"]["summary"])
        self.assertEqual(payload["verifyEvidence"]["latest"]["verdict"], "passed")
        self.assertEqual(payload["effectiveness"]["verdict"], "blocked")
        self.assertEqual(payload["instructionQuality"]["summary"]["status"], "strong")
        self.assertGreaterEqual(
            payload["instructionQuality"]["summary"]["averageScore"], 80
        )
        self.assertEqual(
            payload["skillWiring"]["schemaVersion"],
            "harnessforge.skillWiring.v1",
        )
        self.assertEqual(payload["skillWiring"]["status"], "wired")
        self.assertIn("AGENTS.md", payload["skillWiring"]["instructionRoutes"])
        self.assertIn(
            "docs/harness/feedback/verification-matrix.md",
            payload["skillWiring"]["resolvedReferences"],
        )
        self.assertEqual(
            payload["nestedInstructionPlan"]["schemaVersion"],
            "harnessforge.nestedInstructionPlan.v1",
        )
        self.assertEqual(payload["nestedInstructionPlan"]["status"], "no_action")
        self.assertEqual(payload["firstAgentTask"]["status"], "pending_review")
        self.assertEqual(payload["firstAgentTask"]["lifecycle"]["status"], "pending")
        self.assertEqual(
            payload["firstAgentTask"]["lifecycle"]["evidencePath"],
            "docs/harness/evidence/first-agent-review.json",
        )
        self.assertEqual(payload["platform"]["contract"], "cross-platform")
        self.assertEqual(payload["releaseControls"]["present"], True)
        self.assertEqual(
            payload["maturity"]["schemaVersion"], "harnessforge.maturity.v1"
        )
        self.assertEqual(payload["maturity"]["currentLevel"], "generated")
        self.assertEqual(payload["maturity"]["nextLevel"], "reviewed")
        self.assertEqual(
            payload["docsFanout"]["authoritativeMap"]["status"], "pending_review"
        )
        self.assertEqual(
            payload["featureState"]["schemaVersion"],
            "harnessforge.featureState.v1",
        )
        self.assertEqual(payload["featureState"]["status"], "aligned")
        self.assertEqual(payload["featureState"]["summary"]["activeCount"], 1)
        self.assertEqual(
            payload["featureState"]["scopeDrift"]["status"], "not_requested"
        )
        self.assertEqual(
            payload["observability"]["schemaVersion"],
            "harnessforge.observability.v1",
        )
        self.assertEqual(payload["observability"]["status"], "strong")
        self.assertGreaterEqual(
            payload["observability"]["summary"]["processSignalCount"], 4
        )
        self.assertEqual(
            payload["indexAdapters"]["schemaVersion"],
            "harnessforge.indexAdapters.v1",
        )
        self.assertEqual(
            payload["indexAdapters"]["defaultBehavior"],
            "standard_library_structural_index",
        )
        self.assertFalse(payload["indexAdapters"]["generationEnabled"])
        self.assertTrue(payload["indexAdapters"]["explicitOptInRequired"])
        self.assertEqual(payload["docsFanout"]["surfaceCount"], 12)
        self.assertEqual(payload["docsFanout"]["coveredSurfaceCount"], 12)
        self.assertTrue(
            all(surface["covered"] for surface in payload["docsFanout"]["surfaces"])
        )
        self.assertEqual(payload["docsFanout"]["diff"]["status"], "not_requested")
        self.assertEqual(
            payload["docsFanout"]["duplicateFacts"]["summary"]["blocks"], 0
        )
        self.assertIn("Run harnessforge report", payload["nextActions"][0])
        self.assertTrue(
            any("first-agent-review.json" in item for item in payload["nextActions"])
        )

    def test_report_json_reports_nested_instruction_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "workspaces": ["packages/*"],
                        "scripts": {"test": "node --test"},
                    }
                ),
                encoding="utf-8",
            )
            for package in ("api", "web"):
                package_root = root / "packages" / package
                package_root.mkdir(parents=True)
                (package_root / "package.json").write_text(
                    json.dumps(
                        (
                            {
                                "name": package,
                                "scripts": {
                                    "test": "vitest",
                                    "build": "vite build",
                                },
                            }
                            if package == "web"
                            else {"name": package}
                        )
                    ),
                    encoding="utf-8",
                )
            (root / "packages" / "web" / "README.md").write_text(
                "# Web Package\n",
                encoding="utf-8",
            )
            (root / "test").mkdir()
            (root / "test" / "package.json").write_text(
                json.dumps({"name": "test-fixtures"}),
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "name: ci\n"
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - packages/web/**\n"
                "jobs:\n"
                "  web:\n"
                "    defaults:\n"
                "      run:\n"
                "        working-directory: packages/web\n"
                "    steps:\n"
                "      - run: npm test\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--json"])
            payload = json.loads(stdout.getvalue())

        plan = payload["nestedInstructionPlan"]
        self.assertEqual(code, 0)
        self.assertEqual(plan["status"], "review_required")
        self.assertFalse(plan["writeByDefault"])
        self.assertEqual(plan["candidateCount"], 3)
        self.assertEqual(
            {item["instructionPath"] for item in plan["candidateComponents"]},
            {
                "packages/api/AGENTS.md",
                "packages/web/AGENTS.md",
                "test/AGENTS.md",
            },
        )
        self.assertEqual(plan["candidateComponents"][0]["path"], "packages/web")
        self.assertEqual(plan["candidateComponents"][0]["rank"], 1)
        self.assertIn(
            "verification source: packages/web/package.json",
            plan["candidateComponents"][0]["rankSignals"],
        )
        self.assertIn(
            "workflow routing: .github/workflows/ci.yml",
            plan["candidateComponents"][0]["rankSignals"],
        )
        self.assertIn(
            "local docs: packages/web/README.md",
            plan["candidateComponents"][0]["rankSignals"],
        )
        self.assertIn("verification", plan["candidateComponents"][0]["reviewFocus"])
        self.assertIn(
            ".github/workflows path filters",
            plan["monorepoSignals"],
        )
        test_candidate = next(
            item for item in plan["candidateComponents"] if item["path"] == "test"
        )
        self.assertNotIn("verification source: test", test_candidate["rankSignals"])
        self.assertTrue(
            any(
                "nested AGENTS.md candidates" in action
                for action in payload["nextActions"]
            )
        )

    def test_inspect_readiness_reports_broken_skill_wiring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / ".agents/skills/harness/references/repo-harness.md").unlink()
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(payload["skillWiring"]["status"], "incomplete")
        self.assertTrue(
            any("repo-harness.md is missing" in item for item in payload["warnings"])
        )
        self.assertTrue(
            any("skill wiring" in item for item in payload["nextActions"])
        )

    def test_report_json_includes_policy_presets_and_sbom_adapter_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "specs" / "001-demo").mkdir(parents=True)
            (root / "specs" / "001-demo" / "spec.md").write_text(
                "# Demo\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "report",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(
            payload["policyPresets"]["schemaVersion"],
            "harnessforge.policyPresets.v1",
        )
        available_ids = {
            item["id"] for item in payload["policyPresets"]["availablePresets"]
        }
        self.assertIn("open-source-library", available_ids)
        self.assertIn("spec-driven", available_ids)
        recommended_ids = {
            item["id"] for item in payload["policyPresets"]["recommendedPresets"]
        }
        self.assertIn("open-source-library", recommended_ids)
        self.assertIn("spec-driven", recommended_ids)
        self.assertEqual(
            payload["sbomAdapter"]["schemaVersion"],
            "harnessforge.sbomAdapter.v1",
        )
        self.assertEqual(
            payload["sbomAdapter"]["defaultBehavior"],
            "detect_existing_only",
        )
        self.assertFalse(payload["sbomAdapter"]["generationEnabled"])
        self.assertTrue(payload["sbomAdapter"]["explicitOptInRequired"])

    def test_report_json_summarizes_completed_first_agent_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            _write_verify_report(root, "docs/harness/evidence/verify-2026-06-15.json")
            _write_first_agent_review(root)
            task = root / "docs/harness/state/first-agent-task.md"
            task.write_text(
                task.read_text(encoding="utf-8").replace("REVIEW REQUIRED: ", ""),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(payload["firstAgentTask"]["status"], "reviewed_or_retired")
        lifecycle = payload["firstAgentTask"]["lifecycle"]
        self.assertEqual(lifecycle["status"], "completed")
        self.assertTrue(lifecycle["schemaValid"])
        self.assertEqual(lifecycle["blockers"], [])
        self.assertEqual(lifecycle["warnings"], [])

    def test_report_consumes_high_risk_surface_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# AGENTS.md\n\n"
                "## Project overview\n"
                "This project is a Python repository with repo-owned harness docs.\n\n"
                "## Startup\n"
                "Read `README.md`, `feature_list.json`, and `current-state.md`.\n\n"
                "## Verification\n"
                "Run `python -m unittest discover -s tests` before completion.\n\n"
                "## Constraints\n"
                "Do not expose secrets. Preserve security boundaries and "
                "project docs.\n\n"
                "## State\n"
                "Use `current-state.md` and `docs/roadmap.md` for current work.\n\n"
                "## Routing\n"
                "See `docs/harness/README.md` for harness maintenance guidance.\n",
                encoding="utf-8",
            )
            (root / "Dockerfile").write_text(
                "FROM python:3.13\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "name: ci\n"
                "on:\n"
                "  push:\n"
                "  pull_request:\n"
                "jobs:\n"
                "  test:\n"
                "    steps:\n"
                "      - run: python -m unittest discover -s tests\n"
                "        env:\n"
                "          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n",
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m unittest discover -s tests",
                    ]
                )
            task = root / "docs/harness/state/first-agent-task.md"
            task.write_text(
                task.read_text(encoding="utf-8").replace("REVIEW REQUIRED: ", ""),
                encoding="utf-8",
            )
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-2026-06-15.json",
            )
            _write_first_agent_review(
                root,
                status="completed",
                high_risk_surfaces=[
                    {
                        "path": "AGENTS.md",
                        "category": "instruction-router",
                        "decision": "accepted",
                    },
                    {
                        "path": "Dockerfile",
                        "category": "container-runtime",
                        "decision": "accepted",
                    },
                    {
                        "path": ".github/workflows/ci.yml",
                        "category": "workflow",
                        "decision": "accepted",
                    },
                ],
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(payload["readiness"]["reviewRequiredCount"], 0)
        self.assertEqual(
            payload["readiness"]["highRiskAcceptance"]["status"],
            "accepted_advisory",
        )
        self.assertEqual(
            payload["readiness"]["highRiskAcceptance"]["summary"]["acceptedCount"],
            3,
        )
        surfaces = {
            item["path"]: item
            for item in payload["readiness"]["reviewSurfaces"]
        }
        self.assertEqual(surfaces["AGENTS.md"]["status"], "accepted_advisory")
        self.assertEqual(
            surfaces[".github/workflows/ci.yml"]["status"],
            "accepted_advisory",
        )
        self.assertEqual(surfaces["Dockerfile"]["status"], "accepted_advisory")
        self.assertGreaterEqual(
            payload["readiness"]["reviewStatusSummary"]["acceptedAdvisory"],
            3,
        )
        self.assertFalse(
            any(
                "AGENTS.md already exists" in item
                for item in payload["readiness"]["reviewRequired"]
            )
        )
        self.assertFalse(
            any("Dockerfile" in item for item in payload["readiness"]["reviewRequired"])
        )
        self.assertFalse(
            any(
                ".github/workflows/ci.yml" in item
                for item in payload["readiness"]["reviewRequired"]
            )
        )
        self.assertNotEqual(payload["maturity"]["currentLevel"], "generated")

    def test_finalize_review_requires_explicit_high_risk_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_review_finalize_fixture(root)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m unittest discover -s tests",
                    ]
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                dry_run_code = main(["finalize-review", "--target", str(root), "--json"])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                apply_code = main(["finalize-review", "--target", str(root), "--apply"])

            payload = json.loads(stdout.getvalue())
            evidence = json.loads(
                (
                    root / "docs/harness/evidence/first-agent-review.json"
                ).read_text(encoding="utf-8")
            )

        self.assertEqual(init_code, 0)
        self.assertEqual(dry_run_code, 0)
        self.assertEqual(apply_code, 2)
        self.assertEqual(payload["schemaVersion"], "harnessforge.reviewFinalization.v1")
        self.assertEqual(payload["mode"], "dry_run")
        self.assertTrue(payload["review"]["requiresHighRiskAcceptanceFlag"])
        self.assertEqual(
            {item["path"] for item in payload["highRiskSurfaces"]},
            {"AGENTS.md", ".github/workflows/ci.yml"},
        )
        self.assertEqual(evidence["status"], "pending")

    def test_finalize_review_apply_requires_yes_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_review_finalize_fixture(root)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m unittest discover -s tests",
                    ]
                )
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                apply_code = main(
                    [
                        "finalize-review",
                        "--target",
                        str(root),
                        "--apply",
                        "--accept-detected-high-risk",
                    ]
                )
            evidence = json.loads(
                (
                    root / "docs/harness/evidence/first-agent-review.json"
                ).read_text(encoding="utf-8")
            )

        self.assertEqual(init_code, 0)
        self.assertEqual(apply_code, 2)
        self.assertIn("requires --yes", stderr.getvalue())
        self.assertEqual(evidence["status"], "pending")

    def test_finalize_review_apply_retires_task_and_accepts_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_review_finalize_fixture(root)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m unittest discover -s tests",
                    ]
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                finalize_code = main(
                    [
                        "finalize-review",
                        "--target",
                        str(root),
                        "--apply",
                        "--accept-detected-high-risk",
                        "--yes",
                        "--reviewed-by",
                        "Maintainer",
                        "--json",
                    ]
                )
            report_stdout = io.StringIO()
            with contextlib.redirect_stdout(report_stdout):
                report_code = main(["report", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            report = json.loads(report_stdout.getvalue())
            evidence = json.loads(
                (
                    root / "docs/harness/evidence/first-agent-review.json"
                ).read_text(encoding="utf-8")
            )
            task = (
                root / "docs/harness/state/first-agent-task.md"
            ).read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(init_code, 0)
        self.assertEqual(finalize_code, 0)
        self.assertEqual(report_code, 0)
        self.assertEqual(payload["mode"], "apply")
        self.assertEqual(payload["changedFiles"], 3)
        self.assertEqual(
            {item["path"] for item in payload["highRiskSurfaces"]},
            {"AGENTS.md", ".github/workflows/ci.yml"},
        )
        self.assertEqual(evidence["status"], "retired")
        self.assertEqual(evidence["reviewedBy"], ["Maintainer"])
        self.assertEqual(
            evidence["highRiskSurfaceReview"]["status"],
            "accepted_advisory",
        )
        self.assertEqual(
            {item["path"] for item in evidence["highRiskSurfaceReview"]["surfaces"]},
            {"AGENTS.md", ".github/workflows/ci.yml"},
        )
        self.assertIn("Status: retired after first-agent review.", task)
        self.assertNotIn("REVIEW REQUIRED", task)
        self.assertNotIn(
            "docs/harness/state/first-agent-task.md",
            manifest["reviewRequired"],
        )
        self.assertNotIn(
            "docs/harness/evidence/first-agent-review.json",
            manifest["reviewRequired"],
        )
        self.assertEqual(
            manifest["generatedFiles"]["docs/harness/state/first-agent-task.md"][
                "ownership"
            ],
            "project-owned",
        )
        self.assertNotIn(
            "REVIEW REQUIRED",
            manifest["requiredHarnessSnippets"]["docs/harness/state/first-agent-task.md"],
        )
        self.assertEqual(report["readiness"]["verdict"], "warning")
        self.assertEqual(report["readiness"]["reviewRequiredCount"], 0)
        self.assertEqual(report["skillWiring"]["status"], "incomplete")
        self.assertTrue(
            any("harness skill wiring" in item for item in report["nextActions"])
        )
        self.assertEqual(
            report["readiness"]["highRiskAcceptance"]["summary"]["acceptedCount"],
            2,
        )
        self.assertEqual(report["maturity"]["currentLevel"], "reviewed")

    def test_migrate_state_dry_run_reports_legacy_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "progress.md").write_text("# Progress\n\nDone.\n", encoding="utf-8")
            (root / "session-handoff.md").write_text(
                "# Handoff\n\nNext step.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["migrate-state", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            current_exists = (root / "current-state.md").exists()

        self.assertEqual(code, 0)
        self.assertEqual(payload["schemaVersion"], "harnessforge.stateMigration.v1")
        self.assertEqual(payload["mode"], "dry_run")
        self.assertFalse(payload["execution"]["writesPerformed"])
        self.assertFalse(current_exists)
        self.assertEqual(
            {item["path"] for item in payload["legacyFiles"] if item["exists"]},
            {"progress.md", "session-handoff.md"},
        )
        self.assertEqual(payload["plannedWrites"][0]["path"], "current-state.md")
        self.assertEqual(payload["plannedWrites"][0]["status"], "would_write")

    def test_migrate_state_apply_requires_yes_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "progress.md").write_text("# Progress\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                code = main(["migrate-state", "--target", str(root), "--apply"])
            current_exists = (root / "current-state.md").exists()

        self.assertEqual(code, 2)
        self.assertFalse(current_exists)
        self.assertIn("requires --yes", stderr.getvalue())

    def test_migrate_state_apply_preserves_legacy_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "current-state.md").write_text(
                "# Current State\n\n## Current Objective\n\nExisting.\n",
                encoding="utf-8",
            )
            (root / "progress.md").write_text("# Progress\n\nDone.\n", encoding="utf-8")
            (root / "session-handoff.md").write_text(
                "# Handoff\n\nNext step.\n",
                encoding="utf-8",
            )
            first_stdout = io.StringIO()
            with contextlib.redirect_stdout(first_stdout):
                first_code = main(
                    [
                        "migrate-state",
                        "--target",
                        str(root),
                        "--apply",
                        "--yes",
                        "--json",
                    ]
                )
            second_stdout = io.StringIO()
            with contextlib.redirect_stdout(second_stdout):
                second_code = main(
                    [
                        "migrate-state",
                        "--target",
                        str(root),
                        "--apply",
                        "--yes",
                        "--json",
                    ]
                )

            first_payload = json.loads(first_stdout.getvalue())
            second_payload = json.loads(second_stdout.getvalue())
            current = (root / "current-state.md").read_text(encoding="utf-8")
            progress_preserved = (root / "progress.md").exists()
            handoff_preserved = (root / "session-handoff.md").exists()

        self.assertEqual(first_code, 0)
        self.assertEqual(second_code, 0)
        self.assertEqual(first_payload["mode"], "apply")
        self.assertEqual(first_payload["changedFiles"], 1)
        self.assertEqual(second_payload["changedFiles"], 0)
        self.assertEqual(second_payload["appliedWrites"][0]["status"], "unchanged")
        self.assertTrue(progress_preserved)
        self.assertTrue(handoff_preserved)
        self.assertIn("<!-- harnessforge-state-migration:start -->", current)
        self.assertIn("### progress.md", current)
        self.assertIn("### session-handoff.md", current)

    def test_readiness_warns_when_first_agent_evidence_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            (root / "docs/harness/evidence/first-agent-review.json").unlink()
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertEqual(payload["firstAgentLifecycle"]["status"], "pending")
        self.assertTrue(
            any("first-agent review evidence is missing" in item for item in payload["warnings"])
        )

    def test_report_json_marks_stale_first_agent_review_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            evidence = root / "docs/harness/evidence/first-agent-review.json"
            stale_timestamp = 1
            os.utime(evidence, (stale_timestamp, stale_timestamp))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        lifecycle = payload["firstAgentTask"]["lifecycle"]
        self.assertEqual(lifecycle["status"], "stale")
        self.assertEqual(lifecycle["evidenceStatus"], "pending")
        self.assertTrue(
            any("stale" in item for item in lifecycle["warnings"])
        )

    def test_report_since_reports_docs_fanout_and_duplicate_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            _git(root, "init")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "HarnessForge Test")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "initial")
            repeated_fact = (
                "This durable harness fact is repeated on purpose so the report "
                "can identify duplicated long-form guidance and route one copy "
                "through the authoritative facts map instead of keeping the same "
                "maintenance instruction in multiple Markdown files."
            )
            for relative_path in (
                "AGENTS.md",
                "docs/harness/release/release-controls.md",
                "docs/harness/boundaries/security-boundary-map.md",
            ):
                path = root / relative_path
                path.write_text(
                    path.read_text(encoding="utf-8")
                    + "\n\n"
                    + repeated_fact
                    + "\n",
                    encoding="utf-8",
                )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["report", "--target", str(root), "--since", "HEAD", "--json"])

            payload = json.loads(stdout.getvalue())
            blocking_stdout = io.StringIO()
            with contextlib.redirect_stdout(blocking_stdout):
                blocking_code = main(
                    [
                        "report",
                        "--target",
                        str(root),
                        "--since",
                        "HEAD",
                        "--require-docs-fanout-budget",
                        "--json",
                    ]
                )
            blocking_payload = json.loads(blocking_stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        fanout = payload["docsFanout"]
        self.assertEqual(fanout["contract"]["verdict"], "warning")
        self.assertEqual(fanout["diff"]["status"], "available")
        self.assertEqual(fanout["diff"]["base"], "HEAD")
        self.assertEqual(fanout["diff"]["changedFileCount"], 3)
        self.assertEqual(fanout["diff"]["classification"], "exception_review")
        self.assertGreaterEqual(fanout["diff"]["touchedSurfaceCount"], 4)
        self.assertIn("security_privacy", fanout["diff"]["touchedSurfaceIds"])
        self.assertTrue(
            any("Docs fan-out warning" in item for item in fanout["warnings"])
        )
        self.assertGreaterEqual(fanout["duplicateFacts"]["summary"]["blocks"], 1)
        duplicate_paths = set(fanout["duplicateFacts"]["items"][0]["paths"])
        self.assertIn("AGENTS.md", duplicate_paths)
        self.assertEqual(blocking_code, 2)
        self.assertEqual(
            blocking_payload["docsFanout"]["contract"]["verdict"],
            "blocked",
        )
        self.assertIn(
            "Changed files touch more than three product boundary surfaces.",
            blocking_payload["docsFanout"]["contract"]["blockedReasons"],
        )

    def test_report_markdown_can_write_target_contained_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(["init", "--target", str(root), "--command", "python -m compileall ."])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "report",
                        "--target",
                        str(root),
                        "--markdown-report",
                        "docs/harness/evidence/report.md",
                        "--json-report",
                        "docs/harness/evidence/report.json",
                    ]
                )

            markdown = (root / "docs/harness/evidence/report.md").read_text(
                encoding="utf-8"
            )
            payload = json.loads(
                (root / "docs/harness/evidence/report.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(code, 0)
        self.assertIn(
            "Markdown report written to docs/harness/evidence/report.md",
            stdout.getvalue(),
        )
        self.assertIn(
            "JSON report written to docs/harness/evidence/report.json",
            stdout.getvalue(),
        )
        self.assertIn("# HarnessForge Report", markdown)
        self.assertIn("## Readiness", markdown)
        self.assertIn("## Docs Fan-Out", markdown)
        self.assertIn("## Next Actions", markdown)
        self.assertEqual(payload["schemaVersion"], "harnessforge.report.v1")

    def test_release_check_blocks_missing_verify_evidence_without_running_commands(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            with contextlib.redirect_stdout(io.StringIO()):
                main(["init", "--target", str(root), "--command", command])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["release-check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 2)
        self.assertFalse(marker.exists())
        self.assertEqual(payload["schemaVersion"], "harnessforge.releaseCheck.v1")
        self.assertEqual(payload["execution"]["commandsExecuted"], False)
        self.assertEqual(payload["execution"]["writesPerformed"], False)
        self.assertEqual(payload["execution"]["publishesPerformed"], False)
        self.assertEqual(payload["verdict"], "blocked")
        gates = {item["id"]: item for item in payload["gates"]}
        self.assertEqual(gates["audit-score"]["status"], "passed")
        self.assertEqual(gates["verify-evidence"]["status"], "blocked")
        self.assertIn(
            "no stored verify evidence report found",
            gates["verify-evidence"]["message"],
        )

    def test_release_check_writes_target_contained_evidence_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            _write_verify_report(root, "docs/harness/evidence/verify-2026-06-15.json")
            _write_first_agent_review(root)
            task = root / "docs/harness/state/first-agent-task.md"
            task.write_text(
                task.read_text(encoding="utf-8").replace("REVIEW REQUIRED: ", ""),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "release-check",
                        "--target",
                        str(root),
                        "--json-report",
                        "docs/harness/evidence/release-check.json",
                        "--markdown-report",
                        "docs/harness/evidence/release-check.md",
                    ]
                )

            payload = json.loads(
                (root / "docs/harness/evidence/release-check.json").read_text(
                    encoding="utf-8"
                )
            )
            markdown = (root / "docs/harness/evidence/release-check.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(code, 1)
        self.assertIn(
            "JSON release check written to docs/harness/evidence/release-check.json",
            stdout.getvalue(),
        )
        self.assertIn(
            "Markdown release check written to docs/harness/evidence/release-check.md",
            stdout.getvalue(),
        )
        self.assertEqual(payload["verdict"], "warning")
        gates = {item["id"]: item for item in payload["gates"]}
        self.assertEqual(gates["verify-evidence"]["status"], "passed")
        self.assertEqual(gates["first-agent-lifecycle"]["status"], "passed")
        self.assertEqual(gates["feature-state"]["status"], "passed")
        self.assertEqual(gates["observability"]["status"], "passed")
        self.assertEqual(gates["effectiveness-evidence"]["status"], "warning")
        self.assertEqual(gates["sbom"]["status"], "not_required")
        self.assertIn("maturityLevel", payload["summary"])
        self.assertEqual(payload["summary"]["featureStateStatus"], "aligned")
        self.assertEqual(payload["summary"]["observabilityStatus"], "strong")
        self.assertIn("reviewWork", payload["sourceReport"])
        self.assertIn("currentLevel", payload["sourceReport"]["maturity"])
        self.assertIn("# HarnessForge Release Check", markdown)

    def test_release_check_accepts_compact_verify_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--command",
                        "python -m compileall .",
                    ]
                )
            _write_verify_summary(
                root,
                "docs/harness/evidence/verify-summary.json",
            )
            _write_first_agent_review(root)
            task = root / "docs/harness/state/first-agent-task.md"
            task.write_text(
                task.read_text(encoding="utf-8").replace("REVIEW REQUIRED: ", ""),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["release-check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 1)
        gates = {item["id"]: item for item in payload["gates"]}
        self.assertEqual(gates["verify-evidence"]["status"], "passed")
        self.assertEqual(
            payload["sourceReport"]["verifyEvidence"]["latest"]["schemaVersion"],
            "harnessforge.verifySummary.v1",
        )
        self.assertTrue(payload["sourceReport"]["verifyEvidence"]["latest"]["compact"])

    def test_plan_json_maps_changed_files_without_running_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "demo.py").write_text("VALUE = 1\n", encoding="utf-8")
            _git(root, "init")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "HarnessForge Test")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "initial")
            (root / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
            marker = root / "ran.txt"
            python_command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "plan",
                        "--target",
                        str(root),
                        "--since",
                        "HEAD",
                        "--json",
                        "--command",
                        python_command,
                        "--command",
                        "npm test",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(payload["schemaVersion"], "harnessforge.plan.v1")
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["mode"], "diff")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertEqual(payload["base"], "HEAD")
        self.assertEqual(payload["changedFiles"], ["src/demo.py"])
        self.assertEqual(payload["verdict"], "planned")
        self.assertEqual(payload["summary"]["planned"], 1)
        self.assertEqual(len(payload["checks"]), 1)
        self.assertEqual(payload["checks"][0]["command"], python_command)
        self.assertEqual(payload["checks"][0]["matchedFiles"], ["src/demo.py"])
        self.assertIn("python", payload["checks"][0]["reason"])

    def test_plan_text_blocks_when_git_diff_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["plan", "--target", str(root), "--since", "HEAD"])
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            text = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        self.assertIn("Verification plan: blocked", text)
        self.assertIn("Unable to inspect changed files with git diff", text)

    def test_plan_json_includes_untracked_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            _git(root, "init")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "HarnessForge Test")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "initial")
            (root / "src").mkdir()
            (root / "src" / "new_module.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "plan",
                        "--target",
                        str(root),
                        "--since",
                        "HEAD",
                        "--json",
                        "--command",
                        "python -m unittest discover",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["changedFiles"], ["src/new_module.py"])
        self.assertEqual(payload["checks"][0]["matchedFiles"], ["src/new_module.py"])

    def test_plan_json_warns_about_unmatched_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "demo.py").write_text("VALUE = 1\n", encoding="utf-8")
            _git(root, "init")
            _git(root, "config", "user.email", "test@example.invalid")
            _git(root, "config", "user.name", "HarnessForge Test")
            _git(root, "add", ".")
            _git(root, "commit", "-m", "initial")
            (root / "README.md").write_text("# Demo\n\nUpdate.\n", encoding="utf-8")
            (root / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "plan",
                        "--target",
                        str(root),
                        "--since",
                        "HEAD",
                        "--json",
                        "--command",
                        "python -m unittest discover",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["changedFiles"], ["README.md", "src/demo.py"])
        self.assertEqual(payload["unmatchedFiles"], ["README.md"])
        self.assertTrue(
            any(
                "No matching checks for changed files" in item
                for item in payload["warnings"]
            )
        )
        self.assertEqual(payload["checks"][0]["matchedFiles"], ["src/demo.py"])

    def test_inspect_readiness_reports_stored_verify_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-2026-06-15.json",
                verdict="passed",
                recorded_at="2026-06-15T05:00:00Z",
            )
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-2026-06-14.json",
                verdict="failed",
                recorded_at="2026-06-14T05:00:00Z",
            )
            (root / "docs/harness/evidence/verify-bad.json").write_text(
                "{not json",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    ["inspect", "--target", str(root), "--readiness", "--json"]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        evidence = payload["verifyEvidence"]
        self.assertEqual(
            evidence["latest"]["path"],
            "docs/harness/evidence/verify-2026-06-15.json",
        )
        self.assertEqual(evidence["latest"]["mode"], "run")
        self.assertEqual(evidence["latest"]["verdict"], "passed")
        self.assertEqual(evidence["latest"]["recordedAt"], "2026-06-15T05:00:00Z")
        reports = {item["path"]: item for item in evidence["reports"]}
        self.assertTrue(
            reports["docs/harness/evidence/verify-2026-06-15.json"]["schemaValid"]
        )
        self.assertFalse(
            reports["docs/harness/evidence/verify-bad.json"]["schemaValid"]
        )
        self.assertEqual(
            reports["docs/harness/evidence/verify-2026-06-14.json"]["verdict"],
            "failed",
        )
        self.assertTrue(any("failed" in item for item in payload["warnings"]))
        self.assertTrue(
            any("invalid verify evidence" in item for item in payload["warnings"])
        )
        self.assertTrue(
            any(
                "Review stored verify evidence" in item
                for item in payload["nextActions"]
            )
        )

    def test_inspect_readiness_warns_for_stale_verify_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            report = _write_verify_report(
                root,
                "docs/harness/evidence/verify-old.json",
                verdict="passed",
                recorded_at="2026-01-01T00:00:00Z",
            )
            os.utime(report, (0, 0))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness"])

            output = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Readiness: warning", output)
        self.assertIn("Verify evidence:", output)
        self.assertIn("verify-old.json: passed", output)
        self.assertIn("stale", output)

    def test_inspect_readiness_can_require_verify_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "inspect",
                        "--target",
                        str(root),
                        "--readiness",
                        "--json",
                        "--require-verify-evidence",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertTrue(payload["verifyEvidenceRequired"])
        self.assertTrue(
            any(
                "No stored verify evidence report" in item
                for item in payload["blockedReasons"]
            )
        )

    def test_inspect_readiness_reports_config_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "packageManager": "npm@10.0.0",
                        "scripts": {"test": "node --test"},
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "inspect",
                        "--target",
                        str(root),
                        "--readiness",
                        "--json",
                        "--package-manager",
                        "pnpm",
                        "--command",
                        "pnpm test",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        precedence = payload["configPrecedence"]
        self.assertEqual(precedence[0], "CLI --command: pnpm test")
        self.assertEqual(precedence[1], "CLI --package-manager: pnpm")
        self.assertIn("package.json packageManager: npm@10.0.0", precedence)

    def test_inspect_readiness_blocks_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertTrue(
            any("No project verification" in item for item in payload["blockedReasons"])
        )
        self.assertTrue(any("--command" in item for item in payload["nextActions"]))

    def test_inspect_readiness_reports_context_budget_and_duplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            repeated_block = "\n".join(
                f"- Shared routing rule {index}" for index in range(1, 7)
            )
            long_tail = "\n".join(f"- Extra local rule {index}" for index in range(320))
            (root / "AGENTS.md").write_text(
                "# Existing\n\n" + repeated_block + "\n" + long_tail + "\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n" + repeated_block + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        context = payload["contextBudget"]
        files = {item["path"]: item for item in context["instructionFiles"]}
        self.assertGreater(files["AGENTS.md"]["lineCount"], 300)
        self.assertIn("oversized", files["AGENTS.md"]["findings"])
        duplicates = context["duplicateInstructionBlocks"]
        self.assertTrue(
            any(
                item["left"] == "AGENTS.md" and item["right"] == "CLAUDE.md"
                for item in duplicates
            )
        )
        self.assertTrue(any("context budget" in item for item in payload["warnings"]))
        self.assertTrue(any("duplicate instruction" in item for item in payload["warnings"]))

    def test_inspect_readiness_reports_instruction_quality_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            low_signal = "\n".join(
                f"Project background placeholder paragraph {index} TODO later."
                for index in range(240)
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n" + low_signal + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        quality = payload["instructionQuality"]
        self.assertEqual(quality["summary"]["status"], "weak")
        files = {item["path"]: item for item in quality["files"]}
        agents = files["AGENTS.md"]
        self.assertEqual(agents["budgetStatus"], "over_hard")
        self.assertIn("missing_sections", agents["findings"])
        self.assertIn("placeholder_or_review_noise", agents["findings"])
        self.assertEqual(quality["largestFiles"][0]["path"], "AGENTS.md")
        self.assertTrue(
            any("instruction quality warning" in item for item in payload["warnings"])
        )
        self.assertTrue(
            any("instruction budget warning" in item for item in payload["warnings"])
        )

    def test_inspect_readiness_reports_governance_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "marketplace.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            (root / ".claude").mkdir()
            (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
            (root / ".codex").mkdir()
            (root / ".codex" / "config.toml").write_text(
                "sandbox = 'read-only'\n",
                encoding="utf-8",
            )
            (root / ".claude" / "hooks").mkdir()
            (root / ".claude" / "hooks" / "pre-tool-use.sh").write_text(
                "#!/bin/sh\n",
                encoding="utf-8",
            )
            (root / ".devcontainer").mkdir()
            (root / ".devcontainer" / "devcontainer.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            (root / "Dockerfile").write_text(
                "FROM python:3.13\n",
                encoding="utf-8",
            )
            (root / "compose.yaml").write_text(
                "services: {}\n",
                encoding="utf-8",
            )
            (root / ".husky").mkdir()
            (root / ".husky" / "pre-commit").write_text(
                "#!/bin/sh\n",
                encoding="utf-8",
            )
            (root / ".pre-commit-config.yaml").write_text(
                "repos: []\n",
                encoding="utf-8",
            )
            (root / ".sandbox").mkdir()
            (root / ".sandbox" / "policy.toml").write_text(
                "mode = 'deny'\n",
                encoding="utf-8",
            )
            (root / ".env.example").write_text(
                "API_TOKEN=\n",
                encoding="utf-8",
            )
            (root / ".env.local").write_text(
                "API_TOKEN=secret\n",
                encoding="utf-8",
            )
            (root / "skills" / "meta-harness").mkdir(parents=True)
            (root / "skills" / "meta-harness" / "SKILL.md").write_text(
                "---\nname: meta-harness\n---\n",
                encoding="utf-8",
            )
            (root / "install.sh").write_text(
                "#!/usr/bin/env bash\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "copilot-setup-steps.yml").write_text(
                "name: setup\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        inventory = {item["path"]: item for item in payload["governanceInventory"]}
        self.assertEqual(inventory[".mcp.json"]["category"], "mcp-config")
        self.assertIn("server-trust", inventory[".mcp.json"]["surfaces"])
        self.assertEqual(inventory[".claude/settings.json"]["category"], "agent-settings")
        self.assertEqual(inventory[".codex/config.toml"]["category"], "agent-settings")
        self.assertEqual(
            inventory[".devcontainer/devcontainer.json"]["category"],
            "devcontainer",
        )
        self.assertEqual(inventory["Dockerfile"]["category"], "container-runtime")
        self.assertIn("image-build", inventory["Dockerfile"]["surfaces"])
        self.assertEqual(inventory["compose.yaml"]["category"], "container-runtime")
        self.assertEqual(inventory[".sandbox/policy.toml"]["category"], "sandbox")
        self.assertEqual(inventory[".env.example"]["category"], "environment-template")
        self.assertEqual(
            inventory[".github/workflows/copilot-setup-steps.yml"]["category"],
            "agent-setup-workflow",
        )
        self.assertEqual(inventory[".claude/hooks/pre-tool-use.sh"]["category"], "hook")
        self.assertEqual(inventory[".husky/pre-commit"]["category"], "hook")
        self.assertEqual(inventory[".pre-commit-config.yaml"]["category"], "hook")
        self.assertEqual(inventory[".env.local"]["category"], "environment-local")
        self.assertEqual(
            inventory[".claude-plugin/marketplace.json"]["category"],
            "agent-plugin",
        )
        self.assertEqual(inventory["skills/meta-harness/SKILL.md"]["category"], "agent-skill")
        self.assertEqual(inventory["install.sh"]["category"], "installer-script")
        self.assertTrue(any("governance inventory" in item for item in payload["warnings"]))
        self.assertTrue(any("MCP" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("devcontainer" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("environment" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("hook" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("skill" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("plugin" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("installer" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_effectiveness_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "evals").mkdir()
            (root / "evals" / "harness-effectiveness.md").write_text(
                "# Harness Effectiveness Eval\n",
                encoding="utf-8",
            )
            (root / "benchmarks").mkdir()
            (root / "benchmarks" / "run_log.jsonl").write_text(
                "{\"agent\":\"baseline\",\"quality\":1.0,\"cost\":100}\n",
                encoding="utf-8",
            )
            (root / "score_harness.py").write_text(
                "print('score')\n",
                encoding="utf-8",
            )
            (root / "results.jsonl").write_text(
                "{\"verdict\":\"planned\"}\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        inventory = {item["path"]: item for item in payload["effectivenessInventory"]}
        self.assertEqual(
            inventory["evals/harness-effectiveness.md"]["category"], "eval-spec"
        )
        self.assertEqual(
            inventory["benchmarks/run_log.jsonl"]["category"], "result-log"
        )
        self.assertEqual(inventory["score_harness.py"]["category"], "scorer")
        self.assertEqual(inventory["results.jsonl"]["category"], "result-log")
        self.assertTrue(any("effectiveness eval" in item for item in payload["warnings"]))
        self.assertTrue(
            any("candidate-sensitive" in item for item in payload["reviewRequired"])
        )
        self.assertTrue(any("held-out" in item for item in payload["reviewRequired"]))

    def test_quickstart_guides_first_run_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / "specs" / "001-demo").mkdir(parents=True)
            (root / "specs" / "001-demo" / "spec.md").write_text(
                "# Demo Spec\n",
                encoding="utf-8",
            )
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            manifest_exists = (root / "docs" / "harness" / "manifest.json").exists()

        self.assertEqual(code, 0)
        self.assertEqual(agents, "# Existing\n\nProject-owned instructions.\n")
        self.assertFalse(manifest_exists)
        self.assertIn(f"Quickstart for {root.name}", output)
        self.assertIn("Detected stack: python", output)
        self.assertIn("Readiness: warning", output)
        self.assertIn("Source of truth:", output)
        self.assertIn("Existing files preserved:", output)
        self.assertIn("AGENTS.md", output)
        self.assertIn("Files HarnessForge would create:", output)
        self.assertIn("docs/harness/manifest.json", output)
        self.assertIn("Generated files needing project review:", output)
        self.assertIn("docs/harness/boundaries/change-contract.md", output)
        self.assertIn("Review required:", output)
        self.assertIn("MCP configuration detected", output)
        self.assertIn("Next commands:", output)
        self.assertIn("harnessforge init --target <repo> --dry-run", output)
        self.assertIn("harnessforge sync --check --target <repo>", output)

    def test_quickstart_interactive_json_reports_reproducible_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "quickstart",
                        "--target",
                        str(root),
                        "--interactive",
                        "--max-files",
                        "3",
                        "--component-limit",
                        "2",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(
            payload["schemaVersion"], "harnessforge.quickstartPlan.v1"
        )
        self.assertTrue(payload["interactive"])
        self.assertEqual(payload["target"]["root"], None)
        self.assertFalse(payload["execution"]["writesPerformed"])
        self.assertEqual(payload["decisions"]["agentFile"], "AGENTS.md")
        self.assertEqual(payload["decisions"]["maxFiles"], 3)
        self.assertEqual(payload["decisions"]["componentLimit"], 2)
        self.assertEqual(payload["repositoryScan"]["maxFiles"], 3)
        self.assertEqual(payload["repositoryScan"]["componentScan"]["limit"], 2)
        self.assertIn("--platform-contract", payload["reproducibleCommands"]["init"])
        self.assertIn("--max-files 3", payload["reproducibleCommands"]["init"])
        self.assertIn("--component-limit 2", payload["reproducibleCommands"]["init"])
        self.assertIn("harnessforge init", payload["reproducibleCommands"]["init"])

    def test_quickstart_interactive_skips_prompts_without_tty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["quickstart", "--target", str(root), "--interactive"])

        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("Quickstart for", output)
        self.assertIn("Interactive prompts skipped because stdin is not a TTY", output)
        self.assertFalse((root / "AGENTS.md").exists())

    def test_quickstart_reports_blocked_missing_verification_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertIn("Readiness: blocked", output)
        self.assertIn("Blocked reasons:", output)
        self.assertIn("No project verification check detected.", output)
        self.assertIn("--command", output)

    def test_quickstart_guides_existing_harness_to_audit_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                quickstart_code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()

        self.assertEqual(init_code, 0)
        self.assertEqual(quickstart_code, 0)
        self.assertIn("Existing files preserved:", output)
        self.assertNotIn("harnessforge init --target <repo>", output)
        self.assertIn("harnessforge audit --target <repo> --min-score 85", output)
        self.assertIn("harnessforge sync --check --target <repo>", output)

    def test_inspect_readiness_warns_for_specs_and_governance_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / "specs" / "architecture").mkdir(parents=True)
            (root / "specs" / "work-items").mkdir(parents=True)
            (root / "specs" / "foundation.md").write_text("# Foundation\n", encoding="utf-8")
            (root / "specs" / "architecture" / "design.md").write_text(
                "# Design\n",
                encoding="utf-8",
            )
            (root / "specs" / "work-items" / "0000-template.md").write_text(
                "# Work Item\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "copilot-setup-steps.yml").write_text(
                "name: setup\n",
                encoding="utf-8",
            )
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("structured project specs", payload["sourceOfTruth"])
        self.assertTrue(any("AGENTS.md" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("MCP" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("agent setup workflow" in item for item in payload["warnings"]))
        surfaces = payload["reviewSurfaces"]
        self.assertTrue(
            any(
                item["path"] == "AGENTS.md"
                and item["category"] == "instruction-router"
                and item["status"] == "pending_review"
                for item in surfaces
            )
        )
        self.assertTrue(
            any(
                item["path"] == ".mcp.json"
                and item["source"] == "governance-inventory"
                for item in surfaces
            )
        )
        self.assertEqual(payload["reviewStatusSummary"]["pendingReview"], 5)
        self.assertEqual(payload["reviewStatusSummary"]["acceptedAdvisory"], 0)

    def test_inspect_readiness_reports_spec_kit_quality_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / ".specify" / "memory").mkdir(parents=True)
            (root / ".specify" / "memory" / "constitution.md").write_text(
                "# Constitution\n",
                encoding="utf-8",
            )
            (root / ".specify" / "feature.json").write_text(
                json.dumps({"feature_directory": "specs/001-login"}),
                encoding="utf-8",
            )
            feature = root / "specs" / "001-login"
            (feature / "checklists").mkdir(parents=True)
            (feature / "spec.md").write_text(
                "# Feature Specification\n\n"
                "- **FR-001**: System MUST support login via "
                "[NEEDS CLARIFICATION: auth method].\n",
                encoding="utf-8",
            )
            (feature / "checklists" / "requirements.md").write_text(
                "# Checklist\n\n- [ ] CHK001 Are auth requirements clear?\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("Spec Kit project (.specify)", payload["sourceOfTruth"])
        self.assertIn("active feature specs: specs/001-login", payload["sourceOfTruth"])
        self.assertTrue(any("NEEDS CLARIFICATION" in item for item in payload["warnings"]))
        self.assertTrue(any("incomplete requirement checklist" in item for item in payload["warnings"]))
        self.assertTrue(any("missing plan.md" in item for item in payload["warnings"]))
        self.assertTrue(any("missing tasks.md" in item for item in payload["warnings"]))
        self.assertTrue(any("source-of-truth specs" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_aspec_and_workflow_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nFollow AGENTS only.\n",
                encoding="utf-8",
            )
            (root / "aspec" / "architecture").mkdir(parents=True)
            (root / "aspec" / "work-items").mkdir(parents=True)
            (root / "aspec" / "workflows").mkdir()
            (root / "aspec" / "architecture" / "system.md").write_text(
                "# Architecture\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "0000-template.md").write_text(
                "# Work Item Template\n",
                encoding="utf-8",
            )
            (root / "aspec" / "workflows" / "repair.yml").write_text(
                "steps: []\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("aspec", payload["sourceOfTruth"])
        self.assertIn(
            "work-item template: aspec/work-items/0000-template.md",
            payload["sourceOfTruth"],
        )
        self.assertTrue(any("workflow definitions" in item for item in payload["warnings"]))
        self.assertTrue(any("source-of-truth specs" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_workflow_and_work_item_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nFollow AGENTS only.\n",
                encoding="utf-8",
            )
            (root / "aspec" / "workflows").mkdir(parents=True)
            (root / "aspec" / "work-items").mkdir()
            (root / "aspec" / "workflows" / "repair.toml").write_text(
                'name = "repair"\n'
                'setup = ["make setup"]\n'
                'teardown = ["make clean"]\n'
                'remediation = ["python scripts/fix.py"]\n'
                'push = true\n'
                'credentials = ["GH_TOKEN"]\n'
                "[pull_request]\n"
                "enabled = true\n"
                "[ci]\n"
                "poll = true\n",
                encoding="utf-8",
            )
            (root / "workflows").mkdir()
            (root / "workflows" / "release.yml").write_text(
                "name: release\n"
                "on:\n"
                "  push:\n"
                "  pull_request:\n"
                "jobs:\n"
                "  release:\n"
                "    steps:\n"
                "      - run: python scripts/remediate.py\n"
                "        env:\n"
                "          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "0000-template.md").write_text(
                "# Work Item Template\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "1001-repair.md").write_text(
                "# Repair Work Item\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        workflows = {item["path"]: item for item in payload["workflowInventory"]}
        repair = workflows["aspec/workflows/repair.toml"]
        self.assertEqual(repair["format"], "toml")
        for surface in (
            "setup",
            "teardown",
            "remediation",
            "push",
            "pull-request",
            "ci-polling",
            "credentials",
        ):
            self.assertIn(surface, repair["surfaces"])
        release = workflows["workflows/release.yml"]
        self.assertEqual(release["format"], "yaml")
        self.assertIn("pull-request", release["surfaces"])
        self.assertIn("credentials", release["surfaces"])
        work_items = {item["path"]: item for item in payload["workItemInventory"]}
        self.assertEqual(
            work_items["aspec/work-items/0000-template.md"]["kind"],
            "template",
        )
        self.assertEqual(
            work_items["aspec/work-items/1001-repair.md"]["kind"],
            "work-item",
        )
        self.assertTrue(any("workflow inventory" in item for item in payload["warnings"]))
        self.assertTrue(any("credential" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_generated_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text("# edited\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        drift = {item["path"]: item for item in payload["generatedDrift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")
        self.assertTrue(any("generated drift" in item for item in payload["warnings"]))

    def test_inspect_readiness_text_reports_verdict_and_next_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness"])

        self.assertEqual(code, 0)
        self.assertIn("Readiness: blocked", stdout.getvalue())
        self.assertIn("Next actions:", stdout.getvalue())

    def test_sync_check_json_reports_ready_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text(
                "import unittest\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertEqual(payload["mode"], "check")
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["exitCode"], 0)
        self.assertEqual(payload["readiness"]["generatedDrift"], [])
        self.assertIn(
            "python -m unittest discover",
            payload["readiness"]["runnableChecks"],
        )

    def test_sync_check_verify_evidence_gate_passes_with_current_run_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-current.json",
                verdict="passed",
                mode="run",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "sync",
                        "--check",
                        "--target",
                        str(root),
                        "--json",
                        "--require-verify-evidence",
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["exitCode"], 0)
        self.assertTrue(payload["readiness"]["verifyEvidenceRequired"])
        self.assertEqual(payload["readiness"]["blockedReasons"], [])
        self.assertEqual(
            payload["readiness"]["verifyEvidence"]["latest"]["path"],
            "docs/harness/evidence/verify-current.json",
        )

    def test_sync_check_verify_evidence_gate_blocks_bad_reports(self) -> None:
        def prepare_failed(root: Path) -> None:
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-failed.json",
                verdict="failed",
            )

        def prepare_blocked(root: Path) -> None:
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-blocked.json",
                verdict="blocked",
                summary={
                    "total": 1,
                    "planned": 0,
                    "skipped": 0,
                    "blocked": 1,
                    "passed": 0,
                    "failed": 0,
                    "timedOut": 0,
                    "errors": 0,
                },
            )

        def prepare_plan(root: Path) -> None:
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-plan.json",
                verdict="planned",
                mode="plan",
                summary={
                    "total": 1,
                    "planned": 1,
                    "skipped": 0,
                    "blocked": 0,
                    "passed": 0,
                    "failed": 0,
                    "timedOut": 0,
                    "errors": 0,
                },
            )

        def prepare_timed_out(root: Path) -> None:
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-timeout.json",
                verdict="passed",
                summary={
                    "total": 1,
                    "planned": 0,
                    "skipped": 0,
                    "blocked": 0,
                    "passed": 0,
                    "failed": 0,
                    "timedOut": 1,
                    "errors": 0,
                },
            )

        def prepare_stale(root: Path) -> None:
            report = _write_verify_report(
                root,
                "docs/harness/evidence/verify-stale.json",
                verdict="passed",
            )
            os.utime(report, (0, 0))

        def prepare_invalid(root: Path) -> None:
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-passed.json",
                verdict="passed",
            )
            (root / "docs/harness/evidence/verify-invalid.json").write_text(
                "{not json",
                encoding="utf-8",
            )

        cases = (
            ("failed", prepare_failed, "verdict is failed"),
            ("blocked", prepare_blocked, "verdict is blocked"),
            ("plan", prepare_plan, "run-mode verify evidence is required"),
            ("timed_out", prepare_timed_out, "timed_out checks"),
            ("stale", prepare_stale, "stale"),
            ("invalid", prepare_invalid, "invalid"),
        )
        for name, prepare, needle in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "pyproject.toml").write_text(
                    "[project]\nname='demo'\n",
                    encoding="utf-8",
                )
                (root / "tests").mkdir()
                (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
                prepare(root)
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = main(
                        [
                            "sync",
                            "--check",
                            "--target",
                            str(root),
                            "--json",
                            "--require-verify-evidence",
                        ]
                    )

                payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 2)
            self.assertEqual(payload["verdict"], "blocked")
            self.assertEqual(payload["exitCode"], 2)
            self.assertTrue(payload["readiness"]["verifyEvidenceRequired"])
            self.assertTrue(
                any(needle in item for item in payload["readiness"]["blockedReasons"])
            )

    def test_sync_check_exits_warning_for_generated_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text("# edited\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "warning")
        self.assertEqual(payload["exitCode"], 1)
        drift = {item["path"]: item for item in payload["readiness"]["generatedDrift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")

    def test_sync_check_exits_blocked_for_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root)])

        self.assertEqual(code, 2)
        self.assertIn("Sync check: blocked", stdout.getvalue())
        self.assertIn("No project verification", stdout.getvalue())

    def test_sync_requires_check_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["sync", "--target", tmp])

        self.assertEqual(code, 2)
        self.assertIn("--check", stderr.getvalue())

    def test_verify_json_plan_reports_checks_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            command = (
                "python -c \"from pathlib import Path; "
                "Path('ran.txt').write_text('ran')\""
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--command",
                        command,
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(payload["schemaVersion"], "harnessforge.verify.v1")
        self.assertEqual(payload["mode"], "plan")
        self.assertEqual(payload["verdict"], "planned")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertEqual(payload["summary"]["planned"], 1)
        self.assertEqual(payload["checks"][0]["source"], "explicit")
        self.assertEqual(payload["checks"][0]["status"], "planned")
        self.assertIsNone(payload["checks"][0]["exitCode"])
        self.assertIsNone(payload["target"]["root"])

    def test_verify_json_blocks_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["verify", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertEqual(payload["summary"]["blocked"], 1)
        self.assertTrue(
            any("No project verification" in item for item in payload["blockedReasons"])
        )

    def test_verify_run_executes_explicit_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; "
                "Path('ran.txt').write_text('ran', encoding='utf-8'); "
                "print('verification ok')"
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--run",
                        "--yes",
                        "--command",
                        command,
                    ]
                )

            payload = json.loads(stdout.getvalue())
            marker_exists = marker.exists()

        self.assertEqual(code, 0)
        self.assertTrue(marker_exists)
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["verdict"], "passed")
        self.assertTrue(payload["execution"]["commandsExecuted"])
        self.assertIsInstance(payload["execution"]["startedAt"], str)
        self.assertIsInstance(payload["execution"]["endedAt"], str)
        self.assertGreaterEqual(payload["execution"]["durationMs"], 0)
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["checks"][0]["status"], "passed")
        self.assertEqual(payload["checks"][0]["exitCode"], 0)
        self.assertIn("verification ok", payload["checks"][0]["stdoutPreview"])
        self.assertIsNone(payload["target"]["root"])

    def test_verify_run_requires_yes_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; "
                "Path('ran.txt').write_text('ran', encoding='utf-8')"
            )
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--run",
                        "--command",
                        command,
                    ]
                )

        self.assertEqual(code, 2)
        self.assertFalse(marker.exists())
        self.assertIn("requires --yes", stderr.getvalue())

    def test_verify_run_reports_failed_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = _python_command(
                "import sys; "
                "print('before failure'); "
                "sys.stderr.write('verification failed\\n'); "
                "raise SystemExit(7)"
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--run",
                        "--yes",
                        "--command",
                        command,
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "failed")
        self.assertEqual(payload["summary"]["failed"], 1)
        self.assertEqual(payload["checks"][0]["status"], "failed")
        self.assertEqual(payload["checks"][0]["exitCode"], 7)
        self.assertIn("before failure", payload["checks"][0]["stdoutPreview"])
        self.assertIn("verification failed", payload["checks"][0]["stderrPreview"])

    def test_verify_run_blocks_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    ["verify", "--target", str(root), "--json", "--run", "--yes"]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 2)
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["verdict"], "blocked")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertEqual(payload["summary"]["blocked"], 1)

    def test_verify_run_reports_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = _python_command("import time; time.sleep(2)")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--run",
                        "--yes",
                        "--timeout-seconds",
                        "0.1",
                        "--command",
                        command,
                    ]
                )

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "failed")
        self.assertEqual(payload["summary"]["timedOut"], 1)
        self.assertEqual(payload["checks"][0]["status"], "timed_out")
        self.assertIsNone(payload["checks"][0]["exitCode"])

    def test_verify_json_report_writes_target_relative_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = _python_command("print('report ok')")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--run",
                        "--yes",
                        "--command",
                        command,
                        "--json-report",
                        " docs\\harness\\evidence\\verify.json ",
                    ]
                )

            report_path = root / "docs" / "harness" / "evidence" / "verify.json"
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["verdict"], "passed")
        self.assertIn(
            "Verify JSON report written to docs/harness/evidence/verify.json",
            stdout.getvalue(),
        )
        self.assertIn("Verify run: passed", stdout.getvalue())

    def test_verify_evidence_summary_omits_command_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = _python_command(
                "import sys; print('sensitive ' + 'stdout'); "
                "sys.stderr.write('sensitive ' + 'stderr\\n')"
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--run",
                        "--yes",
                        "--command",
                        command,
                        "--evidence-summary",
                        "docs/harness/evidence/verify-summary.json",
                    ]
                )

            summary_path = root / "docs/harness/evidence/verify-summary.json"
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            raw_payload = summary_path.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(payload["schemaVersion"], "harnessforge.verifySummary.v1")
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["verdict"], "passed")
        self.assertFalse(payload["privacy"]["stdoutStderrCaptured"])
        self.assertNotIn("stdoutPreview", raw_payload)
        self.assertNotIn("stderrPreview", raw_payload)
        self.assertNotIn("sensitive stdout", raw_payload)
        self.assertNotIn("sensitive stderr", raw_payload)
        self.assertIn(
            "Verify evidence summary written to docs/harness/evidence/verify-summary.json",
            stdout.getvalue(),
        )

    def test_verify_json_report_keeps_json_stdout_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = _python_command("print('report ok')")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "verify",
                        "--target",
                        str(root),
                        "--json",
                        "--run",
                        "--yes",
                        "--command",
                        command,
                        "--json-report",
                        "reports/verify.json",
                    ]
                )

            stdout_payload = json.loads(stdout.getvalue())
            file_payload = json.loads(
                (root / "reports" / "verify.json").read_text(encoding="utf-8")
            )

        self.assertEqual(code, 0)
        self.assertEqual(stdout_payload["verdict"], "passed")
        self.assertEqual(file_payload, stdout_payload)

    def test_verify_json_report_rejects_paths_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            outside = Path(tmp) / "verify.json"
            for report_path in (
                "../verify.json",
                "..\\verify.json",
                str(outside),
                "C:\\temp\\verify.json",
                "C:verify.json",
                "\\verify.json",
                "\\\\server\\share\\verify.json",
            ):
                with self.subTest(report_path=report_path):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        code = main(
                            [
                                "verify",
                                "--target",
                                str(root),
                                "--json-report",
                                report_path,
                            ]
                        )

                    self.assertEqual(code, 2)
                    self.assertIn("report paths", stderr.getvalue())

            self.assertFalse(outside.exists())

    def test_blueprint_list_and_show_json(self) -> None:
        list_stdout = io.StringIO()
        with contextlib.redirect_stdout(list_stdout):
            list_code = main(["blueprint", "list", "--json"])
        show_stdout = io.StringIO()
        with contextlib.redirect_stdout(show_stdout):
            show_code = main(["blueprint", "show", "agentic-app", "--json"])

        list_payload = json.loads(list_stdout.getvalue())
        show_payload = json.loads(show_stdout.getvalue())

        self.assertEqual(list_code, 0)
        self.assertEqual(show_code, 0)
        ids = {item["id"] for item in list_payload["blueprints"]}
        self.assertIn("agentic-app", ids)
        self.assertIn("spec-driven", ids)
        self.assertIn("open-source-library", ids)
        self.assertIn("internal-service", ids)
        self.assertIn("infrastructure-iac", ids)
        self.assertEqual(show_payload["id"], "agentic-app")
        self.assertIn("reviewQuestions", show_payload)
        self.assertIn("generatedFiles", show_payload)

    def test_blueprint_apply_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--dry-run",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            blueprint_file = root / "docs/harness/blueprints/agentic-app.md"

        self.assertEqual(code, 0)
        self.assertFalse(blueprint_file.exists())
        writes = {item["path"]: item for item in payload["writes"]}
        self.assertEqual(
            writes["docs/harness/blueprints/agentic-app.md"]["status"],
            "would_write",
        )

    def test_blueprint_apply_requires_yes_non_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--json",
                    ]
                )

            blueprint_file = root / "docs/harness/blueprints/agentic-app.md"

        self.assertEqual(code, 2)
        self.assertFalse(blueprint_file.exists())
        self.assertIn("requires --yes", stderr.getvalue())

    def test_blueprint_apply_writes_reviewed_artifacts_and_preserves_existing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                apply_code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--yes",
                        "--json",
                    ]
                )
            first_payload = json.loads(stdout.getvalue())
            blueprint_file = root / "docs/harness/blueprints/agentic-app.md"
            manifest_file = root / "docs/harness/blueprints/manifest.json"
            blueprint_text = blueprint_file.read_text(encoding="utf-8")
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            blueprint_file.write_text("local blueprint edits\n", encoding="utf-8")
            second_stdout = io.StringIO()
            with contextlib.redirect_stdout(second_stdout):
                second_code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--yes",
                        "--json",
                    ]
                )
            second_payload = json.loads(second_stdout.getvalue())
            final_blueprint_text = blueprint_file.read_text(encoding="utf-8")

        self.assertEqual(apply_code, 0)
        self.assertEqual(second_code, 0)
        self.assertIn("Agentic Application Blueprint", blueprint_text)
        self.assertIn("Review Required", blueprint_text)
        self.assertIn("agentic-app", manifest["appliedBlueprints"])
        first_writes = {item["path"]: item for item in first_payload["writes"]}
        self.assertEqual(
            first_writes["docs/harness/blueprints/agentic-app.md"]["status"],
            "written",
        )
        second_writes = {item["path"]: item for item in second_payload["writes"]}
        self.assertEqual(
            second_writes["docs/harness/blueprints/agentic-app.md"]["status"],
            "skipped",
        )
        self.assertEqual(final_blueprint_text, "local blueprint edits\n")

    def test_blueprint_apply_force_overwrites_existing_blueprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_file = root / "docs/harness/blueprints/agentic-app.md"
            blueprint_file.parent.mkdir(parents=True)
            blueprint_file.write_text("local blueprint edits\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--force",
                        "--yes",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            blueprint_text = blueprint_file.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        writes = {item["path"]: item for item in payload["writes"]}
        self.assertEqual(
            writes["docs/harness/blueprints/agentic-app.md"]["status"],
            "updated",
        )
        self.assertIn("Agentic Application Blueprint", blueprint_text)

    def test_blueprint_apply_preserves_non_generated_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_file = root / "docs/harness/blueprints/manifest.json"
            manifest_file.parent.mkdir(parents=True)
            manifest_file.write_text('{"owner":"project"}\n', encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--yes",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            manifest_text = manifest_file.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        writes = {item["path"]: item for item in payload["writes"]}
        self.assertEqual(
            writes["docs/harness/blueprints/manifest.json"]["status"],
            "skipped",
        )
        self.assertEqual(manifest_text, '{"owner":"project"}\n')

    def test_blueprint_apply_does_not_claim_skipped_existing_blueprint(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_file = root / "docs/harness/blueprints/agentic-app.md"
            blueprint_file.parent.mkdir(parents=True)
            blueprint_file.write_text("project-owned blueprint\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "blueprint",
                        "apply",
                        "agentic-app",
                        "--target",
                        str(root),
                        "--yes",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            manifest = json.loads(
                (root / "docs/harness/blueprints/manifest.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(code, 0)
        writes = {item["path"]: item for item in payload["writes"]}
        self.assertEqual(
            writes["docs/harness/blueprints/agentic-app.md"]["status"],
            "skipped",
        )
        blueprint_manifest = manifest["appliedBlueprints"]["agentic-app"]
        self.assertNotIn(
            "docs/harness/blueprints/agentic-app.md",
            blueprint_manifest["generatedFiles"],
        )
        self.assertEqual(
            blueprint_manifest["preservedFiles"][
                "docs/harness/blueprints/agentic-app.md"
            ]["ownership"],
            "project-owned-preserved",
        )

    def test_init_can_scaffold_optional_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--with-ci-workflow",
                    ]
                )

            ci = root / ".github/workflows/harnessforge.yml"
            self_heal = root / ".github/workflows/harness-self-heal.yml"
            ci_exists = ci.exists()
            self_heal_exists = self_heal.exists()

        self.assertEqual(code, 0)
        self.assertTrue(ci_exists)
        self.assertFalse(self_heal_exists)
        self.assertIn("Optional workflow scaffold review required", stdout.getvalue())
        self.assertIn("<reviewed-commit-sha>", stdout.getvalue())
        self.assertIn("permissions", stdout.getvalue())
        self.assertIn(
            "sync preflight warnings are advisory by default", stdout.getvalue()
        )
        self.assertIn("verify evidence gating is off by default", stdout.getvalue())

    def test_init_can_generate_macos_only_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--platform-contract",
                        "macos-only",
                    ]
                )

            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            init_sh_exists = (root / "init.sh").exists()
            init_ps1_exists = (root / "init.ps1").exists()

        self.assertEqual(code, 0)
        self.assertTrue(init_sh_exists)
        self.assertFalse(init_ps1_exists)
        self.assertIn("macosOnly", manifest["supportedPlatforms"])
        self.assertNotIn("init.ps1", manifest["requiredFiles"])

    def test_init_records_platform_source_review_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["init", "--target", str(root)])

            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            change_contract = (
                root / "docs/harness/boundaries/change-contract.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        review = manifest["platformSourceReview"]
        self.assertEqual(review["lastReviewed"], "2026-06-15")
        self.assertTrue(review["reviewRequiredBeforePlatformChange"])
        source_ids = {source["id"] for source in review["sources"]}
        self.assertIn("python-devguide-versions", source_ids)
        self.assertIn("github-actions-hosted-runners", source_ids)
        self.assertIn("github-runner-images-windows-vs2026", source_ids)
        self.assertIn("current primary-source evidence", change_contract)
        self.assertIn("runner labels", change_contract)

    def test_update_drift_report_detects_modified_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text(
                "# edited\n\nlocal change\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                report_code = main(
                    [
                        "update",
                        "--target",
                        str(root),
                        "--drift-report",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            claude_text = (root / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(init_code, 0)
        self.assertEqual(report_code, 0)
        drift = {item["path"]: item for item in payload["drift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")
        self.assertEqual(drift["AGENTS.md"]["ownership"], "generated")
        self.assertEqual(
            drift["AGENTS.md"]["recommendedAction"],
            "review-local-edits-before-overwrite",
        )
        self.assertFalse(claude_text.startswith("# edited"))

    def test_update_apply_refreshes_unchanged_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            old_content = "# old generated agents\n"
            (root / "AGENTS.md").write_text(old_content, encoding="utf-8")
            manifest_path = root / "docs/harness/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["generatedFiles"]["AGENTS.md"]["contentSha256"] = (
                hashlib.sha256(old_content.encode("utf-8")).hexdigest()
            )
            manifest["generatedFiles"]["AGENTS.md"]["templateSha256"] = "old-template"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                update_code = main(
                    ["update", "--target", str(root), "--apply", "--yes", "--json"]
                )
            payload = json.loads(stdout.getvalue())
            agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual(init_code, 0)
        self.assertEqual(update_code, 0)
        writes = {item["path"]: item for item in payload["writes"]}
        self.assertEqual(writes["AGENTS.md"]["status"], "updated")
        self.assertIn("generated-owned template changed", writes["AGENTS.md"]["reason"])
        self.assertIn("## Project overview", agents_text)
        self.assertNotEqual(agents_text, old_content)

    def test_init_records_existing_files_as_project_owned_without_initial_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                "# Existing\n\nKeep local instructions.\n",
                encoding="utf-8",
            )
            init_stdout = io.StringIO()
            with contextlib.redirect_stdout(init_stdout):
                init_code = main(["init", "--target", str(root)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                report_code = main(
                    [
                        "update",
                        "--target",
                        str(root),
                        "--drift-report",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(report_code, 0)
        self.assertIn("Existing files preserved", init_stdout.getvalue())
        self.assertIn("HARNESSFORGE_AGENTS.md", init_stdout.getvalue())
        drift = {item["path"]: item for item in payload["drift"]}
        self.assertEqual(drift["AGENTS.md"]["ownership"], "project")
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "unchanged")

    def test_init_can_enhance_existing_instruction_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\nKeep local instructions.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                init_code = main(
                    ["init", "--target", str(root), "--enhance-existing"]
                )
            with contextlib.redirect_stdout(io.StringIO()):
                audit_code = main(
                    ["audit", "--target", str(root), "--min-score", "100"]
                )
            report_stdout = io.StringIO()
            with contextlib.redirect_stdout(report_stdout):
                report_code = main(["report", "--target", str(root), "--json"])
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            report = json.loads(report_stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertEqual(report_code, 0)
        self.assertIn("ENHANCED AGENTS.md", stdout.getvalue())
        self.assertIn("Keep local instructions.", agents)
        self.assertIn("HarnessForge Quality Addendum", agents)
        self.assertEqual(report["skillWiring"]["status"], "wired")
        self.assertIn("AGENTS.md", report["skillWiring"]["instructionRoutes"])

    def test_init_enhance_existing_dry_run_json_reports_review_plan(self) -> None:
        repeated = (
            "Always inspect the project-owned verification docs before changing "
            "shared behavior or accepting generated guidance."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n"
                "## Build\n\n"
                "Use /Users/person/private/repo for local scripts.\n\n"
                "You must use Antigravity and agy for research.\n\n"
                "Never run tests in this repository.\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--enhance-existing",
                        "--dry-run",
                        "--json",
                        "--command",
                        command,
                    ]
                )
            raw = stdout.getvalue()
            payload = json.loads(raw)
            marker_exists = marker.exists()

        files = {
            item["path"]: item
            for item in payload["enhanceExistingPlan"]["files"]
        }
        agents = files["AGENTS.md"]
        finding_types = {item["type"] for item in agents["findings"]}

        self.assertEqual(code, 0)
        self.assertFalse(marker_exists)
        self.assertNotIn(str(root), raw)
        self.assertNotIn("/Users/person", raw)
        self.assertEqual(payload["schemaVersion"], "harnessforge.initPlan.v1")
        self.assertEqual(payload["target"]["root"], None)
        self.assertEqual(payload["mode"], "dry_run")
        self.assertEqual(
            payload["enhanceExistingPlan"]["schemaVersion"],
            "harnessforge.enhanceExistingPlan.v1",
        )
        self.assertEqual(agents["status"], "would_enhance")
        self.assertEqual(agents["sections"][0]["title"], "Existing")
        self.assertIn("Build", {section["title"] for section in agents["sections"]})
        self.assertIn("local_absolute_path", finding_types)
        self.assertIn("user_specific_tool_mandate", finding_types)
        self.assertIn("verification_conflict", finding_types)
        self.assertIn("duplicated_instruction_block", finding_types)
        self.assertIn("boundary", agents["taskClassGuidance"]["taskClasses"])
        self.assertIn("verification", agents["taskClassGuidance"]["taskClasses"])
        self.assertEqual(agents["ruleLifecycle"]["source"], "AGENTS.md")
        self.assertIn(
            "the user-specific mandate is replaced by project-owned tooling guidance",
            agents["ruleLifecycle"]["retireWhen"],
        )
        self.assertIn(
            "the local path is replaced by a repo-relative path or setup variable",
            agents["ruleLifecycle"]["retireWhen"],
        )
        self.assertEqual(
            agents["proposedEdits"][0]["action"],
            "append_quality_addendum",
        )

    def test_init_json_requires_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["init", "--target", str(root), "--json"])

        self.assertEqual(code, 2)
        self.assertIn("--dry-run", stderr.getvalue())

    def test_init_enhance_existing_dry_run_json_recommends_section_aware_edits(
        self,
    ) -> None:
        repeated = (
            "Always inspect the project-owned verification docs before changing "
            "shared behavior or accepting generated guidance."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n"
                "## Build\n\n"
                "Use /Users/person/private/repo for local scripts.\n\n"
                "You must use Antigravity and agy for research.\n\n"
                "Never run tests in this repository.\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--enhance-existing",
                        "--dry-run",
                        "--json",
                    ]
                )
            raw = stdout.getvalue()
            payload = json.loads(raw)

        files = {
            item["path"]: item
            for item in payload["enhanceExistingPlan"]["files"]
        }
        agents = files["AGENTS.md"]
        coverage = agents["sectionCoverage"]
        proposed_edits = agents["proposedEdits"]
        actions = {item["action"] for item in proposed_edits}

        self.assertEqual(code, 0)
        self.assertNotIn("/Users/person", raw)
        self.assertEqual(coverage["recommendedShape"], "canonical_instruction")
        self.assertIn("Build and test commands", coverage["present"])
        self.assertIn("Project overview", coverage["missing"])
        self.assertIn("Security considerations", coverage["missing"])
        self.assertIn("append_quality_addendum", actions)
        self.assertIn("add_missing_section", actions)
        self.assertIn("generalize_local_absolute_path", actions)
        self.assertIn("replace_user_specific_tool_mandate", actions)
        self.assertIn("replace_verification_conflict", actions)
        self.assertIn("consolidate_duplicate_instruction_block", actions)
        self.assertTrue(all(item["reviewRequired"] for item in proposed_edits))
        self.assertTrue(
            any(
                item["action"] == "add_missing_section"
                and item["section"] == "Security considerations"
                for item in proposed_edits
            )
        )

    def test_init_enhance_existing_dry_run_json_includes_patch_previews(
        self,
    ) -> None:
        repeated = (
            "Always inspect the project-owned verification docs before changing "
            "shared behavior or accepting generated guidance."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n"
                "## Build\n\n"
                "Use /Users/person/private/repo for local scripts.\n\n"
                "You must use Antigravity and agy for research.\n\n"
                "Never run tests in this repository.\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--enhance-existing",
                        "--dry-run",
                        "--json",
                    ]
                )
            raw = stdout.getvalue()
            payload = json.loads(raw)

        files = {
            item["path"]: item
            for item in payload["enhanceExistingPlan"]["files"]
        }
        agents = files["AGENTS.md"]
        previews = {
            item["action"]: item["patchPreview"]
            for item in agents["proposedEdits"]
        }

        self.assertEqual(code, 0)
        self.assertNotIn("/Users/person", raw)
        self.assertIn("patchPreviews", payload["enhanceExistingPlan"]["summary"])
        self.assertGreater(payload["enhanceExistingPlan"]["summary"]["patchPreviews"], 0)
        self.assertFalse(previews["add_missing_section"]["applySupported"])
        self.assertTrue(previews["add_missing_section"]["reviewOnly"])
        self.assertEqual(previews["add_missing_section"]["format"], "reviewed_hunks")
        self.assertIn(
            "## Security considerations",
            "\n".join(previews["add_missing_section"]["hunks"][0]["addedLines"]),
        )
        self.assertEqual(
            previews["generalize_local_absolute_path"]["hunks"][0]["removed"],
            "[REDACTED_LOCAL_ABSOLUTE_PATH]",
        )
        self.assertIn(
            "<repo-relative-path-or-setup-variable>",
            previews["generalize_local_absolute_path"]["hunks"][0]["added"],
        )
        self.assertEqual(
            previews["replace_user_specific_tool_mandate"]["hunks"][0]["operation"],
            "replace_reviewed_text",
        )
        self.assertEqual(
            previews["consolidate_duplicate_instruction_block"]["hunks"][0]["operation"],
            "remove_duplicate_or_replace_with_route",
        )
        self.assertTrue(
            all(
                not preview["applySupported"]
                for preview in previews.values()
            )
        )

    def test_enhance_json_reports_existing_instruction_plan_without_writes(
        self,
    ) -> None:
        repeated = (
            "Always inspect the project-owned verification docs before changing "
            "shared behavior or accepting generated guidance."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n"
                "## Build\n\n"
                "Use /Users/person/private/repo for local scripts.\n\n"
                "You must use Antigravity and agy for research.\n\n"
                "Never run tests in this repository.\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "enhance",
                        "--target",
                        str(root),
                        "--json",
                        "--command",
                        command,
                    ]
                )
            raw = stdout.getvalue()
            payload = json.loads(raw)
            marker_exists = marker.exists()

        agents = {
            item["path"]: item
            for item in payload["enhanceExistingPlan"]["files"]
        }["AGENTS.md"]

        self.assertEqual(code, 0)
        self.assertFalse(marker_exists)
        self.assertNotIn(str(root), raw)
        self.assertNotIn("/Users/person", raw)
        self.assertEqual(payload["schemaVersion"], "harnessforge.enhanceCommand.v1")
        self.assertEqual(payload["mode"], "review")
        self.assertEqual(payload["target"]["root"], None)
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertFalse(payload["execution"]["writesPerformed"])
        self.assertEqual(
            payload["enhanceExistingPlan"]["schemaVersion"],
            "harnessforge.enhanceExistingPlan.v1",
        )
        self.assertIn("instructionQuality", agents)
        self.assertIn("recommendations", agents["instructionQuality"])
        self.assertIn("taskClassGuidance", agents)
        self.assertIn("ruleLifecycle", agents)
        self.assertIn("boundary", agents["taskClassGuidance"]["taskClasses"])
        self.assertIn("verification", agents["taskClassGuidance"]["taskClasses"])
        self.assertEqual(agents["ruleLifecycle"]["owner"], "project maintainer review")
        self.assertIn("patchPreviews", payload["enhanceExistingPlan"]["summary"])
        self.assertIn("local_absolute_path", {item["type"] for item in agents["findings"]})

    def test_enhance_json_reports_nested_instruction_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "workspaces": ["packages/*"],
                        "scripts": {"test": "node --test"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n## Verification\n\nRun the project checks.\n",
                encoding="utf-8",
            )
            for package in ("api", "web"):
                package_root = root / "packages" / package
                package_root.mkdir(parents=True)
                (package_root / "package.json").write_text(
                    json.dumps(
                        (
                            {
                                "name": package,
                                "scripts": {"test": "vitest"},
                            }
                            if package == "web"
                            else {"name": package}
                        )
                    ),
                    encoding="utf-8",
                )
            (root / "packages" / "web" / "README.md").write_text(
                "# Web\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "enhance",
                        "--target",
                        str(root),
                        "--json",
                        "--component-limit",
                        "2",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        plan = payload["nestedInstructionPlan"]
        self.assertEqual(code, 0)
        self.assertEqual(payload["repositoryScan"]["componentScan"]["limit"], 2)
        self.assertEqual(plan["status"], "review_required")
        self.assertEqual(plan["candidateCount"], 1)
        self.assertEqual(plan["omittedCandidateCount"], 1)
        self.assertEqual(
            plan["omittedCandidateComponents"][0]["path"],
            "packages/web",
        )
        self.assertFalse(plan["writeByDefault"])

    def test_enhance_text_summarizes_existing_instruction_plan(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\n"
                "## Build\n\n"
                "Never run tests in this repository.\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["enhance", "--target", str(root)])
            output = stdout.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("Enhance review for ", output)
        self.assertIn("Mode: review only", output)
        self.assertIn("Files reviewed: 1", output)
        self.assertIn("Nested AGENTS.md candidates: 0", output)
        self.assertIn("Omitted nested AGENTS.md candidates: 0", output)
        self.assertIn("AGENTS.md", output)
        self.assertIn("verification_conflict", output)
        self.assertIn("add_missing_section", output)
        self.assertIn("No files were changed.", output)

    def test_audit_requires_explicit_override_for_local_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "README.md").write_text(
                "Local checkout was /Users/person/private/repo\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                strict_code = main(
                    ["audit", "--target", str(root), "--min-score", "100"]
                )
            with contextlib.redirect_stdout(io.StringIO()):
                allowed_code = main(
                    [
                        "audit",
                        "--target",
                        str(root),
                        "--min-score",
                        "85",
                        "--allow-local-absolute-paths",
                    ]
                )

        self.assertEqual(init_code, 0)
        self.assertEqual(strict_code, 1)
        self.assertEqual(allowed_code, 0)
        self.assertIn("Durable harness text avoids local absolute paths", stdout.getvalue())

    def test_update_without_apply_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["update", "--target", str(root)])

            self.assertEqual(code, 0)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("No files changed", stdout.getvalue())

    def test_init_rejects_unsafe_agent_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["init", "--target", tmp, "--agent-file", "../AGENTS.md"])

        self.assertEqual(code, 2)
        self.assertIn("--agent-file", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
