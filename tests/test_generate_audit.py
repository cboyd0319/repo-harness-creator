from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harnessforge.audit import audit_target
from harnessforge.generate import create_harness

AGENTS_SECTION_ORDER = [
    "## Project overview",
    "## Build and test commands",
    "## Code style guidelines",
    "## Testing instructions",
    "## Security considerations",
]


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
        target = root / "target.md"
        link = root / "link.md"
        target.write_text("target", encoding="utf-8")
        try:
            link.symlink_to(target)
        except OSError:
            return False
        return link.is_symlink()


class GenerateAuditTests(unittest.TestCase):
    def test_agents_files_follow_required_section_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        root_agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
        template_agents = (
            repo_root / "src/harnessforge/templates/agents.md.tmpl"
        ).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            generated_agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        for content in (root_agents, template_agents, generated_agents):
            headings = [
                line
                for line in content.splitlines()
                if line.startswith("## ")
            ]
            self.assertEqual(headings, AGENTS_SECTION_ORDER)
            self.assertIn("Startup", content)
            self.assertIn("Definition Of Done", content)
            self.assertIn("End of Session", content)
            self.assertIn("personal machines", content)

    def test_init_writes_cross_platform_harness_and_audits_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            profile, writes = create_harness(root)
            result = audit_target(root)
            init_sh = (root / "init.sh").read_text(encoding="utf-8")
            init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")
            claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            gemini = (root / "GEMINI.md").read_text(encoding="utf-8")
            copilot = (root / ".github/copilot-instructions.md").read_text(
                encoding="utf-8"
            )

        written = {write.path.name for write in writes if write.status == "written"}
        self.assertEqual(profile.stack, "python")
        self.assertIn("AGENTS.md", written)
        self.assertIn("CLAUDE.md", written)
        self.assertIn("GEMINI.md", written)
        self.assertIn("copilot-instructions.md", written)
        self.assertIn("check_pins.py", written)
        self.assertIn("@AGENTS.md", claude)
        self.assertIn("@AGENTS.md", gemini)
        self.assertIn("../AGENTS.md", copilot)
        self.assertIn("Security boundary map", copilot)
        self.assertIn('cd "$SCRIPT_DIR"', init_sh)
        self.assertIn("--no-env", init_sh)
        self.assertIn("OPENAI_API_KEY", init_sh)
        self.assertIn("PYTHON_BIN", init_sh)
        self.assertIn("scripts/check_pins.py --root .", init_sh)
        self.assertIn("harnessforge audit --target . --min-score 85", init_sh)
        self.assertIn("Set-Location -LiteralPath $ScriptRoot", init_ps1)
        self.assertIn("function Invoke-Native", init_ps1)
        self.assertIn("[switch] $NoEnv", init_ps1)
        self.assertIn("OPENAI_API_KEY", init_ps1)
        self.assertIn("Get-Command python3", init_ps1)
        self.assertIn("scripts/check_pins.py --root .", init_ps1)
        self.assertNotIn("Invoke-Expression", init_ps1)
        self.assertEqual(result.overall, 100)

    def test_platform_routers_follow_custom_agent_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, agent_file="PROJECT_AGENTS.md")
            claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            gemini = (root / "GEMINI.md").read_text(encoding="utf-8")
            copilot = (root / ".github/copilot-instructions.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("@PROJECT_AGENTS.md", claude)
        self.assertIn("@PROJECT_AGENTS.md", gemini)
        self.assertIn("../PROJECT_AGENTS.md", copilot)
        self.assertIn("PROJECT_AGENTS.md", manifest["requiredFiles"])
        self.assertIn("CLAUDE.md", manifest["requiredFiles"])
        self.assertIn("GEMINI.md", manifest["requiredFiles"])
        self.assertIn(
            ".github/copilot-instructions.md",
            manifest["requiredFiles"],
        )

    def test_optional_workflow_scaffolds_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)

            self.assertFalse((root / ".github/workflows/harnessforge.yml").exists())
            self.assertFalse((root / ".github/workflows/harness-self-heal.yml").exists())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resolved_root = root.resolve()
            _, writes = create_harness(
                root,
                with_ci_workflow=True,
                with_self_heal_workflow=True,
            )
            ci = (root / ".github/workflows/harnessforge.yml").read_text(
                encoding="utf-8"
            )
            self_heal = (root / ".github/workflows/harness-self-heal.yml").read_text(
                encoding="utf-8"
            )
            written = {
                str(write.path.resolve().relative_to(resolved_root))
                for write in writes
                if write.status == "written"
            }

        self.assertIn(".github/workflows/harnessforge.yml", written)
        self.assertIn(".github/workflows/harness-self-heal.yml", written)
        self.assertIn("workflow_dispatch", ci)
        self.assertIn("cancel-in-progress: true", ci)
        self.assertIn("persist-credentials: false", ci)
        self.assertIn("contents: write", self_heal)
        self.assertIn("gh pr create", self_heal)

    def test_generated_pin_checker_is_advisory_unless_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            workflow_dir = root / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "bad.yml").write_text(
                "steps:\n  - uses: actions/checkout@v6\n",
                encoding="utf-8",
            )
            (root / "Dockerfile").write_text(
                "FROM python:3.13\n",
                encoding="utf-8",
            )
            (root / "requirements.txt").write_text(
                "requests>=2\n",
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"left-pad": "^1.3.0"}}),
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
            script = root / "scripts" / "check_pins.py"

            advisory = subprocess.run(
                [sys.executable, str(script), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            strict = subprocess.run(
                [sys.executable, str(script), "--root", str(root), "--strict"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(advisory.returncode, 0)
        self.assertIn("Advisory mode", advisory.stdout)
        self.assertEqual(strict.returncode, 1)
        self.assertIn("40-char SHA", strict.stdout)
        self.assertIn("container base image", strict.stdout)
        self.assertIn("Python requirement", strict.stdout)
        self.assertIn("exact npm version", strict.stdout)
        self.assertIn("package-lock entry", strict.stdout)

    def test_existing_files_are_skipped_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("custom", encoding="utf-8")
            _, writes = create_harness(root)

        agents = [write for write in writes if write.path.name == "AGENTS.md"]
        self.assertEqual(agents[0].status, "skipped")
        self.assertEqual(agents[0].reason, "exists")

    def test_manifest_is_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(manifest["version"], 1)
        self.assertIn("CLAUDE.md", manifest["requiredFiles"])
        self.assertIn("GEMINI.md", manifest["requiredFiles"])
        self.assertIn(".github/copilot-instructions.md", manifest["requiredFiles"])
        self.assertIn("init.ps1", manifest["requiredFiles"])
        self.assertIn("docs/harness/clean-state-checklist.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/component-inventory.md", manifest["requiredFiles"])
        self.assertIn("scripts/check_pins.py", manifest["requiredFiles"])
        self.assertIn("docs/harness/release-controls.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/research-sources.json", manifest["requiredFiles"])
        self.assertIn("detectedComponents", manifest)

    def test_live_manifest_matches_generated_shared_snippets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        live = json.loads(
            (repo_root / "docs/harness/manifest.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            generated = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        shared_controls = {
            "docs/harness/verification-matrix.md",
            "docs/harness/security-boundary-map.md",
            "docs/harness/release-controls.md",
            "docs/harness/self-healing.md",
            "docs/harness/agent-operating-model.md",
            "docs/harness/entropy-control.md",
        }
        live_snippets = live["requiredHarnessSnippets"]
        for file_name in sorted(shared_controls):
            snippets = generated["requiredHarnessSnippets"][file_name]
            with self.subTest(file_name=file_name):
                self.assertEqual(live_snippets.get(file_name), snippets)

    def test_generated_component_inventory_records_workspace_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "packageManager": "pnpm@10.0.0",
                        "workspaces": ["packages/*"],
                    }
                ),
                encoding="utf-8",
            )
            (root / "pnpm-workspace.yaml").write_text(
                "packages:\n  - packages/*\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "component.yml").write_text(
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - 'packages/**'\n",
                encoding="utf-8",
            )
            create_harness(root)
            inventory = (root / "docs/harness/component-inventory.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("## Detected Workspace Markers", inventory)
        self.assertIn("## Detected Routing Markers", inventory)
        self.assertIn("package.json workspaces", inventory)
        self.assertIn("pnpm-workspace.yaml", inventory)
        self.assertIn(".github/workflows path filters", inventory)
        self.assertIn("package.json workspaces", manifest["detectedWorkspaceMarkers"])
        self.assertIn(
            ".github/workflows path filters",
            manifest["detectedRoutingMarkers"],
        )

    def test_audit_catches_missing_local_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "README.md").write_text(
                "See [missing](docs/harness/missing.md)\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        feedback = next(domain for domain in result.domains if domain.name == "feedback")
        link_check = next(
            check for check in feedback.checks if check.message == "Local Markdown links resolve"
        )
        self.assertFalse(link_check.passed)
        self.assertIn("missing.md", link_check.detail)

    def test_audit_catches_missing_local_markdown_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "README.md").write_text(
                "See [missing anchor](docs/harness/README.md#not-present)\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        feedback = next(domain for domain in result.domains if domain.name == "feedback")
        link_check = next(
            check for check in feedback.checks if check.message == "Local Markdown links resolve"
        )
        self.assertFalse(link_check.passed)
        self.assertIn("missing local anchor", link_check.detail)

    def test_audit_ignores_markdown_links_inside_fenced_code_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "README.md").write_text(
                "```markdown\n"
                "See [example only](docs/harness/missing.md#not-present)\n"
                "```\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        feedback = next(domain for domain in result.domains if domain.name == "feedback")
        link_check = next(
            check for check in feedback.checks if check.message == "Local Markdown links resolve"
        )
        self.assertTrue(link_check.passed, link_check.detail)

    def test_bottleneck_domain_penalizes_overall_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "feature_list.json").unlink()
            (root / "progress.md").unlink()
            (root / "session-handoff.md").unlink()

            result = audit_target(root)

        self.assertEqual(result.bottleneck, "state")
        self.assertLess(result.overall, 85)

    def test_powershell_uses_windows_gradle_wrapper_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "build.gradle").write_text("plugins { id 'java' }\n", encoding="utf-8")
            (root / "gradlew").write_text("#!/usr/bin/env sh\n", encoding="utf-8")
            create_harness(root)
            init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")

        self.assertIn("gradlew.bat", init_ps1)
        self.assertIn("Gradle wrapper not found", init_ps1)

    def test_python3_commands_use_selected_interpreter_in_generated_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("python3 -m unittest",))
            init_sh = (root / "init.sh").read_text(encoding="utf-8")
            init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")

        self.assertIn('"${PYTHON_BIN}" -m unittest', init_sh)
        self.assertIn("Invoke-Native $PythonBin -m unittest", init_ps1)
        self.assertNotIn("\npython3 -m unittest", init_sh)
        self.assertNotIn("\npython3 -m unittest", init_ps1)

    def test_simple_native_powershell_commands_fail_fast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("npm test",))
            init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")

        self.assertIn("Invoke-Native 'npm' 'test'", init_ps1)
        self.assertNotIn("\nnpm test", init_ps1)

    def test_rejects_agent_file_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(ValueError):
                create_harness(root, agent_file="../AGENTS.md")

    @unittest.skipUnless(_supports_file_symlink(), "symlinks unavailable")
    def test_audit_does_not_read_instruction_symlink_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            outside = Path(tmp) / "outside.md"
            root.mkdir()
            outside.write_text(
                "# External\n\nStartup\nDefinition Of Done\nVerification\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").symlink_to(outside)

            result = audit_target(root)

        instructions = next(domain for domain in result.domains if domain.name == "instructions")
        root_instruction = next(
            check
            for check in instructions.checks
            if check.message == "Root agent instruction file exists"
        )
        self.assertFalse(root_instruction.passed)

    def test_audit_flags_markdown_links_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "README.md").write_text(
                "See [outside](../outside.md)\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        feedback = next(domain for domain in result.domains if domain.name == "feedback")
        link_check = next(
            check for check in feedback.checks if check.message == "Local Markdown links resolve"
        )
        self.assertFalse(link_check.passed)
        self.assertIn("outside", link_check.detail)

    def test_audit_flags_windows_absolute_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "README.md").write_text(
                "See [secret](C:\\Users\\person\\secret.md)\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        feedback = next(domain for domain in result.domains if domain.name == "feedback")
        link_check = next(
            check for check in feedback.checks if check.message == "Local Markdown links resolve"
        )
        self.assertFalse(link_check.passed)
        self.assertIn("absolute local path", link_check.detail)

    def test_audit_flags_local_absolute_path_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "README.md").write_text(
                "Local checkout was /Users/person/private/repo\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        scope = next(domain for domain in result.domains if domain.name == "scope")
        path_check = next(
            check
            for check in scope.checks
            if check.message == "Durable harness text avoids local absolute paths"
        )
        self.assertFalse(path_check.passed)
        self.assertIn("README.md", path_check.detail)
        self.assertTrue(
            any("Remove local absolute paths" in item for item in result.recommendations)
        )

    def test_audit_can_explicitly_allow_local_absolute_path_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "README.md").write_text(
                "User-requested local path was C:\\Users\\person\\repo\n",
                encoding="utf-8",
            )

            result = audit_target(root, allow_local_absolute_paths=True)

        scope = next(domain for domain in result.domains if domain.name == "scope")
        path_check = next(
            check
            for check in scope.checks
            if check.message == "Durable harness text avoids local absolute paths"
        )
        self.assertTrue(path_check.passed, path_check.detail)

    def test_manifest_required_files_cannot_point_outside_target(self) -> None:
        for required_file in ("../outside.md", "..\\outside.md"):
            with self.subTest(required_file=required_file):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "repo"
                    (root / "docs" / "harness").mkdir(parents=True)
                    (Path(tmp) / "outside.md").write_text("outside", encoding="utf-8")
                    (root / "docs" / "harness" / "manifest.json").write_text(
                        json.dumps({"requiredFiles": [required_file]}),
                        encoding="utf-8",
                    )

                    result = audit_target(root)

                self.assertTrue(
                    any("outside repo" in failure for failure in result.manifest_failures)
                )

    @unittest.skipUnless(_supports_directory_symlink(), "symlinks unavailable")
    def test_refuses_to_write_through_directory_symlink_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "docs").mkdir()
            (root / "docs" / "harness").symlink_to(outside, target_is_directory=True)

            with self.assertRaises(ValueError):
                create_harness(root)

        self.assertFalse((root / "AGENTS.md").exists())
        self.assertFalse((outside / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
