from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATH_RE = "|".join(
    (r"/" + "Users/", "Documents" + "/" + "GitHub", "C:" + r"\\Users\\")
)


class LargePublicRepoAnalysisTests(unittest.TestCase):
    def test_default_corpus_lists_without_network_or_local_paths(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/analyze_large_public_repos.py", "--list", "--json"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": os.pathsep.join((str(ROOT / "src"), str(ROOT)))},
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            payload["schemaVersion"],
            "harnessforge.largePublicRepoCorpusList.v1",
        )
        self.assertGreaterEqual(payload["summary"]["repos"], 12)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertNotRegex(result.stdout, LOCAL_PATH_RE)

    def test_analyzes_existing_checkout_and_reports_nested_agents_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            corpus = tmp_path / "corpus.json"
            workdir = tmp_path / "work"
            checkout = workdir / "checkouts" / "sample-monorepo"
            checkout.mkdir(parents=True)
            self._write_sample_repo(checkout)
            head = self._git(checkout, "rev-parse", "HEAD").strip()
            corpus.write_text(
                json.dumps(
                    {
                        "schemaVersion": "harnessforge.largePublicRepoCorpus.v1",
                        "lastReviewed": "2026-06-16",
                        "repos": [
                            {
                                "id": "sample-monorepo",
                                "repository": "example/sample-monorepo",
                                "url": "https://github.com/example/sample-monorepo",
                                "pinnedRef": head,
                                "categories": ["typescript-app", "monorepo"],
                                "analysisFocus": [
                                    "nested-agents-monorepo-instruction-scopes"
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            json_report = tmp_path / "report.json"
            markdown_report = tmp_path / "report.md"

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/analyze_large_public_repos.py",
                    "--corpus",
                    str(corpus),
                    "--workdir",
                    str(workdir),
                    "--repo",
                    "sample-monorepo",
                    "--max-files",
                    "4",
                    "--component-limit",
                    "3",
                    "--json-report",
                    str(json_report),
                    "--markdown-report",
                    str(markdown_report),
                    "--json",
                ],
                cwd=ROOT,
                env={
                    **os.environ,
                    "PYTHONPATH": os.pathsep.join((str(ROOT / "src"), str(ROOT))),
                },
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(json_report.read_text(encoding="utf-8"))
            repo = payload["repositories"][0]

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertEqual(payload["schemaVersion"], "harnessforge.largePublicRepoAnalysis.v1")
            self.assertFalse(payload["execution"]["networkAccess"])
            self.assertEqual(repo["status"], "analyzed")
            self.assertTrue(repo["headMatchesPinnedRef"])
            self.assertEqual(repo["dryRunGeneration"]["requestedFileScanLimit"], 4)
            self.assertEqual(repo["dryRunGeneration"]["fileScanLimit"], 4)
            self.assertEqual(repo["dryRunGeneration"]["requestedComponentLimit"], 3)
            self.assertEqual(repo["dryRunGeneration"]["componentLimit"], 3)
            self.assertTrue(repo["dryRunGeneration"]["usesRequestedFileScanLimit"])
            self.assertFalse(repo["dryRunGeneration"]["usesDefaultFileScanLimit"])
            self.assertIn(
                "file_scan_truncated",
                {gap["code"] for gap in repo["qualityGaps"]},
            )
            self.assertEqual(repo["fileCoverage"]["status"], "budget_limited")
            self.assertIn("scanEligibleFileCount", repo["fileCoverage"])
            self.assertIn("skippedFileCount", repo["fileCoverage"])
            self.assertTrue(repo["fileCoverage"]["categorySummary"])
            self.assertEqual(
                repo["componentOverflow"]["schemaVersion"],
                "harnessforge.componentOverflow.v1",
            )
            self.assertEqual(
                repo["verificationCommands"]["schemaVersion"],
                "harnessforge.verificationCommands.v1",
            )
            self.assertIn(
                "package-script",
                repo["verificationCommands"]["summary"]["sourceTypes"],
            )
            self.assertEqual(
                repo["verificationCommands"]["commands"][0]["sourcePath"],
                "package.json",
            )
            self.assertEqual(
                repo["repoMap"]["verification"]["schemaVersion"],
                "harnessforge.verificationCommands.v1",
            )
            self.assertIn(
                "file_coverage_budget_limited",
                {gap["code"] for gap in repo["qualityGaps"]},
            )
            self.assertIn(
                "file_discovery_priority",
                {item["code"] for item in payload["crossRepoFindings"]},
            )
            self.assertNotIn(
                "generator_default_scan_limit",
                {gap["code"] for gap in repo["qualityGaps"]},
            )
            self.assertEqual(repo["nestedInstructionPlan"]["status"], "review_required")
            self.assertFalse(repo["nestedInstructionPlan"]["writeByDefault"])
            self.assertGreater(repo["nestedInstructionPlan"]["candidateCount"], 0)
            self.assertIn(
                "nested_agents_review_needed",
                {gap["code"] for gap in repo["qualityGaps"]},
            )
            self.assertIn("Nested `AGENTS.md` entries", markdown_report.read_text(encoding="utf-8"))
            self.assertNotRegex(json_report.read_text(encoding="utf-8"), str(tmp_path))

    def _write_sample_repo(self, root: Path) -> None:
        (root / "package.json").write_text(
            json.dumps(
                {
                    "name": "sample",
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
                json.dumps({"name": f"@sample/{package}"}),
                encoding="utf-8",
            )
            (package_root / "index.ts").write_text("export const ok = true\n", encoding="utf-8")
        (root / "README.md").write_text("# Sample\n", encoding="utf-8")
        self._git(root, "init")
        self._git(root, "add", ".")
        self._git(
            root,
            "-c",
            "user.name=HarnessForge Tests",
            "-c",
            "user.email=tests@example.invalid",
            "commit",
            "-m",
            "initial",
        )

    def _git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(result.stderr or result.stdout)
        return result.stdout


if __name__ == "__main__":
    unittest.main()
