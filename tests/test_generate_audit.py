from __future__ import annotations

import json
import re
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
            self.assertIn("Core harness contract", content)
            self.assertIn("effective agent", content)
            self.assertIn("Implementation Discipline", content)
            self.assertIn("standard library", content)
            self.assertIn("intentional simplification", content)
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
            facts = (root / "docs/harness/authoritative-facts.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        written = {write.path.name for write in writes if write.status == "written"}
        self.assertEqual(profile.stack, "python")
        self.assertIn("AGENTS.md", written)
        self.assertIn("CLAUDE.md", written)
        self.assertIn("GEMINI.md", written)
        self.assertIn("copilot-instructions.md", written)
        self.assertIn("authoritative-facts.md", written)
        self.assertIn("check_pins.py", written)
        self.assertIn("@AGENTS.md", claude)
        self.assertIn("@AGENTS.md", gemini)
        self.assertIn("../AGENTS.md", copilot)
        self.assertIn("Security boundary map", copilot)
        self.assertIn("Authoritative Facts And Docs Routing", facts)
        self.assertIn("Boundary Types Covered", facts)
        self.assertIn("Generated harness files", facts)
        self.assertIn("GitHub Action", facts)
        self.assertIn(
            "docs/harness/authoritative-facts.md", manifest["requiredFiles"]
        )
        self.assertIn(
            "docs/harness/authoritative-facts.md", manifest["reviewRequired"]
        )
        self.assertIn(
            "Boundary Types Covered",
            manifest["requiredHarnessSnippets"][
                "docs/harness/authoritative-facts.md"
            ],
        )
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

    def test_generated_harness_markdown_footprint_stays_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            create_harness(
                root,
                commands=("python -m unittest discover -s tests",),
            )
            markdown = [
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() == ".md"
            ]
            generated_files = [path for path in root.rglob("*") if path.is_file()]
            sizes = {
                path.relative_to(root).as_posix(): len(
                    path.read_text(encoding="utf-8")
                )
                for path in markdown
            }
            line_count = sum(
                len(path.read_text(encoding="utf-8").splitlines())
                for path in markdown
            )
            total_bytes = sum(path.stat().st_size for path in generated_files)
            total_lines = sum(
                len(path.read_text(encoding="utf-8").splitlines())
                for path in generated_files
            )
            result = audit_target(root)

        self.assertEqual(result.overall, 100)
        self.assertLess(total_bytes, 140_000)
        self.assertLess(total_lines, 3_000)
        self.assertLess(sum(sizes.values()), 70_000)
        self.assertLess(line_count, 1_500)
        self.assertFalse((root / "docs/harness/research/research-sources.json").exists())
        self.assertLess(sizes["docs/harness/README.md"], 6_500)
        self.assertLess(sizes["docs/harness/state/roadmap.md"], 8_000)
        self.assertLess(sizes["AGENTS.md"], 6_000)

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
            self.assertFalse((root / "docs/harness/operations/self-healing.md").exists())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resolved_root = root.resolve()
            _, writes = create_harness(
                root,
                with_ci_workflow=True,
            )
            ci = (root / ".github/workflows/harnessforge.yml").read_text(
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
            self_heal_workflow_exists = (
                root / ".github/workflows/harness-self-heal.yml"
            ).exists()
            self_healing_doc_exists = (
                root / "docs/harness/operations/self-healing.md"
            ).exists()

        self.assertIn(".github/workflows/harnessforge.yml", written)
        self.assertNotIn(".github/workflows/harness-self-heal.yml", written)
        self.assertFalse(self_heal_workflow_exists)
        self.assertFalse(self_healing_doc_exists)
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
        ci_required_snippets = manifest["requiredHarnessSnippets"][
            ".github/workflows/harnessforge.yml"
        ]
        self.assertIn("command: sync", ci_required_snippets)
        self.assertIn("require-verify-evidence", ci_required_snippets)
        self.assertIn("Read-only sync preflight", ci_required_snippets)
        self.assertNotIn(".github/workflows/harness-self-heal.yml", manifest["requiredFiles"])
        self.assertNotIn("docs/harness/operations/self-healing.md", manifest["requiredFiles"])
        self.assertNotIn(
            ".github/workflows/harness-self-heal.yml",
            manifest["requiredHarnessSnippets"],
        )
        self.assertNotIn(
            "docs/harness/operations/self-healing.md",
            manifest["requiredHarnessSnippets"],
        )

    def test_generated_docs_separate_workflow_and_action_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                with_ci_workflow=True,
            )
            ci = (root / ".github/workflows/harnessforge.yml").read_text(
                encoding="utf-8"
            )
            security = (root / "docs/harness/boundaries/security-boundary-map.md").read_text(
                encoding="utf-8"
            )
            readme = (root / "docs/harness/README.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertNotIn("schedule:", ci)
        self.assertNotIn("cron:", ci)
        self.assertNotIn("refresh_research.py", ci)
        self.assertIn("Workflow surfaces", security)
        self.assertIn("published HarnessForge composite Action", security)
        self.assertIn("does not schedule, commit, push, or open pull requests", security)
        self.assertIn("Five Core Subsystems", readme)
        self.assertIn("Effective Agent Boundary", readme)
        self.assertIn("The model is the LLM", readme)
        self.assertIn("changes effective agent behavior", readme)
        self.assertIn("instructions + tools + environment + state + feedback", readme)
        self.assertIn("least privilege", readme)
        self.assertIn("verification commands explicit", readme)
        self.assertIn("Bottleneck And Harness Debt", readme)
        self.assertIn("controlled-variable exclusion tests", readme)
        self.assertIn("failure records and attribution", readme)
        self.assertIn("project-owned generated files", readme)
        self.assertNotIn("self-healing.md", readme)
        self.assertNotIn("docs/harness/operations/self-healing.md", manifest["requiredFiles"])
        self.assertIn(
            "Workflow surfaces",
            manifest["requiredHarnessSnippets"][
                "docs/harness/boundaries/security-boundary-map.md"
            ],
        )

    def test_generated_harness_avoids_repo_local_workflow_preferences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(
                root,
                with_ci_workflow=True,
            )

            generated_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file()
            )
            sources = (root / "docs/harness/research/sources.md").read_text(encoding="utf-8")

        self.assertNotRegex(generated_text, r"(?i)\blocal commits?\b")
        self.assertNotRegex(generated_text, r"(?i)\bself-heal(?:ing)?\b")
        self.assertNotIn("Local production harness patterns", generated_text)
        self.assertIn("Reviewed production harness patterns", sources)
        self.assertIn("https://agentskills.io/specification.md", sources)
        self.assertIn("https://agentskills.io/skill-creation/best-practices.md", sources)
        self.assertIn("https://agentskills.io/skill-creation/evaluating-skills.md", sources)
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
        self.assertIn("docs/harness/state/clean-state-checklist.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/boundaries/component-inventory.md", manifest["requiredFiles"])
        self.assertIn("scripts/check_pins.py", manifest["requiredFiles"])
        self.assertIn("docs/harness/release/release-controls.md", manifest["requiredFiles"])
        self.assertNotIn("docs/harness/research/research-sources.json", manifest["requiredFiles"])
        self.assertIn("docs/harness/state/roadmap.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/feedback/sensor-registry.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/research/source-record.schema.json", manifest["requiredFiles"])
        self.assertIn("docs/harness/research/source-record-example.json", manifest["requiredFiles"])
        self.assertIn("docs/harness/evidence/first-agent-review.json", manifest["requiredFiles"])
        self.assertIn(".agents/skills/harness/SKILL.md", manifest["requiredFiles"])
        self.assertIn(
            ".agents/skills/harness/references/repo-harness.md",
            manifest["requiredFiles"],
        )
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
        self.assertIn("docs/harness/boundaries/feature-privacy-labels.json", manifest["reviewRequired"])
        self.assertIn("docs/harness/evidence/first-agent-review.json", manifest["reviewRequired"])
        self.assertIn(".agents/skills/harness/SKILL.md", manifest["reviewRequired"])

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
            matrix = (root / "docs/harness/feedback/verification-matrix.md").read_text(
                encoding="utf-8"
            )
            evidence = (root / "docs/harness/evidence/evidence-log.md").read_text(
                encoding="utf-8"
            )
            release = (root / "docs/harness/release/release-controls.md").read_text(
                encoding="utf-8"
            )
            normalized_matrix = " ".join(matrix.split())

        self.assertIn("repo-owned commands", matrix)
        self.assertIn("harnessforge verify --target . --json --run", matrix)
        self.assertIn(
            "--json-report docs/harness/evidence/verify-<date>.json",
            normalized_matrix,
        )
        self.assertIn("docs/harness/evidence/verify-<date>.json", matrix)
        self.assertIn("`failed`, `timed_out`, or `blocked`", matrix)
        self.assertIn("evidence ladder", matrix)
        self.assertIn("System/user-flow checks", matrix)
        self.assertIn("agent-oriented failure messages", matrix)
        self.assertIn(
            "optional unless the repo owner adopts HarnessForge",
            normalized_matrix,
        )
        self.assertIn("does not prove real-agent effectiveness", matrix)

        self.assertIn("target-relative report path", evidence)
        self.assertIn("repo-owned verification command", evidence)
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
            registry = (root / "docs/harness/feedback/sensor-registry.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("docs/harness/feedback/sensor-registry.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/feedback/sensor-registry.md", manifest["reviewRequired"])
        self.assertEqual(
            manifest["generatedFiles"]["docs/harness/feedback/sensor-registry.md"]["ownership"],
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
        self.assertIn("docs/harness/state/roadmap.md", registry)
        self.assertIn("Agent-Oriented Failure Feedback", registry)
        self.assertIn("what failed", registry)
        self.assertIn("Pending project-specific decision.", registry)
        self.assertIn("Pending owner.", registry)
        self.assertIn("Pending retirement condition.", registry)
        self.assertEqual(registry.count("REVIEW REQUIRED"), 1)
        self.assertIn("does not prove real-agent effectiveness", registry)

    def test_generated_first_agent_task_guides_harness_improvement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            task = (root / "docs/harness/state/first-agent-task.md").read_text(
                encoding="utf-8"
            )
            review = json.loads(
                (root / "docs/harness/evidence/first-agent-review.json").read_text(
                    encoding="utf-8"
                )
            )
            skill = (root / ".agents/skills/harness/SKILL.md").read_text(
                encoding="utf-8"
            )
            skill_reference = (
                root / ".agents/skills/harness/references/repo-harness.md"
            ).read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("docs/harness/state/first-agent-task.md", agents)
        self.assertIn(".agents/skills/harness/SKILL.md", agents)
        self.assertIn("docs/harness/state/first-agent-task.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/state/first-agent-task.md", manifest["reviewRequired"])
        self.assertIn("docs/harness/evidence/first-agent-review.json", manifest["requiredFiles"])
        self.assertIn("docs/harness/evidence/first-agent-review.json", manifest["reviewRequired"])
        self.assertIn(".agents/skills/harness/SKILL.md", manifest["requiredFiles"])
        self.assertIn(
            ".agents/skills/harness/references/repo-harness.md",
            manifest["requiredFiles"],
        )
        self.assertIn(".agents/skills/harness/SKILL.md", manifest["reviewRequired"])
        self.assertEqual(
            manifest["generatedFiles"]["docs/harness/state/first-agent-task.md"][
                "ownership"
            ],
            "generated",
        )
        self.assertIn("# First-Agent Harness Improvement Task", task)
        self.assertIn("REVIEW REQUIRED", task)
        self.assertIn("component inventory", task)
        self.assertIn("readiness signals", task)
        self.assertIn("verification matrix", task)
        self.assertIn("evidence log", task)
        self.assertIn("security boundary", task)
        self.assertIn("fresh-session test", task)
        self.assertIn("source-of-truth locale", task)
        self.assertIn("runtime and process observability", task)
        self.assertIn("Behavior, verification, status, and evidence", task)
        self.assertIn("Do not overwrite project-owned instructions", task)
        self.assertIn("Do not run target commands", task)
        self.assertEqual(review["schemaVersion"], "harnessforge.firstAgentReview.v1")
        self.assertEqual(review["status"], "pending")
        self.assertEqual(review["taskPath"], "docs/harness/state/first-agent-task.md")
        self.assertIn("freshSession", review)
        self.assertIn("evidenceRefs", review["verification"])
        self.assertTrue(any("REVIEW REQUIRED" in item for item in review["remainingReview"]))
        self.assertNotIn("Antigravity", task)
        self.assertNotIn("AGY", task)
        self.assertIn("name: harness", skill)
        self.assertIn("Zero-Install Rule", skill)
        self.assertIn("HarnessForge CLI and the HarnessForge GitHub Action are optional", skill)
        self.assertIn("references/repo-harness.md", skill)
        self.assertIn("trigger contract", skill)
        self.assertIn("pressure", skill)
        self.assertIn(
            "../../../docs/harness/feedback/verification-matrix.md",
            skill_reference,
        )
        self.assertIn("../../../docs/harness/evidence/evidence-log.md", skill_reference)
        self.assertIn("https://agentskills.io/specification.md", skill_reference)
        self.assertIn(
            "https://github.com/anthropics/skills/tree/main/skills/skill-creator",
            skill_reference,
        )
        self.assertIn("repo-owned commands", skill)

    def test_generated_harness_skill_matches_agent_skills_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            skill_path = root / ".agents/skills/harness/SKILL.md"
            reference_path = (
                root / ".agents/skills/harness/references/repo-harness.md"
            )
            skill = skill_path.read_text(encoding="utf-8")
            skill_reference = reference_path.read_text(encoding="utf-8")

        lines = skill.splitlines()
        self.assertEqual(lines[0], "---")
        frontmatter_end = lines.index("---", 1)
        frontmatter = {}
        for line in lines[1:frontmatter_end]:
            key, value = line.split(":", maxsplit=1)
            frontmatter[key.strip()] = value.strip()

        name = frontmatter["name"]
        description = frontmatter["description"]
        self.assertEqual(name, skill_path.parent.name)
        self.assertRegex(name, r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
        self.assertNotIn("--", name)
        self.assertGreaterEqual(len(description), 1)
        self.assertLessEqual(len(description), 1024)
        self.assertIn("first-agent review", description)
        self.assertIn("repo-local harness skill", description)
        self.assertLess(len(lines), 500)

        expected_refs = ("references/repo-harness.md",)
        for ref in expected_refs:
            self.assertIn(f"`{ref}`", skill)

        root_relative_refs = (
            "AGENTS.md",
            "feature_list.json",
            "current-state.md",
            "docs/harness/README.md",
            "docs/harness/authoritative-facts.md",
            "docs/harness/feedback/verification-matrix.md",
            "docs/harness/evidence/evidence-log.md",
        )
        for ref in root_relative_refs:
            self.assertNotRegex(skill, rf"`{re.escape(ref)}`")

        self.assertIn("../../../AGENTS.md", skill_reference)
        self.assertIn("../../../feature_list.json", skill_reference)
        self.assertIn("../../../current-state.md", skill_reference)
        self.assertIn("../../../docs/harness/README.md", skill_reference)
        self.assertIn("../../../docs/harness/authoritative-facts.md", skill_reference)
        self.assertIn(
            "../../../docs/harness/feedback/verification-matrix.md",
            skill_reference,
        )
        self.assertIn("../../../docs/harness/evidence/evidence-log.md", skill_reference)

    def test_generated_roadmap_tracks_harness_work_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            roadmap = (root / "docs/harness/state/roadmap.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("docs/harness/state/roadmap.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/state/roadmap.md", manifest["reviewRequired"])
        self.assertEqual(
            manifest["generatedFiles"]["docs/harness/state/roadmap.md"]["ownership"],
            "generated",
        )
        self.assertIn("# Harness Roadmap", roadmap)
        self.assertIn("REVIEW REQUIRED", roadmap)
        self.assertIn("Source And Evidence Weighting", roadmap)
        self.assertIn("Smallest Correct Work Gate", roadmap)
        self.assertIn("standard library", roadmap)
        self.assertIn("native platform feature", roadmap)
        self.assertIn("Task Buckets", roadmap)
        self.assertIn("Status Lifecycle", roadmap)
        self.assertIn("Surface Impact Checklist", roadmap)
        self.assertIn("Fresh-Session Test", roadmap)
        self.assertIn("Instruction Rule Lifecycle", roadmap)
        self.assertIn("Completion Evidence Ladder", roadmap)
        self.assertIn("Generated or owned harness files", roadmap)
        self.assertIn("CI or hosted automation", roadmap)
        self.assertIn("Roadmap Items", roadmap)
        self.assertIn("Surfaces In Scope", roadmap)
        self.assertIn("Execution Gate", roadmap)
        self.assertIn("Technical Debt And Drift", roadmap)
        self.assertIn("Failure-Mode Map", roadmap)
        self.assertIn("source-of-truth locale", roadmap)
        self.assertIn("agent-oriented", roadmap)
        self.assertIn("current-state.md", roadmap)

    def test_generated_quality_docs_track_clean_state_and_evidence_layers(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            quality = (root / "docs/harness/feedback/quality-document.md").read_text(
                encoding="utf-8"
            )
            rubric = (root / "docs/harness/feedback/evaluator-rubric.md").read_text(
                encoding="utf-8"
            )
            contract = (root / "docs/harness/boundaries/change-contract.md").read_text(
                encoding="utf-8"
            )
            operating = (
                root / "docs/harness/operations/agent-operating-model.md"
            ).read_text(encoding="utf-8")
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("docs/harness/feedback/quality-document.md", manifest["requiredFiles"])
        self.assertIn("docs/harness/feedback/quality-document.md", manifest["reviewRequired"])
        self.assertIn("Harness Subsystem Health", quality)
        self.assertIn("Instructions", quality)
        self.assertIn("Tools", quality)
        self.assertIn("Environment", quality)
        self.assertIn("State", quality)
        self.assertIn("Feedback", quality)
        self.assertIn("verification commands", quality)
        self.assertIn("Clean-State Dimensions", quality)
        self.assertIn("Benchmark Or Task Evidence", quality)
        self.assertIn("Complexity and scope stayed minimal", quality)
        self.assertIn("Standard startup path still works", quality)
        self.assertIn("Structural scores alone are not enough", quality)
        self.assertIn("static checks", rubric)
        self.assertIn("runtime/startup checks", rubric)
        self.assertIn("system or user-flow checks", rubric)
        self.assertIn("unnecessary abstractions", rubric)
        self.assertIn("drive-by refactors", rubric)
        self.assertIn("Build Necessity Gate", contract)
        self.assertIn("standard library", contract)
        self.assertIn("intentional simplification", contract)
        self.assertIn("Smallest Correct Change", operating)
        self.assertIn("existing dependencies before new code", operating)

    def test_generated_source_record_schema_guides_project_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root)
            schema = json.loads(
                (root / "docs/harness/research/source-record.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            example = json.loads(
                (root / "docs/harness/research/source-record-example.json").read_text(
                    encoding="utf-8"
                )
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn(
            "docs/harness/research/source-record.schema.json",
            manifest["requiredFiles"],
        )
        self.assertIn(
            "docs/harness/research/source-record-example.json",
            manifest["requiredFiles"],
        )
        self.assertIn(
            "docs/harness/research/source-record-example.json",
            manifest["reviewRequired"],
        )
        self.assertEqual(schema["title"], "HarnessForge Project Source Record")
        schema_text = json.dumps(schema)
        self.assertIn("targetRelativePath", schema_text)
        self.assertIn("machine-local absolute paths", schema_text)
        self.assertIn("project-owned records", schema_text)
        self.assertFalse((root / "docs/harness/research/research-sources.json").exists())
        self.assertEqual(example["id"], "source-record-example")
        self.assertEqual(example["reviewStatus"], "REVIEW REQUIRED")
        self.assertEqual(
            example["source"]["targetRelativePath"],
            "docs/architecture.md",
        )
        self.assertIn("REVIEW REQUIRED", json.dumps(example))

    def test_audit_penalizes_old_generated_harness_quality_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("python -m compileall .",))
            for relative_path in (
                "docs/harness/state/first-agent-task.md",
                "docs/harness/state/roadmap.md",
                "docs/harness/feedback/sensor-registry.md",
            ):
                (root / relative_path).unlink()
            manifest_path = root / "docs/harness/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop("platformContract", None)
            manifest.pop("supportedPlatforms", None)
            manifest.pop("generatedFiles", None)
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            result = audit_target(root)
            checks = {
                check.message: check.passed
                for domain in result.domains
                for check in domain.checks
            }

        self.assertLess(result.overall, 100)
        self.assertFalse(checks["Platform contract metadata is present"])
        self.assertFalse(checks["Generated-file ownership metadata is present"])
        self.assertFalse(checks["Sensor registry exists"])
        self.assertFalse(checks["First-agent harness improvement task exists"])
        self.assertFalse(checks["Harness roadmap exists"])

    def test_audit_flags_generated_target_repo_local_self_healing_leak(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("python -m compileall .",))
            leaked = root / "docs/harness/operations/self-healing.md"
            leaked.write_text("# Self-Healing Harness Loop\n", encoding="utf-8")
            manifest_path = root / "docs/harness/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["requiredFiles"].append("docs/harness/operations/self-healing.md")
            manifest["requiredHarnessSnippets"][
                "docs/harness/operations/self-healing.md"
            ] = ["Self-Healing Harness Loop", "with-self-heal-workflow"]
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            result = audit_target(root)
            scope = next(domain for domain in result.domains if domain.name == "scope")
            boundary = next(
                check
                for check in scope.checks
                if check.message
                == "Generated target harness excludes HarnessForge repo-local self-healing"
            )

        self.assertLess(result.overall, 100)
        self.assertFalse(boundary.passed)
        self.assertIn("docs/harness/operations/self-healing.md", boundary.detail)

    def test_audit_rejects_flat_top_level_harness_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("python -m compileall .",))
            (root / "docs/harness/stray.md").write_text(
                "Flat harness docs should move into a focused subdirectory.\n",
                encoding="utf-8",
            )

            result = audit_target(root)
            scope = next(domain for domain in result.domains if domain.name == "scope")
            layout = next(
                check
                for check in scope.checks
                if check.message == "Harness docs use the organized directory layout"
            )

        self.assertLess(result.overall, 100)
        self.assertFalse(layout.passed)
        self.assertIn("stray.md", layout.detail)

    def test_audit_requires_harnessforge_product_fact_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_harness(root, commands=("python -m compileall .",))
            for relative_path in (
                "action.yml",
                "docs/action.md",
                "src/harnessforge/cli.py",
            ):
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("placeholder\n", encoding="utf-8")
            manifest_path = root / "docs/harness/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["requiredFiles"].extend(
                ["action.yml", "docs/action.md", "src/harnessforge/cli.py"]
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            facts_path = root / "docs/harness/authoritative-facts.md"
            facts_path.unlink()

            missing = audit_target(root)
            facts_path.write_text(
                "# Authoritative Facts And Docs Routing\n\n"
                "## Boundary Types Covered\n\n"
                "## Fact Owners\n\n"
                "## Change-To-Docs Routing\n\n"
                "## Fan-Out Budgets\n",
                encoding="utf-8",
            )
            present = audit_target(root)

        missing_scope = next(domain for domain in missing.domains if domain.name == "scope")
        present_scope = next(domain for domain in present.domains if domain.name == "scope")
        self.assertFalse(
            next(
                check
                for check in missing_scope.checks
                if check.message == "HarnessForge docs routing map exists"
            ).passed
        )
        self.assertTrue(
            next(
                check
                for check in present_scope.checks
                if check.message == "HarnessForge docs routing map exists"
            ).passed
        )

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
        self.assertIn("Implementation discipline", agents)
        self.assertIn("standard library", agents)
        self.assertIn("intentional simplifications", agents)
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
        self.assertIn("docs/harness/boundaries/component-inventory.md", agents)

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
            "docs/harness/feedback/verification-matrix.md",
            "docs/harness/boundaries/security-boundary-map.md",
            "docs/harness/release/release-controls.md",
            "docs/harness/state/first-agent-task.md",
            "docs/harness/operations/agent-operating-model.md",
            "docs/harness/state/entropy-control.md",
            "docs/harness/feedback/sensor-registry.md",
            "docs/harness/research/source-record.schema.json",
            "docs/harness/research/source-record-example.json",
        }
        live_snippets = live["requiredHarnessSnippets"]
        for file_name in sorted(shared_controls):
            snippets = generated["requiredHarnessSnippets"][file_name]
            live_values = live_snippets.get(file_name)
            with self.subTest(file_name=file_name):
                self.assertEqual(live_values, snippets)

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
            inventory = (root / "docs/harness/boundaries/component-inventory.md").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )

        self.assertIn("## Detected Workspace Markers", inventory)
        self.assertIn("## Effective Agent Boundary", inventory)
        self.assertIn("shell and file tools", inventory)
        self.assertIn("changes the effective agent", inventory)
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
            (root / "current-state.md").unlink()

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
