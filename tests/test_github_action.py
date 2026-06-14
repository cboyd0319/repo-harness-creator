from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from repo_harness_creator.generate import create_harness
from repo_harness_creator.github_action import _output, run_from_env


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
            self.assertIn("overall-score=", output_text)
            self.assertIn("report-json=reports/report.json", output_text)
            self.assertIn("report-html=report.html", output_text)
            self.assertTrue((root / "report.html").exists())
            self.assertTrue((root / "reports" / "report.json").exists())
            self.assertIn("Repo Harness Audit", summary.read_text(encoding="utf-8"))

    def test_action_report_paths_must_stay_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            create_harness(root)
            outside = Path(tmp) / "outside.html"
            for report_path in ("../outside.html", str(outside)):
                with self.subTest(report_path=report_path):
                    env = {
                        "INPUT_COMMAND": "audit",
                        "INPUT_TARGET": str(root),
                        "INPUT_HTML_REPORT": report_path,
                    }

                    with self.assertRaises(ValueError):
                        run_from_env(env)

            self.assertFalse(outside.exists())

    def test_action_outputs_do_not_allow_newline_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "outputs.txt"

            _output({"GITHUB_OUTPUT": str(output)}, {"report-json": "report.json\ninjected=true"})

            self.assertNotIn("\ninjected=true\n", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
