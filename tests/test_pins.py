from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_pins import check_root


class PinCheckTests(unittest.TestCase):
    def test_accepts_exact_build_requirement_and_sha_pinned_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n'
                "[project]\n"
                'name = "demo"\n'
                'version = "0.1.0"\n'
                "dependencies = []\n",
                encoding="utf-8",
            )
            (root / ".github/workflows/ci.yml").write_text(
                "steps:\n"
                "  - uses: actions/checkout@"
                "df4cb1c069e1874edd31b4311f1884172cec0e10 # v6\n"
                "  - uses: ./\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertEqual(failures, [])

    def test_rejects_range_requirement_and_tag_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools>=77"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / ".github/workflows/ci.yml").write_text(
                "steps:\n  - uses: actions/checkout@v6\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertGreaterEqual(len(failures), 2)
        self.assertTrue(any("exact pin" in failure for failure in failures))
        self.assertTrue(any("40-char SHA" in failure for failure in failures))

    def test_read_only_ci_checkout_does_not_persist_credentials(self) -> None:
        root = Path(__file__).resolve().parents[1]
        lines = (root / ".github/workflows/ci.yml").read_text(
            encoding="utf-8"
        ).splitlines()
        checkout_line = next(
            index
            for index, line in enumerate(lines)
            if "uses: actions/checkout@" in line
        )
        checkout_block = lines[checkout_line : checkout_line + 5]

        self.assertTrue(
            any("persist-credentials: false" in line for line in checkout_block)
        )

    def test_self_heal_stages_generated_root_and_template_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/harness-self-heal.yml").read_text(
            encoding="utf-8"
        )
        git_add_line = next(
            line.strip()
            for line in workflow.splitlines()
            if line.strip().startswith("git add ")
        )

        for path in (
            "docs/harness",
            "src/repo_harness_creator/templates",
            "AGENTS.md",
            "progress.md",
            "session-handoff.md",
            "feature_list.json",
            "init.sh",
            "init.ps1",
        ):
            with self.subTest(path=path):
                self.assertIn(path, git_add_line)


if __name__ == "__main__":
    unittest.main()
