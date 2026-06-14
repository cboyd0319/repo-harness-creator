from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harnessforge.detect import detect_project


def _supports_directory_symlink() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target"
        link = root / "link"
        target.mkdir()
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            return False
        return link.is_symlink()


def _supports_file_symlink() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target.json"
        link = root / "link.json"
        target.write_text("{}", encoding="utf-8")
        try:
            link.symlink_to(target)
        except OSError:
            return False
        return link.is_symlink()


class DetectProjectTests(unittest.TestCase):
    def test_detects_python_project_and_stdlib_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests/test_demo.py").write_text(
                "import unittest\n\nclass Demo(unittest.TestCase):\n    pass\n",
                encoding="utf-8",
            )
            profile = detect_project(root)

        self.assertEqual(profile.stack, "python")
        self.assertIn("python", profile.languages)
        self.assertIn(". (pyproject.toml)", profile.components)
        self.assertIn("python -m compileall .", profile.verification_commands)
        self.assertIn("python -m unittest discover", profile.verification_commands)

    def test_detects_python_tooling_defaults_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n\n[tool.ruff]\n\n[tool.mypy]\n",
                encoding="utf-8",
            )
            profile = detect_project(root)

        self.assertIn("python -m ruff check .", profile.verification_commands)
        self.assertIn("python -m mypy .", profile.verification_commands)

    def test_detects_react_project_and_package_manager(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = {
                "dependencies": {"react": "^19.0.0"},
                "devDependencies": {"typescript": "^5.0.0"},
                "scripts": {"test": "vitest", "build": "vite build"},
            }
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            (root / "pnpm-lock.yaml").write_text("", encoding="utf-8")
            profile = detect_project(root)

        self.assertEqual(profile.stack, "typescript-react")
        self.assertIn("pnpm", profile.package_managers)
        self.assertIn("pnpm run test", profile.verification_commands)
        self.assertIn("pnpm run build", profile.verification_commands)

    def test_detects_nested_components_without_installing_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "apps" / "web").mkdir(parents=True)
            (root / "services" / "api").mkdir(parents=True)
            (root / "apps" / "web" / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest"}}),
                encoding="utf-8",
            )
            (root / "services" / "api" / "pyproject.toml").write_text(
                "[project]\nname='api'\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("apps/web (package.json)", profile.components)
        self.assertIn("services/api (pyproject.toml)", profile.components)

    def test_detects_javascript_workspace_and_orchestrator_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = {
                "packageManager": "pnpm@10.0.0",
                "workspaces": ["apps/*", "packages/*"],
                "scripts": {"test": "turbo run test"},
            }
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            (root / "pnpm-workspace.yaml").write_text(
                "packages:\n  - apps/*\n  - packages/*\n",
                encoding="utf-8",
            )
            (root / "turbo.json").write_text("{}", encoding="utf-8")
            (root / "apps" / "web").mkdir(parents=True)
            (root / "apps" / "web" / "project.json").write_text(
                "{}",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("pnpm", profile.package_managers)
        self.assertIn("package.json workspaces", profile.workspace_markers)
        self.assertIn("pnpm-workspace.yaml", profile.workspace_markers)
        self.assertIn("turbo.json", profile.workspace_markers)
        self.assertIn("apps/web (project.json)", profile.components)
        self.assertIn("pnpm run test", profile.verification_commands)

    def test_detects_vanilla_monorepo_routing_without_root_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "component-a").mkdir()
            (root / "component-a" / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest"}}),
                encoding="utf-8",
            )
            (root / "component-b").mkdir()
            (root / "component-b" / "pyproject.toml").write_text(
                "[project]\nname='component-b'\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "component-a.yml").write_text(
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - 'component-a/**'\n"
                "jobs:\n"
                "  test:\n"
                "    steps:\n"
                "      - run: ./scripts/test.sh\n"
                "        working-directory: component-a\n",
                encoding="utf-8",
            )
            (root / ".devcontainer" / "python").mkdir(parents=True)
            (root / ".devcontainer" / "python" / "devcontainer.json").write_text(
                "{}",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("component-a (package.json)", profile.components)
        self.assertIn("component-b (pyproject.toml)", profile.components)
        self.assertIn(
            "multiple nested component manifests",
            profile.workspace_markers,
        )
        self.assertIn(".github/workflows", profile.routing_markers)
        self.assertIn(".github/workflows path filters", profile.routing_markers)
        self.assertIn(".github/workflows working-directory", profile.routing_markers)
        self.assertIn(".devcontainer", profile.routing_markers)

    def test_detects_uv_and_cargo_workspaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\n"
                "name = 'workspace-root'\n"
                "[tool.uv.workspace]\n"
                "members = ['packages/*']\n"
                "[tool.pytest.ini_options]\n"
                "testpaths = ['tests']\n",
                encoding="utf-8",
            )
            (root / "uv.lock").write_text("", encoding="utf-8")
            (root / "Cargo.toml").write_text(
                "[workspace]\n"
                "members = ['crates/*']\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("pyproject.toml [tool.uv.workspace]", profile.workspace_markers)
        self.assertIn("Cargo.toml [workspace]", profile.workspace_markers)
        self.assertIn(
            "uv run --all-packages python -m pytest",
            profile.verification_commands,
        )

    def test_rust_workspace_uses_workspace_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[workspace]\n"
                "members = ['crates/*']\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "rust")
        self.assertIn("cargo test --workspace", profile.verification_commands)

    def test_detects_polyglot_build_orchestrators(self) -> None:
        cases = (
            ("MODULE.bazel", "bazel", "bazel test //...", "MODULE.bazel"),
            ("pants.toml", "pants", "pants test ::", "pants.toml"),
            (".buckconfig", "buck", "buck2 test //...", ".buckconfig"),
        )
        for marker, stack, command, component in cases:
            with self.subTest(marker=marker):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / marker).write_text("", encoding="utf-8")

                    profile = detect_project(root)

                self.assertEqual(profile.stack, stack)
                self.assertIn(command, profile.verification_commands)
                self.assertIn(component, profile.workspace_markers)

    def test_detects_dotnet_solution_and_project_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Demo.slnx").write_text("<Solution />\n", encoding="utf-8")
            (root / "src" / "Lib").mkdir(parents=True)
            (root / "src" / "Lib" / "Lib.fsproj").write_text(
                "<Project />\n",
                encoding="utf-8",
            )
            (root / "tests" / "App").mkdir(parents=True)
            (root / "tests" / "App" / "App.vbproj").write_text(
                "<Project />\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "dotnet")
        self.assertIn(". (Demo.slnx)", profile.components)
        self.assertIn("src/Lib (Lib.fsproj)", profile.components)
        self.assertIn("tests/App (App.vbproj)", profile.components)

    def test_detects_jvm_go_and_php_workspace_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.work").write_text("go 1.23\nuse ./service\n", encoding="utf-8")
            (root / "settings.gradle.kts").write_text(
                'include("app", "lib")\n',
                encoding="utf-8",
            )
            (root / "pom.xml").write_text(
                "<project>"
                "<modules><module>service</module></modules>"
                "</project>\n",
                encoding="utf-8",
            )
            (root / "composer.json").write_text(
                json.dumps({"repositories": [{"type": "path", "url": "packages/*"}]}),
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("go.work", profile.workspace_markers)
        self.assertIn("settings.gradle.kts", profile.workspace_markers)
        self.assertIn("pom.xml <modules>", profile.workspace_markers)
        self.assertIn("composer.json path repositories", profile.workspace_markers)

    def test_detects_terraform_and_harness_routing_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "infra" / "bootstrap" / "modules" / "state").mkdir(
                parents=True
            )
            (root / "infra" / "bootstrap" / "main.tf").write_text(
                "terraform {}\n",
                encoding="utf-8",
            )
            (root / "infra" / "bootstrap" / "versions.tf").write_text(
                "terraform {}\n",
                encoding="utf-8",
            )
            state_main = (
                root / "infra" / "bootstrap" / "modules" / "state" / "main.tf"
            )
            state_main.write_text(
                "resource \"null_resource\" \"example\" {}\n",
                encoding="utf-8",
            )
            (root / ".harness").mkdir()
            (root / ".harness" / "pipeline.yaml").write_text(
                "pipeline: {}\n",
                encoding="utf-8",
            )
            (root / ".github" / "actions" / "local").mkdir(parents=True)
            (root / ".github" / "actions" / "local" / "action.yml").write_text(
                "runs:\n  using: composite\n",
                encoding="utf-8",
            )
            (root / ".windsurf" / "rules").mkdir(parents=True)
            (root / ".windsurf" / "rules" / "repo.md").write_text(
                "rules\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "terraform")
        self.assertIn("infra/bootstrap (main.tf, versions.tf)", profile.components)
        self.assertIn("infra/bootstrap/modules/state (main.tf)", profile.components)
        self.assertIn(
            "multiple nested component manifests",
            profile.workspace_markers,
        )
        self.assertIn(".harness", profile.routing_markers)
        self.assertIn(".github/actions", profile.routing_markers)
        self.assertIn(".windsurf", profile.routing_markers)

    @unittest.skipUnless(_supports_directory_symlink(), "symlinks unavailable")
    def test_does_not_follow_symlinked_directories_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "pyproject.toml").write_text(
                "[project]\nname='outside'\n",
                encoding="utf-8",
            )
            (root / "external").symlink_to(outside, target_is_directory=True)

            profile = detect_project(root)

        self.assertNotIn("external (pyproject.toml)", profile.components)

    @unittest.skipUnless(_supports_file_symlink(), "symlinks unavailable")
    def test_does_not_read_root_manifest_symlinks_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "package.json").write_text(
                json.dumps({"dependencies": {"react": "^19.0.0"}}),
                encoding="utf-8",
            )
            (outside / "pyproject.toml").write_text(
                "[project]\nname='outside'\n",
                encoding="utf-8",
            )
            (root / "package.json").symlink_to(outside / "package.json")
            (root / "pyproject.toml").symlink_to(outside / "pyproject.toml")

            profile = detect_project(root)

        self.assertEqual(profile.stack, "generic")
        self.assertNotIn("javascript", profile.languages)
        self.assertNotIn("python", profile.languages)
        self.assertEqual(profile.runtime_files, ())
        self.assertEqual(profile.components, ())


if __name__ == "__main__":
    unittest.main()
