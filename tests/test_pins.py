from __future__ import annotations

import tempfile
import unittest
import json
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

    def test_rejects_unexpected_build_hook_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / "setup.py").write_text(
                "from setuptools import setup\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertTrue(any("build hook file" in failure for failure in failures))

    def test_rejects_mutable_container_and_requirement_pins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / "Dockerfile").write_text(
                "FROM python:3.13\n",
                encoding="utf-8",
            )
            (root / "requirements-dev.txt").write_text(
                "pytest>=8\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertTrue(any("container base image" in failure for failure in failures))
        self.assertTrue(any("Python requirement" in failure for failure in failures))

    def test_rejects_mutable_package_json_and_lockfile_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {"left-pad": "^1.3.0"},
                        "devDependencies": {"workspace-lib": "workspace:*"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text(
                json.dumps(
                    {
                        "packages": {
                            "node_modules/left-pad": {
                                "version": "1.3.0",
                                "resolved": "https://example.invalid/left-pad.tgz",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertTrue(any("exact npm version" in failure for failure in failures))
        self.assertTrue(any("npm registry tarball" in failure for failure in failures))
        self.assertTrue(any("sha512 integrity" in failure for failure in failures))

    def test_multiline_workflow_shell_blocks_fail_fast(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflows = sorted((root / ".github/workflows").glob("*.yml"))

        for workflow in workflows:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding="utf-8")
                for line_number, first_command in _multiline_run_first_commands(text):
                    self.assertEqual(
                        first_command,
                        "set -euo pipefail",
                        f"{workflow}:{line_number} multiline run block must fail fast",
                    )

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

    def test_ci_cancels_superseded_runs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")

        self.assertIn("concurrency:", workflow)
        self.assertIn("github.event.pull_request.number || github.ref", workflow)
        self.assertIn("cancel-in-progress: true", workflow)

    def test_ci_keeps_platform_checks_manual(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch'", workflow)
        self.assertIn("macos-15", workflow)
        self.assertIn("windows-2025-vs2026", workflow)

    def test_self_heal_stages_generated_root_and_template_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/harness-self-heal.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('cron: "0 12 * * 1"', workflow)
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


def _multiline_run_first_commands(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    commands: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if not (stripped.startswith("run: |") or stripped.startswith("run: >")):
            continue
        indent = len(line) - len(stripped)
        block: list[str] = []
        for block_line in lines[index + 1 :]:
            block_indent = len(block_line) - len(block_line.lstrip())
            if block_line.strip() and block_indent <= indent:
                break
            block.append(block_line.strip())
        first_command = next(
            (
                block_line
                for block_line in block
                if block_line and not block_line.startswith("#")
            ),
            "",
        )
        commands.append((index + 1, first_command))
    return commands


if __name__ == "__main__":
    unittest.main()
