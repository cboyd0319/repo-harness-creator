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

    def test_python_commands_use_poetry_and_pipenv_runners(self) -> None:
        cases = (
            ("poetry.lock", "poetry run python -m compileall ."),
            ("Pipfile.lock", "pipenv run python -m compileall ."),
        )
        for marker, command in cases:
            with self.subTest(marker=marker):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / "pyproject.toml").write_text(
                        "[project]\nname='demo'\n",
                        encoding="utf-8",
                    )
                    (root / marker).write_text("", encoding="utf-8")

                    profile = detect_project(root)

                self.assertIn(command, profile.verification_commands)

    def test_nested_manifests_contribute_package_manager_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "frontend").mkdir()
            (root / "frontend" / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest"}}),
                encoding="utf-8",
            )
            (root / "frontend" / "pnpm-lock.yaml").write_text("", encoding="utf-8")
            (root / "service").mkdir()
            (root / "service" / "pom.xml").write_text("<project />\n", encoding="utf-8")

            profile = detect_project(root)

        self.assertIn("pnpm", profile.package_managers)
        self.assertIn("npm", profile.package_managers)
        self.assertIn("maven", profile.package_managers)

    def test_docs_site_uses_local_validation_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Gemfile").write_text("source 'https://rubygems.org'\n", encoding="utf-8")
            (root / "_config.yml").write_text("title: docs\n", encoding="utf-8")
            (root / "validate.sh").write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            for index in range(5):
                (root / f"page-{index}.md").write_text("# Page\n", encoding="utf-8")

            profile = detect_project(root)

        self.assertEqual(profile.stack, "docs")
        self.assertIn("./validate.sh", profile.verification_commands)
        self.assertNotIn("bundle exec rake test", profile.verification_commands)

    def test_makefile_commands_use_declared_targets_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text(
                ".PHONY: build test\n\nbuild:\n\t@true\n\ntest:\n\t@true\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn("make test", profile.verification_commands)
        self.assertNotIn("make check", profile.verification_commands)

    def test_detects_swift_package_and_make_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Package.swift").write_text(
                "// swift-tools-version: 6.2\n",
                encoding="utf-8",
            )
            (root / "Sources" / "App").mkdir(parents=True)
            (root / "Sources" / "App" / "main.swift").write_text(
                "print(\"hello\")\n",
                encoding="utf-8",
            )
            (root / "Tests" / "AppTests").mkdir(parents=True)
            (root / "Tests" / "AppTests" / "AppTests.swift").write_text(
                "import Testing\n",
                encoding="utf-8",
            )
            (root / "Makefile").write_text(
                ".PHONY: all test\n\nall:\n\t@true\n\ntest:\n\t@swift test\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "swift")
        self.assertIn("swift", profile.languages)
        self.assertIn("swiftpm", profile.package_managers)
        self.assertIn(". (Makefile, Package.swift)", profile.components)
        self.assertIn("make test", profile.verification_commands)
        self.assertNotIn("swift test", profile.verification_commands)
        self.assertNotIn("make check", profile.verification_commands)

    def test_shell_project_uses_repo_validation_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fix_app.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools" / "validate_harness.sh").write_text(
                "#!/usr/bin/env bash\n",
                encoding="utf-8",
            )
            (root / "tools" / "test_dependency_parsing.sh").write_text(
                "#!/usr/bin/env bash\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "shell")
        self.assertIn("shell", profile.languages)
        self.assertIn("./tools/validate_harness.sh", profile.verification_commands)
        self.assertIn(
            "./tools/test_dependency_parsing.sh",
            profile.verification_commands,
        )
        self.assertNotIn(
            "No project verification check detected",
            "\n".join(profile.verification_commands),
        )

    def test_root_jvm_manifest_takes_priority_over_python_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pom.xml").write_text("<project />\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "helper.py").write_text(
                "print('helper')\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "java")
        self.assertIn("mvn test", profile.verification_commands)
        self.assertNotIn("python -m compileall .", profile.verification_commands)

    def test_root_gemfile_takes_priority_over_python_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Gemfile").write_text(
                "source 'https://rubygems.org'\n",
                encoding="utf-8",
            )
            (root / "scripts").mkdir()
            (root / "scripts" / "helper.py").write_text(
                "print('helper')\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "ruby")
        self.assertIn("bundle exec rake test", profile.verification_commands)
        self.assertNotIn("python -m compileall .", profile.verification_commands)

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
        self.assertEqual(profile.stack, "monorepo")
        self.assertIn("npm --prefix apps/web test", profile.verification_commands)
        self.assertIn("python -m compileall services/api", profile.verification_commands)
        self.assertNotIn(
            "No project verification check detected",
            "\n".join(profile.verification_commands),
        )

    def test_nested_uv_python_project_uses_repo_pytest_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "uv.lock").write_text("", encoding="utf-8")
            (root / "models").mkdir()
            (root / "models" / "pyproject.toml").write_text(
                "[project]\nname='models'\n\n[dependency-groups]\n"
                "dev = ['pytest>=8']\n",
                encoding="utf-8",
            )
            (root / "scripts" / "tests").mkdir(parents=True)
            (root / "scripts" / "tests" / "test_model.py").write_text(
                "def test_model():\n    assert True\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertIn(
            "uv run --project models python -m compileall models",
            profile.verification_commands,
        )
        self.assertIn(
            "uv run --project models python -m pytest scripts/tests",
            profile.verification_commands,
        )
        self.assertNotIn(
            "python -m unittest discover -s scripts/tests",
            profile.verification_commands,
        )

    def test_root_scripts_tests_are_not_assigned_to_many_python_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "packages" / "one").mkdir(parents=True)
            (root / "packages" / "one" / "pyproject.toml").write_text(
                "[project]\nname='one'\n\n[dependency-groups]\n"
                "dev = ['pytest>=8']\n",
                encoding="utf-8",
            )
            (root / "packages" / "two").mkdir(parents=True)
            (root / "packages" / "two" / "pyproject.toml").write_text(
                "[project]\nname='two'\n\n[dependency-groups]\n"
                "dev = ['pytest>=8']\n",
                encoding="utf-8",
            )
            (root / "scripts" / "tests").mkdir(parents=True)
            (root / "scripts" / "tests" / "test_cli.py").write_text(
                "def test_cli():\n    assert True\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertNotIn(
            "python -m pytest scripts/tests",
            profile.verification_commands,
        )

    def test_docs_heavy_multi_component_repo_detects_monorepo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mkdocs.yml").write_text("site_name: demo\n", encoding="utf-8")
            for index in range(6):
                (root / "docs").mkdir(exist_ok=True)
                (root / "docs" / f"page-{index}.md").write_text(
                    "# Page\n",
                    encoding="utf-8",
                )
            (root / "packages" / "cli").mkdir(parents=True)
            (root / "packages" / "cli" / "pyproject.toml").write_text(
                "[project]\nname='cli'\n",
                encoding="utf-8",
            )
            (root / "sdks" / "node").mkdir(parents=True)
            (root / "sdks" / "node" / "package.json").write_text(
                json.dumps({"scripts": {"test": "node --test"}}),
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "monorepo")
        self.assertIn("packages/cli (pyproject.toml)", profile.components)
        self.assertIn("sdks/node (package.json)", profile.components)

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

    def test_root_cargo_workspace_takes_priority_over_bazel_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[workspace]\nmembers = ['crates/app']\n",
                encoding="utf-8",
            )
            (root / "rust-toolchain.toml").write_text(
                "[toolchain]\ncomponents = ['rustfmt', 'clippy']\n",
                encoding="utf-8",
            )
            (root / "MODULE.bazel").write_text("", encoding="utf-8")
            (root / "BUILD.bazel").write_text("", encoding="utf-8")
            (root / ".claude").mkdir()
            (root / ".claude" / "AGENTS.md").write_text(
                "# Claude agent notes\n",
                encoding="utf-8",
            )
            (root / ".claude" / "CLAUDE.md").write_text(
                "# Claude notes\n",
                encoding="utf-8",
            )
            (root / "crates" / "app" / "tests" / "fixtures" / "python").mkdir(
                parents=True
            )
            (
                root
                / "crates"
                / "app"
                / "tests"
                / "fixtures"
                / "python"
                / "pyproject.toml"
            ).write_text("[project]\nname='fixture'\n", encoding="utf-8")

            profile = detect_project(root)

        self.assertEqual(profile.stack, "rust")
        self.assertIn("MODULE.bazel", profile.workspace_markers)
        self.assertIn(".claude/AGENTS.md", profile.routing_markers)
        self.assertIn(".claude/CLAUDE.md", profile.routing_markers)
        self.assertIn("cargo fmt --all -- --check", profile.verification_commands)
        self.assertIn(
            "cargo clippy --workspace --all-targets --all-features -- -D warnings",
            profile.verification_commands,
        )
        self.assertIn("cargo test --workspace", profile.verification_commands)
        self.assertIn("bazel test //...", profile.verification_commands)
        self.assertNotIn(
            "python -m compileall crates/app/tests/fixtures/python",
            profile.verification_commands,
        )

    def test_large_repo_keeps_root_markers_before_file_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(4500):
                path = root / "docs" / "versions" / str(index) / "page.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# Docs\n", encoding="utf-8")
            (root / "MODULE.bazel").write_text("module(name='demo')\n", encoding="utf-8")
            (root / "BUILD").write_text("", encoding="utf-8")
            (root / ".bazelrc").write_text("common --check_direct_dependencies=error\n", encoding="utf-8")
            (root / ".bazelversion").write_text("9.1.1\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[tool.pyink]\n", encoding="utf-8")
            (root / "requirements.txt").write_text("pyink==1.0.0\n", encoding="utf-8")
            (root / "src" / "main" / "java").mkdir(parents=True)
            (root / "src" / "main" / "java" / "Main.java").write_text(
                "class Main {}\n",
                encoding="utf-8",
            )
            (root / "src" / "main" / "cpp").mkdir(parents=True)
            (root / "src" / "main" / "cpp" / "main.cc").write_text(
                "int main() { return 0; }\n",
                encoding="utf-8",
            )
            (root / "tools" / "release").mkdir(parents=True)
            (root / "tools" / "release" / "BUILD").write_text("", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "release.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (root / "third_party" / "vendor" / "buildscripts").mkdir(parents=True)
            (root / "third_party" / "vendor" / "buildscripts" / "pom.xml").write_text(
                "<project />\n",
                encoding="utf-8",
            )

            profile = detect_project(root)

        self.assertEqual(profile.stack, "bazel")
        self.assertIn("java", profile.languages)
        self.assertIn("cpp", profile.languages)
        self.assertIn("MODULE.bazel", profile.runtime_files)
        self.assertIn(".bazelrc", profile.routing_markers)
        self.assertIn(".bazelversion", profile.routing_markers)
        self.assertIn("tools/release (BUILD)", profile.components)
        self.assertIn("bazel test //...", profile.verification_commands)
        self.assertNotIn("python -m compileall .", profile.verification_commands)
        self.assertNotIn(
            "mvn -f third_party/vendor/buildscripts/pom.xml test",
            profile.verification_commands,
        )

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
