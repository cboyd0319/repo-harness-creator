from __future__ import annotations

import json
import shlex
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

    def test_audit_respects_declared_macos_only_platform_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            (root / "init.ps1").unlink()
            manifest_path = root / "docs/harness/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["supportedPlatforms"] = {
                "macosOnly": {
                    "python": "3.13+",
                    "macOS": "26+",
                    "note": (
                        "This repository does not support Windows or Linux "
                        "runtime or contributor verification targets."
                    ),
                }
            }
            manifest["requiredFiles"] = [
                path for path in manifest["requiredFiles"] if path != "init.ps1"
            ]
            manifest_path.write_text(
                f"{json.dumps(manifest, indent=2)}\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        tools = next(domain for domain in result.domains if domain.name == "tools")
        environment = next(
            domain for domain in result.domains if domain.name == "environment"
        )
        self.assertFalse(
            any("PowerShell" in check.message for check in tools.checks)
        )
        self.assertTrue(
            next(
                check
                for check in environment.checks
                if check.message == "Runtime boundary is documented"
            ).passed
        )
        self.assertGreaterEqual(result.overall, 85)

    def test_platform_routers_follow_custom_agent_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            create_harness(root, agent_file="PROJECT_AGENTS.md")
            claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            gemini = (root / "GEMINI.md").read_text(encoding="utf-8")
            copilot = (root / ".github/copilot-instructions.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            result = audit_target(root)

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
        self.assertEqual(result.overall, 100)

    def test_generated_harness_omits_repo_local_research_tool_mandates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)

            generated_text = "\n".join(
                (root / relative).read_text(encoding="utf-8")
                for relative in (
                    "AGENTS.md",
                    "CLAUDE.md",
                    "GEMINI.md",
                    ".github/copilot-instructions.md",
                )
            )

        forbidden_patterns = (
            r"(?i)\b(?:must|required|always)\s+(?:use|run)\s+(?:antigravity|agy)\b",
            r"(?i)\bresearch(?:\s+tasks?)?\b.{0,80}\b(?:antigravity|agy)\b",
            r"(?i)\b(?:antigravity|agy)\b.{0,80}\bresearch(?:\s+tasks?)?\b",
        )
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotRegex(generated_text, pattern)

        self.assertRegex(
            generated_text,
            r"Antigravity can consume `AGENTS\.md`\s+directly",
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
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
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
        self.assertNotIn("schedule:", ci)
        self.assertIn("REVIEW REQUIRED: verify evidence gating is off by default", ci)
        self.assertIn("name: Read-only sync preflight", ci)
        self.assertIn("continue-on-error: true", ci)
        self.assertIn("command: sync", ci)
        self.assertIn('require-verify-evidence: "false"', ci)
        self.assertIn("sync-exit-code", ci)
        self.assertIn("steps.sync.outputs['sync-exit-code'] == '2'", ci)
        self.assertLess(ci.index("command: sync"), ci.index("command: audit"))
        self.assertIn("contents: write", self_heal)
        self.assertIn('agent-file: "AGENTS.md"', self_heal)
        ci_required_snippets = manifest["requiredHarnessSnippets"][
            ".github/workflows/harnessforge.yml"
        ]
        self.assertIn("command: sync", ci_required_snippets)
        self.assertIn("require-verify-evidence", ci_required_snippets)
        self.assertIn("Read-only sync preflight", ci_required_snippets)
        git_add_line = next(
            line.strip()
            for line in self_heal.replace(" \\\n            ", " ").splitlines()
            if line.strip().startswith("git add ")
        )
        staged_paths = shlex.split(git_add_line)[3:]
        for path in (
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            ".github/copilot-instructions.md",
            "docs/harness",
        ):
            with self.subTest(path=path):
                self.assertIn(path, staged_paths)
        self.assertIn("git add --", git_add_line)
        self.assertIn("gh pr create", self_heal)
        self.assertNotIn("schedule:", self_heal)
        self.assertNotIn("refresh_research.py", self_heal)

    def test_self_heal_workflow_respects_custom_agent_file(self) -> None:
        cases = (
            ("PROJECT_AGENTS.md", ("CLAUDE.md", "GEMINI.md"), ("AGENTS.md",)),
            ("GEMINI.md", ("CLAUDE.md",), ("AGENTS.md",)),
        )
        for agent_file, expected_paths, absent_paths in cases:
            with self.subTest(agent_file=agent_file):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    create_harness(
                        root,
                        agent_file=agent_file,
                        with_self_heal_workflow=True,
                    )
                    self_heal = (
                        root / ".github/workflows/harness-self-heal.yml"
                    ).read_text(encoding="utf-8")

                normalized = self_heal.replace(" \\\n            ", " ")
                git_add_line = next(
                    line.strip()
                    for line in normalized.splitlines()
                    if line.strip().startswith("git add ")
                )
                staged_paths = shlex.split(git_add_line)[3:]

                self.assertIn(f"agent-file: \"{agent_file}\"", self_heal)
                self.assertIn(agent_file, staged_paths)
                self.assertIn(".github/copilot-instructions.md", staged_paths)
                for path in expected_paths:
                    self.assertIn(path, staged_paths)
                for path in absent_paths:
                    self.assertNotIn(path, staged_paths)

    def test_self_heal_workflow_respects_platform_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                platform_contract="windows-only",
                with_self_heal_workflow=True,
            )
            self_heal = (root / ".github/workflows/harness-self-heal.yml").read_text(
                encoding="utf-8"
            )

        normalized = self_heal.replace(" \\\n            ", " ")
        git_add_line = next(
            line.strip()
            for line in normalized.splitlines()
            if line.strip().startswith("git add ")
        )
        staged_paths = shlex.split(git_add_line)[3:]

        self.assertIn("pwsh -NoProfile -File ./init.ps1", self_heal)
        self.assertNotIn("./init.sh", self_heal)
        self.assertIn("init.ps1", staged_paths)
        self.assertNotIn("init.sh", staged_paths)

    def test_generated_docs_separate_workflow_and_action_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                with_ci_workflow=True,
                with_self_heal_workflow=True,
            )
            self_heal_workflow = (
                root / ".github/workflows/harness-self-heal.yml"
            ).read_text(encoding="utf-8")
            self_healing = (root / "docs/harness/self-healing.md").read_text(
                encoding="utf-8"
            )
            security = (root / "docs/harness/security-boundary-map.md").read_text(
                encoding="utf-8"
            )
            readme = (root / "docs/harness/README.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertNotIn("schedule:", self_heal_workflow)
        self.assertNotIn("cron:", self_heal_workflow)
        self.assertNotIn("refresh_research.py", self_heal_workflow)
        self.assertIn("## Workflow Boundary", self_healing)
        self.assertIn("published HarnessForge Action", self_healing)
        self.assertIn("Live HarnessForge repository workflow", self_healing)
        self.assertIn("does not schedule jobs", self_healing)
        self.assertIn("Do not copy that behavior", self_healing)
        self.assertIn("Workflow surfaces", security)
        self.assertIn("published HarnessForge composite Action", security)
        self.assertIn("does not schedule, commit, push, or open pull requests", security)
        self.assertIn("project-owned generated files", readme)
        self.assertIn(
            "Workflow Boundary",
            manifest["requiredHarnessSnippets"]["docs/harness/self-healing.md"],
        )
        self.assertIn(
            "Workflow surfaces",
            manifest["requiredHarnessSnippets"][
                "docs/harness/security-boundary-map.md"
            ],
        )

    def test_generated_harness_avoids_repo_local_workflow_preferences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                with_ci_workflow=True,
                with_self_heal_workflow=True,
            )

            generated_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file()
            )
            sources = (root / "docs/harness/sources.md").read_text(encoding="utf-8")

        self.assertNotRegex(generated_text, r"(?i)\blocal commits?\b")
        self.assertNotIn("Local production harness patterns", generated_text)
        self.assertIn("Reviewed production harness patterns", sources)
        self.assertIn("project checkpoints", generated_text)

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
            (root / "pins.toml").write_text(
                "[agent_cli]\n"
                'codex = "0.20.0"\n'
                "\n[agent_cli_integrity]\n"
                'codex = "sha512-reviewed"\n',
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "@openai/codex": "0.21.0",
                            "left-pad": "^1.3.0",
                        }
                    }
                ),
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
        self.assertIn("pins.toml", strict.stdout)

    def test_generated_pin_checker_allows_rust_build_and_container_stage_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[package]\nname = 'demo'\nversion = '0.1.0'\n",
                encoding="utf-8",
            )
            (root / "build.rs").write_text("fn main() {}\n", encoding="utf-8")
            (root / "Dockerfile").write_text(
                "FROM python:3.13@sha256:abc123 AS builder\n"
                "RUN true\n"
                "FROM builder\n",
                encoding="utf-8",
            )
            create_harness(root)
            script = root / "scripts" / "check_pins.py"

            strict = subprocess.run(
                [sys.executable, str(script), "--root", str(root), "--strict"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(strict.returncode, 0, strict.stdout)

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
        self.assertIn("docs/harness/sensor-registry.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/source-record.schema.json", manifest["requiredFiles"])
        self.assertIn("docs/harness/source-record-example.json", manifest["requiredFiles"])
        self.assertIn("detectedComponents", manifest)

    def test_manifest_records_generated_file_ownership_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(manifest["generator"]["name"], "harnessforge")
        self.assertEqual(manifest["generatedFiles"]["AGENTS.md"]["ownership"], "generated")
        self.assertEqual(
            manifest["generatedFiles"]["AGENTS.md"]["template"],
            "agents.md.tmpl",
        )
        self.assertRegex(
            manifest["generatedFiles"]["AGENTS.md"]["contentSha256"],
            r"^[0-9a-f]{64}$",
        )
        self.assertRegex(
            manifest["generatedFiles"]["AGENTS.md"]["templateSha256"],
            r"^[0-9a-f]{64}$",
        )
        self.assertIn("docs/harness/feature-privacy-labels.json", manifest["reviewRequired"])

    def test_generated_placeholders_mark_project_review_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            review_files = tuple(manifest["reviewRequired"])

            for relative_path in review_files:
                with self.subTest(relative_path=relative_path):
                    content = (root / relative_path).read_text(encoding="utf-8")
                    self.assertIn("REVIEW REQUIRED", content)

    def test_generated_evidence_docs_route_verify_run_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            create_harness(root)
            matrix = (root / "docs/harness/verification-matrix.md").read_text(
                encoding="utf-8"
            )
            evidence = (root / "docs/harness/evidence-log.md").read_text(
                encoding="utf-8"
            )
            release = (root / "docs/harness/release-controls.md").read_text(
                encoding="utf-8"
            )
            normalized_matrix = " ".join(matrix.split())

        self.assertIn("harnessforge verify --target . --json --run", matrix)
        self.assertIn(
            "--json-report docs/harness/evidence/verify-<date>.json",
            normalized_matrix,
        )
        self.assertIn("docs/harness/evidence/verify-<date>.json", matrix)
        self.assertIn("`failed`, `timed_out`, or `blocked`", matrix)
        self.assertIn("does not replace `harnessforge audit", matrix)
        self.assertIn("does not prove real-agent effectiveness", matrix)

        self.assertIn("target-relative report path", evidence)
        self.assertIn("harnessforge verify --target . --run --json-report", evidence)
        self.assertIn("Do not paste full stdout", evidence)
        self.assertIn("failed, timed_out, or blocked", evidence)

        self.assertIn("--run --json-report", release)
        self.assertIn("failed, timed_out, or blocked", release)
        self.assertIn("owner, risk, and next action", release)
        self.assertIn("audit score", release)
        self.assertIn("real-agent effectiveness", release)

    def test_generated_sensor_registry_requires_project_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                commands=("python -m pytest", "python -m ruff check ."),
            )
            registry = (root / "docs/harness/sensor-registry.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("docs/harness/sensor-registry.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/sensor-registry.md", manifest["reviewRequired"])
        self.assertEqual(
            manifest["generatedFiles"]["docs/harness/sensor-registry.md"]["ownership"],
            "generated",
        )
        self.assertIn("# Sensor Registry", registry)
        self.assertIn("REVIEW REQUIRED", registry)
        self.assertIn("Owner", registry)
        self.assertIn("Source", registry)
        self.assertIn("Purpose", registry)
        self.assertIn("Retire When", registry)
        self.assertIn("python -m pytest", registry)
        self.assertIn("python -m ruff check .", registry)
        self.assertIn("does not prove real-agent effectiveness", registry)

    def test_generated_source_record_schema_guides_project_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            schema = json.loads(
                (root / "docs/harness/source-record.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            example = json.loads(
                (root / "docs/harness/source-record-example.json").read_text(
                    encoding="utf-8"
                )
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn(
            "docs/harness/source-record.schema.json",
            manifest["requiredFiles"],
        )
        self.assertIn(
            "docs/harness/source-record-example.json",
            manifest["requiredFiles"],
        )
        self.assertIn(
            "docs/harness/source-record-example.json",
            manifest["reviewRequired"],
        )
        self.assertEqual(schema["title"], "HarnessForge Project Source Record")
        schema_text = json.dumps(schema)
        self.assertIn("targetRelativePath", schema_text)
        self.assertIn("machine-local absolute paths", schema_text)
        self.assertIn("docs/harness/research-sources.json", schema_text)
        self.assertEqual(example["id"], "source-record-example")
        self.assertEqual(example["reviewStatus"], "REVIEW REQUIRED")
        self.assertEqual(
            example["source"]["targetRelativePath"],
            "docs/architecture.md",
        )
        self.assertIn("REVIEW REQUIRED", json.dumps(example))

    def test_missing_verification_placeholder_blocks_generated_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            result = audit_target(root)
            init_sh = (root / "init.sh").read_text(encoding="utf-8")
            init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")
            feedback = next(
                domain for domain in result.domains if domain.name == "feedback"
            )

        self.assertIn(
            "REVIEW REQUIRED: No project verification check detected", init_sh
        )
        self.assertIn("exit 1", init_sh)
        self.assertIn(
            "Write-Error 'REVIEW REQUIRED: No project verification check detected",
            init_ps1,
        )
        self.assertIn("exit 1", init_ps1)
        self.assertLess(result.overall, 100)
        self.assertFalse(
            next(
                check
                for check in feedback.checks
                if check.message == "Project verification command is configured"
            ).passed
        )

    def test_generated_docs_only_repo_audits_cross_platform(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Docs\n", encoding="utf-8")
            create_harness(root)

            result = audit_target(root)
            environment = next(
                domain for domain in result.domains if domain.name == "environment"
            )
            feedback = next(
                domain for domain in result.domains if domain.name == "feedback"
            )

        self.assertLess(result.overall, 100)
        self.assertTrue(
            next(
                check
                for check in environment.checks
                if check.message == "Runtime manifest or explicit generic profile is discoverable"
            ).passed
        )
        self.assertTrue(
            next(
                check
                for check in environment.checks
                if check.message == "Runner and path handling is called out"
            ).passed
        )
        self.assertFalse(
            next(
                check
                for check in feedback.checks
                if check.message == "Project verification command is configured"
            ).passed
        )

    def test_generated_swift_and_shell_repos_supply_environment_evidence(self) -> None:
        cases = (
            (
                "swift",
                {
                    "Package.swift": "// swift-tools-version: 6.2\n",
                    "Makefile": ".PHONY: test\n\ntest:\n\t@swift test\n",
                },
            ),
            (
                "shell",
                {
                    "fix_app.sh": "#!/usr/bin/env bash\n",
                    "tools/validate_harness.sh": "#!/usr/bin/env bash\n",
                },
            ),
        )
        for expected_stack, files in cases:
            with self.subTest(expected_stack=expected_stack):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    for relative_path, content in files.items():
                        path = root / relative_path
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(content, encoding="utf-8")
                    create_harness(root)

                    result = audit_target(root)
                    manifest = json.loads(
                        (root / "docs/harness/manifest.json").read_text(
                            encoding="utf-8"
                        )
                    )
                    environment = next(
                        domain
                        for domain in result.domains
                        if domain.name == "environment"
                    )

                self.assertEqual(manifest["detectedStack"], expected_stack)
                self.assertTrue(
                    next(
                        check
                        for check in environment.checks
                        if check.message
                        == "Runtime manifest or explicit generic profile is discoverable"
                    ).passed
                )

    def test_generated_nested_monorepo_without_root_manifest_audits(self) -> None:
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
            create_harness(root)

            result = audit_target(root)
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(manifest["detectedStack"], "monorepo")
        self.assertEqual(result.overall, 100)
        self.assertIn(
            "npm --prefix component-a test",
            manifest["verificationCommands"],
        )
        self.assertIn(
            "python -m compileall component-b",
            manifest["verificationCommands"],
        )

    def test_custom_agent_file_supplies_environment_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                "# Existing agent notes\n\nKeep this file untouched.\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            create_harness(root, agent_file="HARNESSFORGE_AGENTS.md")

            result = audit_target(root)
            generated_agent = (root / "HARNESSFORGE_AGENTS.md").read_text(
                encoding="utf-8"
            )
            environment = next(
                domain for domain in result.domains if domain.name == "environment"
            )

        self.assertEqual(result.overall, 100)
        self.assertIn("side-by-side HarnessForge entrypoint", generated_agent)
        self.assertIn("not the default `AGENTS.md`", generated_agent)
        self.assertTrue(
            next(
                check
                for check in environment.checks
                if check.message == "Runner and path handling is called out"
            ).passed
        )

    def test_enhance_existing_instruction_files_preserves_project_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "MODULE.bazel").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing agent notes\n\nKeep local operating rules.\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Existing Claude notes\n\nKeep Claude-specific reminders.\n",
                encoding="utf-8",
            )
            (root / ".claude").mkdir()
            (root / ".claude" / "AGENTS.md").write_text(
                "# Existing hidden agent notes\n\nKeep hidden agent reminders.\n",
                encoding="utf-8",
            )
            (root / ".claude" / "CLAUDE.md").write_text(
                "# Existing hidden Claude notes\n\nKeep hidden Claude reminders.\n",
                encoding="utf-8",
            )

            _, writes = create_harness(root, enhance_existing=True)
            result = audit_target(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            hidden_agents = (root / ".claude" / "AGENTS.md").read_text(
                encoding="utf-8"
            )
            hidden_claude = (root / ".claude" / "CLAUDE.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        statuses = {
            write.path.resolve().relative_to(root.resolve()).as_posix(): write.status
            for write in writes
        }
        self.assertEqual(statuses["AGENTS.md"], "enhanced")
        self.assertEqual(statuses["CLAUDE.md"], "enhanced")
        self.assertEqual(statuses[".claude/AGENTS.md"], "enhanced")
        self.assertEqual(statuses[".claude/CLAUDE.md"], "enhanced")
        self.assertIn("Keep local operating rules.", agents)
        self.assertIn("HarnessForge Quality Addendum", agents)
        self.assertIn("Definition Of Done", agents)
        self.assertIn("feature_list.json", agents)
        self.assertIn("remote CI", agents)
        self.assertIn("stubbed", agents)
        self.assertIn("Detected project context", agents)
        self.assertIn("Bazel markers detected", agents)
        self.assertIn("Keep Claude-specific reminders.", claude)
        self.assertIn("@AGENTS.md", claude)
        self.assertIn("Shared repo guidance", claude)
        self.assertIn("Keep hidden agent reminders.", hidden_agents)
        self.assertIn("HarnessForge Quality Addendum", hidden_agents)
        self.assertIn("../AGENTS.md", hidden_agents)
        self.assertIn("Keep hidden Claude reminders.", hidden_claude)
        self.assertIn("@../AGENTS.md", hidden_claude)
        self.assertEqual(result.overall, 100)
        self.assertEqual(
            manifest["generatedFiles"]["AGENTS.md"]["ownership"],
            "project-enhanced",
        )

    def test_agents_file_includes_detected_project_context(self) -> None:
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
            (root / ".bazelrc").write_text("common --announce_rc\n", encoding="utf-8")
            (root / ".bazelversion").write_text("9.1.1\n", encoding="utf-8")
            (root / "Package.swift").write_text(
                "// swift-tools-version: 6.2\n",
                encoding="utf-8",
            )
            (root / "Dockerfile").write_text("FROM python:3.13-slim\n", encoding="utf-8")
            (root / "action.yml").write_text("runs:\n  using: composite\n", encoding="utf-8")
            (root / ".claude").mkdir()
            (root / ".claude" / "CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
            (root / "crates" / "web").mkdir(parents=True)
            (root / "crates" / "web" / "package.json").write_text(
                json.dumps({"scripts": {"build": "vite build"}}),
                encoding="utf-8",
            )
            (root / "scripts" / "release").mkdir(parents=True)
            (root / "scripts" / "release" / "BUILD").write_text("", encoding="utf-8")
            (root / "scripts" / "release" / "publish.sh").write_text(
                "#!/usr/bin/env bash\n",
                encoding="utf-8",
            )
            (root / "src-tauri").mkdir()
            (root / "src-tauri" / "Cargo.toml").write_text(
                "[package]\nname='desktop'\nversion='0.1.0'\n",
                encoding="utf-8",
            )
            (root / "infra").mkdir()
            (root / "infra" / "main.tf").write_text("terraform {}\n", encoding="utf-8")
            (root / "third_party" / "vendor").mkdir(parents=True)
            (root / "third_party" / "vendor" / "BUILD").write_text("", encoding="utf-8")
            (root / "scripts" / "docs").mkdir(parents=True)
            (root / "scripts" / "docs" / "BUILD").write_text("", encoding="utf-8")
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("Rust workspace", agents)
        self.assertIn("Swift Package Manager", agents)
        self.assertIn("Bazel markers", agents)
        self.assertIn("Bazel runtime routing files", agents)
        self.assertIn("vendored components", agents)
        self.assertIn("Release or package scripts", agents)
        self.assertIn("Documentation or site-generation", agents)
        self.assertIn("Terraform or infrastructure files", agents)
        self.assertIn("Shell entrypoints", agents)
        self.assertIn("Container image definitions", agents)
        self.assertIn("Tauri desktop surface", agents)
        self.assertIn("JavaScript or TypeScript subprojects", agents)
        self.assertIn("GitHub Action surface", agents)
        self.assertIn("Existing hidden agent instruction files", agents)

    def test_agents_file_includes_generic_spec_runner_and_docgen_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[workspace]\nmembers = ['crates/docgen']\n",
                encoding="utf-8",
            )
            (root / "crates" / "docgen").mkdir(parents=True)
            (root / "crates" / "docgen" / "Cargo.toml").write_text(
                "[package]\nname='project-docgen'\nversion='0.1.0'\n",
                encoding="utf-8",
            )
            (root / "justfile").write_text(
                "gen-docs-check:\n\tcargo run -p project-docgen -- --check\n",
                encoding="utf-8",
            )
            (root / "specs" / "architecture").mkdir(parents=True)
            (root / "specs" / "work-items").mkdir(parents=True)
            (root / "specs" / "foundation.md").write_text(
                "# Foundation\n",
                encoding="utf-8",
            )
            (root / "specs" / "architecture" / "design.md").write_text(
                "# Design\n",
                encoding="utf-8",
            )
            (root / "specs" / "work-items" / "0000-template.md").write_text(
                "# Work Item Template\n",
                encoding="utf-8",
            )
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("Structured project specs detected", agents)
        self.assertIn("Repository task runner detected", agents)
        self.assertIn("Generated documentation checks detected", agents)
        self.assertIn("structured project specs", manifest["detectedWorkspaceMarkers"])
        self.assertIn("justfile", manifest["detectedRoutingMarkers"])
        self.assertIn("just gen-docs-check", manifest["verificationCommands"])

    def test_agents_file_includes_agent_skill_catalog_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "demo").mkdir(parents=True)
            (root / "skills" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\n---\n",
                encoding="utf-8",
            )
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "marketplace.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("Agent skill surfaces detected", agents)
        self.assertIn("Agent plugin manifests detected", agents)
        self.assertIn("agent skills", manifest["detectedRoutingMarkers"])
        self.assertIn(".claude-plugin", manifest["detectedRoutingMarkers"])

    def test_agents_file_includes_docs_catalog_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# Catalog\n\n| Name | Link |\n| --- | --- |\n",
                encoding="utf-8",
            )
            (root / "CONTRIBUTING.md").write_text(
                "# Contributing\n",
                encoding="utf-8",
            )
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("Documentation or catalog repository detected", agents)
        self.assertNotIn("No stack-specific context", agents)

    def test_agents_file_reports_component_inventory_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(85):
                component = root / f"pkg-{index:02d}"
                component.mkdir()
                (component / "package.json").write_text("{}", encoding="utf-8")
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("Component inventory reached", agents)
        self.assertIn("docs/harness/component-inventory.md", agents)

    def test_agents_file_includes_detected_quality_surface_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "native.cpp").write_text(
                "int main() { return 0; }\n",
                encoding="utf-8",
            )
            (root / "App.sln").write_text("\n", encoding="utf-8")
            (root / "composer.json").write_text("{}\n", encoding="utf-8")
            (root / "Gemfile").write_text(
                "source 'https://rubygems.org'\n",
                encoding="utf-8",
            )
            (root / "assets").mkdir()
            (root / "assets" / "demo.js").write_text(
                "console.log('demo')\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(
                "on:\n"
                "  pull_request:\n"
                "    paths:\n"
                "      - 'src/**'\n"
                "jobs:\n"
                "  test:\n"
                "    defaults:\n"
                "      run:\n"
                "        working-directory: src\n",
                encoding="utf-8",
            )
            (root / ".devcontainer").mkdir()
            (root / ".devcontainer" / "devcontainer.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("C/C++ or native-code files detected", agents)
        self.assertIn(".NET solution or project files detected", agents)
        self.assertIn("PHP or Composer surface detected", agents)
        self.assertIn("Ruby or Bundler surface detected", agents)
        self.assertIn("JavaScript or TypeScript files detected without", agents)
        self.assertIn("Existing GitHub workflow surfaces detected", agents)
        self.assertIn("path filters", agents)
        self.assertIn("`working-directory` routing", agents)
        self.assertIn("Devcontainer configuration detected", agents)
        self.assertIn("Existing root agent instruction files detected", agents)
        self.assertIn("CLAUDE.md", agents)

    def test_audit_requires_instructions_to_route_to_detected_spec_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            create_harness(root)
            (root / ".specify").mkdir()
            (root / ".specify" / "feature.json").write_text(
                json.dumps({"feature_directory": "specs/001-login"}),
                encoding="utf-8",
            )
            feature = root / "specs" / "001-login"
            feature.mkdir(parents=True)
            (feature / "spec.md").write_text(
                "# Feature Specification\n\n- **FR-001**: Login\n",
                encoding="utf-8",
            )

            result = audit_target(root)

        instructions = next(
            domain for domain in result.domains if domain.name == "instructions"
        )
        sync_check = next(
            check
            for check in instructions.checks
            if check.message
            == "Instruction files route to detected source-of-truth specs"
        )
        self.assertFalse(sync_check.passed)
        self.assertIn("specs/001-login", sync_check.detail)
        self.assertLess(result.overall, 100)

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
            "docs/harness/sensor-registry.md",
            "docs/harness/source-record.schema.json",
            "docs/harness/source-record-example.json",
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
