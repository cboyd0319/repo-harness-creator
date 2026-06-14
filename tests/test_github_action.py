from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from harnessforge.generate import create_harness
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
            outputs = _parse_github_output(output_text)
            self.assertTrue(outputs["overall-score"].isdigit())
            self.assertEqual(outputs["report-json"], "reports/report.json")
            self.assertEqual(outputs["report-html"], "report.html")
            self.assertTrue((root / "report.html").exists())
            self.assertTrue((root / "reports" / "report.json").exists())
            self.assertIn("HarnessForge Audit", summary.read_text(encoding="utf-8"))

    def test_action_init_can_scaffold_optional_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {
                "INPUT_COMMAND": "init",
                "INPUT_TARGET": str(root),
                "INPUT_WITH_CI_WORKFLOW": "true",
                "INPUT_WITH_SELF_HEAL_WORKFLOW": "true",
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            ci_exists = (root / ".github/workflows/harnessforge.yml").exists()
            self_heal_exists = (
                root / ".github/workflows/harness-self-heal.yml"
            ).exists()

        self.assertEqual(code, 0)
        self.assertTrue(ci_exists)
        self.assertTrue(self_heal_exists)

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
