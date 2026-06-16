from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from harnessforge.generation.generate import create_harness
from harnessforge.github_action import _output, run_from_env


def _parse_github_output(text: str) -> dict[str, str]:
    values = {}
    lines = iter(text.splitlines())
    for line in lines:
        if "<<" in line:
            key, delimiter = line.split("<<", 1)
            value_lines = []
            for value_line in lines:
                if value_line == delimiter:
                    break
                value_lines.append(value_line)
            values[key] = "\n".join(value_lines)
        else:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def _python_command(script: str) -> str:
    return f"{json.dumps(sys.executable)} -c {json.dumps(script)}"


def _write_verify_report(
    root: Path,
    relative_path: str,
    *,
    verdict: str = "passed",
    mode: str = "run",
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
            "startedAt": "2026-06-15T05:00:00Z",
            "endedAt": "2026-06-15T05:00:00Z",
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
        "checks": [],
        "blockedReasons": [],
        "warnings": [],
        "artifacts": [],
    }
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return path


def _write_finalize_fixture(root: Path) -> None:
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
        "Do not expose secrets. Preserve security boundaries and project docs.\n\n"
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


class GitHubActionTests(unittest.TestCase):
    def test_action_manifest_quotes_description_values_with_colons(self) -> None:
        action = Path(__file__).resolve().parents[1] / "action.yml"

        lines = action.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if not stripped.startswith("description: "):
                continue
            value = stripped.split(": ", 1)[1]
            if ":" in value:
                self.assertTrue(
                    value.startswith(("\"", "'")),
                    f"action.yml:{line_number} description with colon must be quoted",
                )

    def test_action_sets_python_safe_path(self) -> None:
        action = Path(__file__).resolve().parents[1] / "action.yml"

        self.assertIn(
            'PYTHONSAFEPATH: "1"',
            action.read_text(encoding="utf-8"),
        )

    def test_action_docs_separate_action_from_workflows(self) -> None:
        root = Path(__file__).resolve().parents[1]
        docs = (root / "docs/action.md").read_text(encoding="utf-8")

        self.assertIn("The Action is separate", docs)
        self.assertIn("does not schedule jobs", docs)
        self.assertIn("refresh research", docs)
        self.assertIn("open pull requests by itself", docs)
        self.assertIn("project-owned generated files", docs)
        self.assertIn("not the live HarnessForge repository workflow", docs)

    def test_action_manifest_and_docs_expose_sync_preflight(self) -> None:
        root = Path(__file__).resolve().parents[1]
        action = (root / "action.yml").read_text(encoding="utf-8")
        docs = (root / "docs/action.md").read_text(encoding="utf-8")

        self.assertIn(
            "audit, init, update, sync, verify, report, release-check, "
            "finalize-review, or doctor",
            action,
        )
        self.assertIn("require-verify-evidence", action)
        self.assertIn("sync-command", action)
        self.assertIn("readiness-verdict", action)
        self.assertIn("sync-exit-code", action)
        self.assertIn("command: sync", docs)
        self.assertIn("require-verify-evidence", docs)
        self.assertIn("sync-command", docs)
        self.assertIn("readiness-verdict", docs)

    def test_action_manifest_and_docs_expose_report_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        action = (root / "action.yml").read_text(encoding="utf-8")
        docs = (root / "docs/action.md").read_text(encoding="utf-8")

        self.assertIn("command: report", docs)
        self.assertIn("markdown-report", action)
        self.assertIn("report-command", action)
        self.assertIn("report-max-files", action)
        self.assertIn("report-since", action)
        self.assertIn("require-docs-fanout-budget", action)
        self.assertIn("docs-fanout-verdict", action)
        self.assertIn("report-markdown", action)
        self.assertIn("Unified Harness Report", docs)
        self.assertIn("report-markdown", docs)
        self.assertIn("report-since", docs)
        self.assertIn("require-docs-fanout-budget", docs)

    def test_action_manifest_and_docs_expose_release_check_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        action = (root / "action.yml").read_text(encoding="utf-8")
        docs = (root / "docs/action.md").read_text(encoding="utf-8")

        self.assertIn("command: release-check", docs)
        self.assertIn("require-sbom", action)
        self.assertIn("release-verdict", action)
        self.assertIn("Release Evidence Check", docs)
        self.assertIn("release-verdict", docs)
        self.assertIn("require-sbom", docs)

    def test_action_manifest_and_docs_expose_finalize_review_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        action = (root / "action.yml").read_text(encoding="utf-8")
        docs = (root / "docs/action.md").read_text(encoding="utf-8")

        self.assertIn("finalize-review", action)
        self.assertIn("accept-detected-high-risk", action)
        self.assertIn("reviewed-by", action)
        self.assertIn("evidence-ref", action)
        self.assertIn("command: finalize-review", docs)
        self.assertIn("accept-detected-high-risk", docs)
        self.assertIn("Review Finalization", docs)

    def test_action_audit_writes_outputs_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            output = root / "outputs.txt"
            summary = root / "summary.md"
            env = {
                "INPUT_COMMAND": "audit",
                "INPUT_TARGET": str(root),
                "INPUT_MIN_SCORE": "85",
                "INPUT_FAIL_ON_SCORE": "true",
                "INPUT_HTML_REPORT": "report.html",
                "INPUT_JSON_REPORT": "reports/report.json",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            self.assertEqual(code, 0)
            output_text = output.read_text(encoding="utf-8")
            outputs = _parse_github_output(output_text)
            self.assertTrue(outputs["overall-score"].isdigit())
            self.assertEqual(outputs["report-json"], "reports/report.json")
            self.assertEqual(outputs["report-html"], "report.html")
            self.assertTrue((root / "report.html").exists())
            self.assertTrue((root / "reports" / "report.json").exists())
            self.assertIn("HarnessForge Audit", summary.read_text(encoding="utf-8"))

    def test_action_report_writes_read_only_json_and_markdown_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                commands=(
                    _python_command(
                        "from pathlib import Path; Path('ran.txt').write_text('ran')"
                    ),
                ),
            )
            _write_verify_report(
                root,
                "docs/harness/evidence/verify-current.json",
            )
            output = root / "outputs.txt"
            summary = root / "summary.md"
            env = {
                "INPUT_COMMAND": "report",
                "INPUT_TARGET": str(root),
                "INPUT_REQUIRE_VERIFY_EVIDENCE": "true",
                "INPUT_REPORT_COMMAND": _python_command(
                    "from pathlib import Path; Path('marker.txt').write_text('ran')"
                ),
                "INPUT_REPORT_SINCE": "HEAD",
                "INPUT_JSON_REPORT": "reports/report.json",
                "INPUT_MARKDOWN_REPORT": "reports/report.md",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads(
                (root / "reports" / "report.json").read_text(encoding="utf-8")
            )
            markdown = (root / "reports" / "report.md").read_text(encoding="utf-8")
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(payload["schemaVersion"], "harnessforge.report.v1")
        self.assertEqual(payload["execution"]["commandsExecuted"], False)
        self.assertEqual(payload["readiness"]["verdict"], "ready")
        self.assertEqual(payload["docsFanout"]["diff"]["status"], "unavailable")
        self.assertEqual(payload["docsFanout"]["contract"]["verdict"], "warning")
        self.assertEqual(outputs["overall-score"], "100")
        self.assertEqual(outputs["report-json"], "reports/report.json")
        self.assertEqual(outputs["report-markdown"], "reports/report.md")
        self.assertEqual(outputs["report-html"], "")
        self.assertEqual(outputs["changed-files"], "0")
        self.assertEqual(outputs["readiness-verdict"], "ready")
        self.assertEqual(outputs["docs-fanout-verdict"], "warning")
        self.assertFalse((root / "ran.txt").exists())
        self.assertFalse((root / "marker.txt").exists())
        self.assertIn("# HarnessForge Report", markdown)
        self.assertIn("HarnessForge Report", summary_text)
        self.assertIn("Accepted high-risk surfaces", summary_text)
        self.assertIn("Review surfaces", summary_text)
        self.assertIn("Docs fan-out verdict", summary_text)
        self.assertIn("Instruction quality", summary_text)
        self.assertIn("First-agent lifecycle", summary_text)
        self.assertIn("Repo map", summary_text)
        self.assertIn("Feature state", summary_text)
        self.assertIn("Observability", summary_text)
        self.assertIn("Index adapters", summary_text)
        self.assertIn("SBOM files", summary_text)

    def test_action_release_check_writes_reports_and_outputs_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                commands=(
                    _python_command(
                        "from pathlib import Path; Path('ran.txt').write_text('ran')"
                    ),
                ),
            )
            _write_verify_report(root, "docs/harness/evidence/verify-current.json")
            output = root / "outputs.txt"
            summary = root / "summary.md"
            env = {
                "INPUT_COMMAND": "release-check",
                "INPUT_TARGET": str(root),
                "INPUT_REPORT_COMMAND": _python_command(
                    "from pathlib import Path; Path('marker.txt').write_text('ran')"
                ),
                "INPUT_JSON_REPORT": "reports/release-check.json",
                "INPUT_MARKDOWN_REPORT": "reports/release-check.md",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads(
                (root / "reports" / "release-check.json").read_text(encoding="utf-8")
            )
            markdown = (root / "reports" / "release-check.md").read_text(
                encoding="utf-8"
            )
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(code, 1)
        self.assertEqual(payload["schemaVersion"], "harnessforge.releaseCheck.v1")
        self.assertEqual(payload["verdict"], "warning")
        self.assertEqual(payload["execution"]["commandsExecuted"], False)
        self.assertFalse((root / "ran.txt").exists())
        self.assertFalse((root / "marker.txt").exists())
        self.assertEqual(outputs["release-verdict"], "warning")
        self.assertEqual(outputs["report-json"], "reports/release-check.json")
        self.assertEqual(outputs["report-markdown"], "reports/release-check.md")
        self.assertEqual(outputs["readiness-verdict"], "ready")
        self.assertEqual(outputs["docs-fanout-verdict"], "not_required")
        self.assertIn("# HarnessForge Release Check", markdown)
        self.assertIn("HarnessForge Release Check", summary_text)
        self.assertIn("Accepted high-risk surfaces", summary_text)
        self.assertIn("Maturity level", summary_text)
        self.assertIn("Feature state", summary_text)
        self.assertIn("Observability", summary_text)
        self.assertIn("first-agent-lifecycle", summary_text)

    def test_action_sync_writes_readiness_report_and_outputs(self) -> None:
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
            )
            output = root / "outputs.txt"
            summary = root / "summary.md"
            env = {
                "INPUT_COMMAND": "sync",
                "INPUT_TARGET": str(root),
                "INPUT_REQUIRE_VERIFY_EVIDENCE": "true",
                "INPUT_JSON_REPORT": "reports/sync.json",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads(
                (root / "reports" / "sync.json").read_text(encoding="utf-8")
            )
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(payload["mode"], "check")
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["exitCode"], 0)
        self.assertTrue(payload["readiness"]["verifyEvidenceRequired"])
        self.assertEqual(outputs["report-json"], "reports/sync.json")
        self.assertEqual(outputs["readiness-verdict"], "ready")
        self.assertEqual(outputs["sync-exit-code"], "0")
        self.assertEqual(outputs["changed-files"], "0")
        self.assertEqual(outputs["verify-verdict"], "")
        self.assertFalse((root / "AGENTS.md").exists())
        self.assertIn("HarnessForge Sync", summary_text)
        self.assertIn("Accepted high-risk surfaces", summary_text)
        self.assertIn("Review surface statuses", summary_text)
        self.assertIn("Instruction quality", summary_text)
        self.assertIn("First-agent lifecycle", summary_text)

    def test_action_finalize_review_applies_explicit_review_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_finalize_fixture(root)
            create_harness(
                root,
                commands=("python -m unittest discover -s tests",),
            )
            output = root / "outputs.txt"
            summary = root / "summary.md"
            env = {
                "INPUT_COMMAND": "finalize-review",
                "INPUT_TARGET": str(root),
                "INPUT_APPLY": "true",
                "INPUT_ACCEPT_DETECTED_HIGH_RISK": "true",
                "INPUT_REVIEWED_BY": "Maintainer",
                "INPUT_JSON_REPORT": "reports/review-finalization.json",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads(
                (root / "reports" / "review-finalization.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (
                    root / "docs/harness/evidence/first-agent-review.json"
                ).read_text(encoding="utf-8")
            )
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(payload["mode"], "apply")
        self.assertEqual(payload["changedFiles"], 3)
        self.assertEqual(
            {item["path"] for item in payload["highRiskSurfaces"]},
            {"AGENTS.md", ".github/workflows/ci.yml"},
        )
        self.assertEqual(evidence["status"], "retired")
        self.assertEqual(
            len(evidence["highRiskSurfaceReview"]["surfaces"]),
            2,
        )
        self.assertEqual(outputs["changed-files"], "3")
        self.assertEqual(
            outputs["report-json"],
            "reports/review-finalization.json",
        )
        self.assertIn("HarnessForge Review Finalization", summary_text)
        self.assertIn("High-risk surfaces", summary_text)

    def test_action_sync_verify_evidence_gate_blocks_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            output = root / "outputs.txt"
            env = {
                "INPUT_COMMAND": "sync",
                "INPUT_TARGET": str(root),
                "INPUT_REQUIRE_VERIFY_EVIDENCE": "true",
                "INPUT_JSON_REPORT": "sync.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads((root / "sync.json").read_text(encoding="utf-8"))
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 2)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertEqual(payload["exitCode"], 2)
        self.assertTrue(payload["readiness"]["verifyEvidenceRequired"])
        self.assertTrue(
            any(
                "No stored verify evidence report" in item
                for item in payload["readiness"]["blockedReasons"]
            )
        )
        self.assertEqual(outputs["readiness-verdict"], "blocked")
        self.assertEqual(outputs["sync-exit-code"], "2")

    def test_action_sync_accepts_explicit_command_without_running_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            output = root / "outputs.txt"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            env = {
                "INPUT_COMMAND": "sync",
                "INPUT_TARGET": str(root),
                "INPUT_SYNC_COMMAND": command,
                "INPUT_JSON_REPORT": "sync.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads((root / "sync.json").read_text(encoding="utf-8"))
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(payload["verdict"], "ready")
        self.assertIn(command, payload["readiness"]["runnableChecks"])
        self.assertEqual(outputs["readiness-verdict"], "ready")

    def test_action_verify_plan_writes_report_without_running(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            output = root / "outputs.txt"
            summary = root / "summary.md"
            command = _python_command(
                "from pathlib import Path; Path('ran.txt').write_text('ran')"
            )
            env = {
                "INPUT_COMMAND": "verify",
                "INPUT_TARGET": str(root),
                "INPUT_VERIFY_COMMAND": command,
                "INPUT_JSON_REPORT": "reports/verify.json",
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads(
                (root / "reports" / "verify.json").read_text(encoding="utf-8")
            )
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            summary_text = summary.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertEqual(payload["mode"], "plan")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertEqual(outputs["report-json"], "reports/verify.json")
        self.assertEqual(outputs["verify-verdict"], "planned")
        self.assertEqual(outputs["changed-files"], "0")
        self.assertIn("HarnessForge Verify", summary_text)

    def test_action_verify_run_executes_when_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "ran.txt"
            output = root / "outputs.txt"
            command = _python_command(
                "from pathlib import Path; "
                "Path('ran.txt').write_text('ran', encoding='utf-8'); "
                "print('action verify ok')"
            )
            env = {
                "INPUT_COMMAND": "verify",
                "INPUT_TARGET": str(root),
                "INPUT_VERIFY_RUN": "true",
                "INPUT_VERIFY_COMMAND": command,
                "INPUT_JSON_REPORT": "verify.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads((root / "verify.json").read_text(encoding="utf-8"))
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            marker_exists = marker.exists()

        self.assertEqual(code, 0)
        self.assertTrue(marker_exists)
        self.assertEqual(payload["mode"], "run")
        self.assertEqual(payload["verdict"], "passed")
        self.assertEqual(payload["checks"][0]["status"], "passed")
        self.assertEqual(outputs["verify-verdict"], "passed")

    def test_action_verify_run_failure_returns_one_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "outputs.txt"
            command = _python_command("import sys; print('bad check'); sys.exit(4)")
            env = {
                "INPUT_COMMAND": "verify",
                "INPUT_TARGET": str(root),
                "INPUT_VERIFY_RUN": "true",
                "INPUT_VERIFY_COMMAND": command,
                "INPUT_JSON_REPORT": "verify.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads((root / "verify.json").read_text(encoding="utf-8"))
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "failed")
        self.assertEqual(payload["checks"][0]["exitCode"], 4)
        self.assertEqual(outputs["verify-verdict"], "failed")

    def test_action_verify_run_blocks_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            output = root / "outputs.txt"
            env = {
                "INPUT_COMMAND": "verify",
                "INPUT_TARGET": str(root),
                "INPUT_VERIFY_RUN": "true",
                "INPUT_JSON_REPORT": "verify.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            payload = json.loads((root / "verify.json").read_text(encoding="utf-8"))
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 2)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertEqual(outputs["verify-verdict"], "blocked")

    def test_action_init_can_scaffold_optional_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {
                "INPUT_COMMAND": "init",
                "INPUT_TARGET": str(root),
                "INPUT_WITH_CI_WORKFLOW": "true",
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            ci_exists = (root / ".github/workflows/harnessforge.yml").exists()
            self_heal_exists = (
                root / ".github/workflows/harness-self-heal.yml"
            ).exists()

        self.assertEqual(code, 0)
        self.assertTrue(ci_exists)
        self.assertFalse(self_heal_exists)

    def test_action_init_can_enhance_existing_instruction_files(self) -> None:
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
            output = root / "github-output.txt"
            env = {
                "INPUT_COMMAND": "init",
                "INPUT_TARGET": str(root),
                "INPUT_ENHANCE_EXISTING": "true",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            outputs = _parse_github_output(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertIn("Keep local instructions.", agents)
        self.assertIn("HarnessForge Quality Addendum", agents)
        self.assertGreaterEqual(int(outputs["changed-files"]), 1)

    def test_action_init_writes_only_inside_declared_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target = workspace / "target-repo"
            env = {
                "INPUT_COMMAND": "init",
                "INPUT_TARGET": str(target),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            self.assertEqual(code, 0)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / "docs/harness/manifest.json").exists())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertFalse((workspace / "docs").exists())

    def test_action_report_paths_must_stay_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            create_harness(root)
            outside = Path(tmp) / "outside.html"
            for report_path in (
                "../outside.html",
                "..\\outside.html",
                str(outside),
                "C:\\temp\\outside.html",
                "C:outside.html",
                "\\outside.html",
                "\\\\server\\share\\outside.html",
            ):
                with self.subTest(report_path=report_path):
                    env = {
                        "INPUT_COMMAND": "audit",
                        "INPUT_TARGET": str(root),
                        "INPUT_HTML_REPORT": report_path,
                    }

                    with self.assertRaises(ValueError):
                        run_from_env(env)

            self.assertFalse(outside.exists())

    def test_action_min_score_must_be_score_range(self) -> None:
        for min_score in ("-1", "101"):
            with self.subTest(min_score=min_score):
                with self.assertRaisesRegex(
                    ValueError,
                    "min-score must be between 0 and 100",
                ):
                    run_from_env({"INPUT_MIN_SCORE": min_score})

    def test_action_report_paths_normalize_windows_relative_separators(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            output = root / "outputs.txt"
            env = {
                "INPUT_COMMAND": "audit",
                "INPUT_TARGET": str(root),
                "INPUT_HTML_REPORT": "reports\\audit.html",
                "INPUT_JSON_REPORT": "reports\\nested\\audit.json",
                "GITHUB_OUTPUT": str(output),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            outputs = _parse_github_output(output.read_text(encoding="utf-8"))
            self.assertEqual(code, 0)
            self.assertEqual(outputs["report-html"], "reports/audit.html")
            self.assertEqual(outputs["report-json"], "reports/nested/audit.json")
            self.assertTrue((root / "reports" / "audit.html").exists())
            self.assertTrue((root / "reports" / "nested" / "audit.json").exists())

    def test_action_outputs_do_not_allow_newline_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "outputs.txt"

            _output(
                {"GITHUB_OUTPUT": str(output)},
                {"report-json": "report.json\ninjected=true"},
            )

            output_text = output.read_text(encoding="utf-8")
            outputs = _parse_github_output(output_text)
            self.assertEqual(set(outputs), {"report-json"})
            self.assertEqual(
                outputs["report-json"],
                "report.json\ninjected=true",
            )


if __name__ == "__main__":
    unittest.main()
