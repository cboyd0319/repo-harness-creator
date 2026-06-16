from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

from scripts.check_pins import check_root


class PinCheckTests(unittest.TestCase):
    def test_accepts_pins_toml_ledger_matches_repo_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/demo").mkdir(parents=True)
            (root / "pins.toml").write_text(
                "[python]\n"
                'minimum_supported = "3.13"\n'
                'setuptools = "82.0.1"\n'
                'requests = "2.32.5"\n'
                "\n[agent_cli]\n"
                'codex = "0.20.0"\n'
                "\n[agent_cli_integrity]\n"
                'codex = "sha512-reviewed"\n'
                "\n[container_images]\n"
                'python_313 = { image = "python", tag = "3.13", '
                'digest = "sha256:abc123" }\n'
                "\n[profile_images]\n"
                'default = "registry.example.com/team/agent:1.2.3"\n',
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n'
                "[project]\n"
                'name = "demo"\n'
                'version = "0.1.0"\n'
                'requires-python = ">=3.13"\n'
                'dependencies = ["requests[socks]==2.32.5"]\n',
                encoding="utf-8",
            )
            (root / "requirements.txt").write_text(
                "requests[socks]==2.32.5\n",
                encoding="utf-8",
            )
            (root / "Containerfile").write_text(
                "FROM python:3.13@sha256:abc123\n",
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"@openai/codex": "0.20.0"}}),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text(
                json.dumps(
                    {
                        "packages": {
                            "": {"dependencies": {"@openai/codex": "0.20.0"}},
                            "node_modules/@openai/codex": {
                                "version": "0.20.0",
                                "resolved": (
                                    "https://registry.npmjs.org/@openai/codex/"
                                    "-/codex-0.20.0.tgz"
                                ),
                                "integrity": "sha512-reviewed",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "src/demo/profiles.py").write_text(
                'PROFILES = {"default": {"image": '
                '"registry.example.com/team/agent:1.2.3"}}\n',
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertEqual(failures, [])

    def test_rejects_pins_toml_ledger_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/demo").mkdir(parents=True)
            (root / "pins.toml").write_text(
                "[python]\n"
                'minimum_supported = "3.13"\n'
                'setuptools = "82.0.1"\n'
                'requests = "2.32.5"\n'
                "\n[agent_cli]\n"
                'codex = "0.20.0"\n'
                "\n[agent_cli_integrity]\n"
                'codex = "sha512-reviewed"\n'
                "\n[container_images]\n"
                'python_313 = { image = "python", tag = "3.13", '
                'digest = "sha256:abc123" }\n'
                "\n[profile_images]\n"
                'default = "registry.example.com/team/agent:1.2.3"\n',
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.2"]\n'
                'build-backend = "setuptools.build_meta"\n'
                "[project]\n"
                'name = "demo"\n'
                'version = "0.1.0"\n'
                'requires-python = ">=3.12"\n'
                'dependencies = ["requests==2.32.4"]\n',
                encoding="utf-8",
            )
            (root / "requirements.txt").write_text(
                "requests==2.32.4\n",
                encoding="utf-8",
            )
            (root / "Containerfile").write_text(
                "FROM python:3.13@sha256:def456\n",
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"@openai/codex": "0.21.0"}}),
                encoding="utf-8",
            )
            (root / "package-lock.json").write_text(
                json.dumps(
                    {
                        "packages": {
                            "": {"dependencies": {"@openai/codex": "0.21.0"}},
                            "node_modules/@openai/codex": {
                                "version": "0.21.0",
                                "resolved": (
                                    "https://registry.npmjs.org/@openai/codex/"
                                    "-/codex-0.21.0.tgz"
                                ),
                                "integrity": "sha512-drifted",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "src/demo/profiles.py").write_text(
                'PROFILES = {"default": {"image": '
                '"registry.example.com/team/agent:9.9.9"}}\n',
                encoding="utf-8",
            )

            failures = check_root(root)

        joined = "\n".join(failures)
        self.assertIn("pins.toml python.minimum_supported", joined)
        self.assertIn("setuptools==82.0.2", joined)
        self.assertIn("requests==2.32.4", joined)
        self.assertIn("container image", joined)
        self.assertIn("@openai/codex", joined)
        self.assertIn("package-lock integrity", joined)
        self.assertIn("profile image", joined)

    def test_checks_maven_and_gradle_dependency_pins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pins.toml").write_text(
                "[python]\n"
                'setuptools = "82.0.1"\n'
                "\n[maven_dependencies]\n"
                '"org.junit.jupiter:junit-jupiter" = "5.10.2"\n'
                '"org.slf4j:slf4j-api" = "2.0.13"\n'
                "\n[gradle_plugins]\n"
                '"com.diffplug.spotless" = "6.25.0"\n',
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / "pom.xml").write_text(
                """
                <project>
                  <dependencies>
                    <dependency>
                      <groupId>org.junit.jupiter</groupId>
                      <artifactId>junit-jupiter</artifactId>
                      <version>5.10.2</version>
                    </dependency>
                  </dependencies>
                </project>
                """,
                encoding="utf-8",
            )
            (root / "build.gradle").write_text(
                """
                plugins {
                    id 'com.diffplug.spotless' version '6.25.0'
                }
                dependencies {
                    implementation 'org.slf4j:slf4j-api:2.0.13'
                }
                """,
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertEqual(failures, [])

    def test_rejects_mutable_maven_and_gradle_dependency_pins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (root / "pom.xml").write_text(
                """
                <project>
                  <dependencies>
                    <dependency>
                      <groupId>org.junit.jupiter</groupId>
                      <artifactId>junit-jupiter</artifactId>
                      <version>5.10.2-SNAPSHOT</version>
                    </dependency>
                  </dependencies>
                </project>
                """,
                encoding="utf-8",
            )
            (root / "build.gradle.kts").write_text(
                """
                plugins {
                    id("com.diffplug.spotless") version "latest.release"
                }
                dependencies {
                    implementation("org.slf4j:slf4j-api:+")
                }
                """,
                encoding="utf-8",
            )

            failures = check_root(root)

        joined = "\n".join(failures)
        self.assertIn("Maven dependency", joined)
        self.assertIn("Gradle plugin", joined)
        self.assertIn("Gradle dependency", joined)

    def test_skips_intentionally_vulnerable_training_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vulnerable = root / "intentionally-vulnerable"
            vulnerable.mkdir()
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n',
                encoding="utf-8",
            )
            (vulnerable / "requirements.txt").write_text(
                "flask>=2\n",
                encoding="utf-8",
            )
            (vulnerable / "package.json").write_text(
                json.dumps({"dependencies": {"express": "^4.18.0"}}),
                encoding="utf-8",
            )
            (vulnerable / "pom.xml").write_text(
                """
                <project>
                  <dependencies>
                    <dependency>
                      <groupId>org.demo</groupId>
                      <artifactId>vulnerable-demo</artifactId>
                      <version>1.0.0-SNAPSHOT</version>
                    </dependency>
                  </dependencies>
                </project>
                """,
                encoding="utf-8",
            )
            (vulnerable / "Dockerfile").write_text(
                "FROM python:latest\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertEqual(failures, [])

    def test_rejects_non_version_python_requirement_without_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\n"
                'requires = ["setuptools==82.0.1"]\n'
                'build-backend = "setuptools.build_meta"\n'
                "[project]\n"
                'name = "demo"\n'
                'version = "0.1.0"\n'
                'dependencies = ["requests==latest"]\n',
                encoding="utf-8",
            )
            (root / "requirements.txt").write_text(
                "flask==latest\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        joined = "\n".join(failures)
        self.assertIn("project dependency", joined)
        self.assertIn("requirements.txt:1 Python requirement", joined)

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

    def test_allows_rust_build_rs_when_cargo_manifest_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[package]\nname = 'demo'\nversion = '0.1.0'\n",
                encoding="utf-8",
            )
            (root / "build.rs").write_text("fn main() {}\n", encoding="utf-8")

            failures = check_root(root)

        self.assertFalse(any("build hook file" in failure for failure in failures))

    def test_rejects_build_rs_without_cargo_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.rs").write_text("fn main() {}\n", encoding="utf-8")

            failures = check_root(root)

        self.assertTrue(any("build hook file" in failure for failure in failures))

    def test_accepts_multistage_container_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Dockerfile").write_text(
                "FROM python:3.13@sha256:abc123 AS builder\n"
                "RUN true\n"
                "FROM builder\n",
                encoding="utf-8",
            )

            failures = check_root(root)

        self.assertFalse(any("container base image" in failure for failure in failures))

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
        workflows_root = root / ".github/workflows"
        workflows = sorted(workflows_root.glob("*.yml"))
        workflows.extend(sorted(workflows_root.glob("*.yml.disabled")))

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
        lines = (root / ".github/workflows/ci.yml.disabled").read_text(
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
        workflow = (root / ".github/workflows/ci.yml.disabled").read_text(
            encoding="utf-8"
        )

        self.assertIn("concurrency:", workflow)
        self.assertIn("github.event.pull_request.number || github.ref", workflow)
        self.assertIn("cancel-in-progress: true", workflow)

    def test_ci_matches_local_verification_gate_shape(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml.disabled").read_text(
            encoding="utf-8"
        )

        self.assertIn("timeout-minutes: 20", workflow)
        self.assertIn("timeout-minutes: 30", workflow)
        self.assertIn("python -m compileall scripts src tests", workflow)
        self.assertIn("python scripts/refresh_research.py --root . --check", workflow)
        self.assertIn(
            "python -m harnessforge audit --target . --min-score 100", workflow
        )
        self.assertIn('min-score: "100"', workflow)

    def test_ci_keeps_platform_checks_manual(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml.disabled").read_text(
            encoding="utf-8"
        )

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch'", workflow)
        self.assertIn("macos-15", workflow)
        self.assertIn("windows-2025-vs2026", workflow)

    def test_self_heal_stages_generated_root_and_template_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (
            root / ".github/workflows/harness-self-heal.yml.disabled"
        ).read_text(encoding="utf-8")
        self.assertIn('cron: "0 12 * * 1"', workflow)
        git_add_line = next(
            line.strip()
            for line in workflow.splitlines()
            if line.strip().startswith("git add ")
        )

        for path in (
            "docs/harness",
            "src/harnessforge/templates",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            ".github/copilot-instructions.md",
            ".agents/skills/harness",
            "current-state.md",
            "feature_list.json",
            "pins.toml",
            "init.sh",
            "init.ps1",
        ):
            with self.subTest(path=path):
                self.assertIn(path, git_add_line)

    def test_self_heal_uses_confirmed_signed_reviewable_writes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (
            root / ".github/workflows/harness-self-heal.yml.disabled"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "python -m harnessforge update --target . --apply --yes --agent-file AGENTS.md",
            workflow,
        )
        self.assertIn("python scripts/refresh_research.py --root . --check", workflow)
        self.assertIn(
            "python -m harnessforge audit --target . --min-score 100", workflow
        )
        self.assertIn("git diff --name-only --exit-code", workflow)
        self.assertIn("git ls-files --others --exclude-standard", workflow)
        self.assertIn(
            'git commit -s -m "docs(harness): refresh self-healing research"',
            workflow,
        )

    def test_pin_check_ignores_local_harnessforge_checkouts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[build-system]\nrequires=['setuptools==82.0.1']\n",
                encoding="utf-8",
            )
            checkout = root / ".harnessforge/large-public-repos/checkouts/demo"
            checkout.mkdir(parents=True)
            (checkout / "requirements.txt").write_text("requests>=2\n", encoding="utf-8")
            (checkout / "Dockerfile").write_text("FROM python:3.13\n", encoding="utf-8")

            failures = check_root(root)

        self.assertEqual(failures, [])


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
