from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harnessforge.cli import main


def _python_command(script: str) -> str:
    return f"{json.dumps(sys.executable)} -c {json.dumps(script)}"


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
            (root / "docs" / "harness").mkdir()
            (root / "docs" / "harness" / "source-record-example.json").write_text(
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
        self.assertIn("pyproject.toml", {item["path"] for item in payload["manifests"]})
        self.assertIn("AGENTS.md", {item["path"] for item in payload["sourceOfTruth"]})
        self.assertIn(
            "docs/harness/source-record-example.json",
            {item["path"] for item in payload["reviewRequired"]},
        )
        self.assertTrue(
            any(item["language"] == "python" for item in payload["languageBreakdown"])
        )

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
        self.assertTrue(payload["summary"]["componentsTruncated"])
        self.assertEqual(payload["limits"]["maxComponents"], 80)
        self.assertIn("80-component detection limit", " ".join(payload["warnings"]))

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
            "verifyEvidence",
        ):
            self.assertIn(key, payload)
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
        self.assertTrue(state["progress.md"])
        self.assertTrue(state["session-handoff.md"])
        self.assertIn("docs/harness/evidence-log.md", state)
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
        self.assertEqual(payload["audit"]["overall"], 100)
        self.assertEqual(payload["drift"]["summary"]["actionable"], 0)
        self.assertIn("fileCount", payload["index"]["summary"])
        self.assertEqual(payload["verifyEvidence"]["latest"]["verdict"], "passed")
        self.assertEqual(payload["effectiveness"]["verdict"], "blocked")
        self.assertEqual(payload["firstAgentTask"]["status"], "pending_review")
        self.assertEqual(payload["platform"]["contract"], "cross-platform")
        self.assertIn("Run harnessforge report", payload["nextActions"][0])

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
        self.assertIn("## Next Actions", markdown)
        self.assertEqual(payload["schemaVersion"], "harnessforge.report.v1")

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
        self.assertIn("docs/harness/change-contract.md", output)
        self.assertIn("Review required:", output)
        self.assertIn("MCP configuration detected", output)
        self.assertIn("Next commands:", output)
        self.assertIn("harnessforge init --target <repo> --dry-run", output)
        self.assertIn("harnessforge sync --check --target <repo>", output)

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
                code = main(["verify", "--target", str(root), "--json", "--run"])

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
                        "--with-self-heal-workflow",
                    ]
                )

            ci = root / ".github/workflows/harnessforge.yml"
            self_heal = root / ".github/workflows/harness-self-heal.yml"
            ci_exists = ci.exists()
            self_heal_exists = self_heal.exists()

        self.assertEqual(code, 0)
        self.assertTrue(ci_exists)
        self.assertTrue(self_heal_exists)
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
                root / "docs/harness/change-contract.md"
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
                update_code = main(["update", "--target", str(root), "--apply", "--json"])
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
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual(init_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertIn("ENHANCED AGENTS.md", stdout.getvalue())
        self.assertIn("Keep local instructions.", agents)
        self.assertIn("HarnessForge Quality Addendum", agents)

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
