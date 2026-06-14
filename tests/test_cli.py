from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from repo_harness_creator.cli import main


class CliTests(unittest.TestCase):
    def test_help_returns_zero(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--help"])

        self.assertEqual(code, 0)
        self.assertIn("repo-harness", stdout.getvalue())

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
