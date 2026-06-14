from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from harnessforge.cli import main


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

    def test_init_can_scaffold_optional_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
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
