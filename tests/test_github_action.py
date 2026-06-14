from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from repo_harness_creator.generate import create_harness
from repo_harness_creator.github_action import _output, run_from_env


class GitHubActionTests(unittest.TestCase):
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
                "INPUT_HTML_REPORT": str(root / "report.html"),
                "INPUT_JSON_REPORT": str(root / "report.json"),
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(summary),
            }

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_from_env(env)

            self.assertEqual(code, 0)
            self.assertIn("overall-score=", output.read_text(encoding="utf-8"))
            self.assertTrue((root / "report.html").exists())
            self.assertTrue((root / "report.json").exists())
            self.assertIn("Repo Harness Audit", summary.read_text(encoding="utf-8"))

    def test_action_outputs_do_not_allow_newline_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "outputs.txt"

            _output({"GITHUB_OUTPUT": str(output)}, {"report-json": "report.json\ninjected=true"})

            self.assertNotIn("\ninjected=true\n", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
