from __future__ import annotations

import contextlib
import io
import json
import re
import unittest

from harnessforge.cli import main


class PublicRepoCorpusTests(unittest.TestCase):
    def test_corpus_json_reports_pinned_offline_quality(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["corpus", "--json"])
        raw = stdout.getvalue()
        payload = json.loads(raw)

        required_categories = {
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
        }

        self.assertEqual(code, 0)
        self.assertEqual(payload["schemaVersion"], "harnessforge.publicRepoCorpus.v1")
        self.assertEqual(payload["mode"], "offline_fixture_quality")
        self.assertFalse(payload["execution"]["networkAccess"])
        self.assertFalse(payload["execution"]["targetWritesPerformed"])
        self.assertFalse(payload["execution"]["commandsExecuted"])
        self.assertTrue(payload["execution"]["temporaryFixtureWritesPerformed"])
        self.assertGreaterEqual(payload["summary"]["fixtures"], 12)
        self.assertEqual(payload["summary"]["failingFixtures"], 0)
        self.assertGreaterEqual(payload["summary"]["minimumScore"], 90)
        self.assertFalse(payload["coverage"]["missingCategories"])
        self.assertTrue(required_categories <= set(payload["coverage"]["categories"]))
        self.assertNotRegex(raw, r"/Users/|Documents/GitHub|Downloads|C:\\Users\\")

        for fixture in payload["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                self.assertRegex(fixture["pinnedRef"], r"^[0-9a-f]{40}$")
                self.assertGreaterEqual(fixture["quality"]["score"], 90)
                self.assertFalse(fixture["quality"]["failedChecks"])
                check_names = {check["name"] for check in fixture["quality"]["checks"]}
                self.assertIn("no_local_absolute_paths", check_names)
                self.assertIn("no_unrendered_template_tokens", check_names)
                self.assertIn("specific_project_context", check_names)

    def test_corpus_text_and_min_score_exit_code(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["corpus", "--min-score", "90"])
        output = stdout.getvalue()

        failing_stdout = io.StringIO()
        with contextlib.redirect_stdout(failing_stdout):
            failing_code = main(["corpus", "--min-score", "101"])

        self.assertEqual(code, 0)
        self.assertIn("Public repo quality corpus", output)
        self.assertIn("Mode: offline fixture quality", output)
        self.assertIn("Failing fixtures: 0", output)
        self.assertIn("pallets-flask", output)
        self.assertEqual(failing_code, 1)


if __name__ == "__main__":
    unittest.main()
