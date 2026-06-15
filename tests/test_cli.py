from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from harnessforge.cli import main


class CliTests(unittest.TestCase):
    def test_help_returns_zero(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["--help"])

        self.assertEqual(code, 0)
        self.assertIn("harnessforge", stdout.getvalue())

    def test_missing_subcommand_returns_usage_error(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([])

        self.assertEqual(code, 2)
        self.assertIn("harnessforge", stdout.getvalue())

    def test_init_and_audit_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                init_code = main(["init", "--target", str(root)])
            with contextlib.redirect_stdout(io.StringIO()):
                audit_code = main(["audit", "--target", str(root), "--min-score", "85"])

        self.assertEqual(init_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertIn("Detected stack", stdout.getvalue())

    def test_inspect_command_reports_profile_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root)])

            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertIn("Detected stack: python", stdout.getvalue())
        self.assertIn("Verification commands:", stdout.getvalue())

    def test_inspect_json_reports_detected_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Cargo.toml").write_text(
                "[workspace]\nmembers = ['crates/*']\n",
                encoding="utf-8",
            )
            (root / "justfile").write_text(
                "ci:\n\tcargo test --workspace\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["detectedStack"], "rust")
        self.assertIn("just", payload["packageManagers"])
        self.assertIn("just ci", payload["verificationCommands"])
        self.assertIn("justfile", payload["routingMarkers"])

    def test_inspect_readiness_json_reports_ready_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text(
                "import unittest\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    ["inspect", "--target", str(root), "--readiness", "--json"]
                )

            payload = json.loads(stdout.getvalue())
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["blockedReasons"], [])
        self.assertEqual(payload["warnings"], [])
        for key in (
            "nextActions",
            "sourceOfTruth",
            "runnableChecks",
            "generatedDrift",
            "reviewRequired",
            "workflowInventory",
            "workItemInventory",
            "contextBudget",
            "governanceInventory",
            "effectivenessInventory",
        ):
            self.assertIn(key, payload)
        self.assertIn("python -m unittest discover", payload["runnableChecks"])

    def test_inspect_readiness_blocks_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "blocked")
        self.assertTrue(
            any("No project verification" in item for item in payload["blockedReasons"])
        )
        self.assertTrue(any("--command" in item for item in payload["nextActions"]))

    def test_inspect_readiness_reports_context_budget_and_duplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            repeated_block = "\n".join(
                f"- Shared routing rule {index}" for index in range(1, 7)
            )
            long_tail = "\n".join(f"- Extra local rule {index}" for index in range(320))
            (root / "AGENTS.md").write_text(
                "# Existing\n\n" + repeated_block + "\n" + long_tail + "\n",
                encoding="utf-8",
            )
            (root / "CLAUDE.md").write_text(
                "# Claude\n\n" + repeated_block + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        context = payload["contextBudget"]
        files = {item["path"]: item for item in context["instructionFiles"]}
        self.assertGreater(files["AGENTS.md"]["lineCount"], 300)
        self.assertIn("oversized", files["AGENTS.md"]["findings"])
        duplicates = context["duplicateInstructionBlocks"]
        self.assertTrue(
            any(
                item["left"] == "AGENTS.md" and item["right"] == "CLAUDE.md"
                for item in duplicates
            )
        )
        self.assertTrue(any("context budget" in item for item in payload["warnings"]))
        self.assertTrue(any("duplicate instruction" in item for item in payload["warnings"]))

    def test_inspect_readiness_reports_governance_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "marketplace.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            (root / ".claude").mkdir()
            (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
            (root / ".codex").mkdir()
            (root / ".codex" / "config.toml").write_text(
                "sandbox = 'read-only'\n",
                encoding="utf-8",
            )
            (root / ".claude" / "hooks").mkdir()
            (root / ".claude" / "hooks" / "pre-tool-use.sh").write_text(
                "#!/bin/sh\n",
                encoding="utf-8",
            )
            (root / ".devcontainer").mkdir()
            (root / ".devcontainer" / "devcontainer.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            (root / ".husky").mkdir()
            (root / ".husky" / "pre-commit").write_text(
                "#!/bin/sh\n",
                encoding="utf-8",
            )
            (root / ".pre-commit-config.yaml").write_text(
                "repos: []\n",
                encoding="utf-8",
            )
            (root / ".sandbox").mkdir()
            (root / ".sandbox" / "policy.toml").write_text(
                "mode = 'deny'\n",
                encoding="utf-8",
            )
            (root / ".env.example").write_text(
                "API_TOKEN=\n",
                encoding="utf-8",
            )
            (root / ".env.local").write_text(
                "API_TOKEN=secret\n",
                encoding="utf-8",
            )
            (root / "skills" / "meta-harness").mkdir(parents=True)
            (root / "skills" / "meta-harness" / "SKILL.md").write_text(
                "---\nname: meta-harness\n---\n",
                encoding="utf-8",
            )
            (root / "install.sh").write_text(
                "#!/usr/bin/env bash\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "copilot-setup-steps.yml").write_text(
                "name: setup\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        inventory = {item["path"]: item for item in payload["governanceInventory"]}
        self.assertEqual(inventory[".mcp.json"]["category"], "mcp-config")
        self.assertIn("server-trust", inventory[".mcp.json"]["surfaces"])
        self.assertEqual(inventory[".claude/settings.json"]["category"], "agent-settings")
        self.assertEqual(inventory[".codex/config.toml"]["category"], "agent-settings")
        self.assertEqual(
            inventory[".devcontainer/devcontainer.json"]["category"],
            "devcontainer",
        )
        self.assertEqual(inventory[".sandbox/policy.toml"]["category"], "sandbox")
        self.assertEqual(inventory[".env.example"]["category"], "environment-template")
        self.assertEqual(
            inventory[".github/workflows/copilot-setup-steps.yml"]["category"],
            "agent-setup-workflow",
        )
        self.assertEqual(inventory[".claude/hooks/pre-tool-use.sh"]["category"], "hook")
        self.assertEqual(inventory[".husky/pre-commit"]["category"], "hook")
        self.assertEqual(inventory[".pre-commit-config.yaml"]["category"], "hook")
        self.assertEqual(inventory[".env.local"]["category"], "environment-local")
        self.assertEqual(
            inventory[".claude-plugin/marketplace.json"]["category"],
            "agent-plugin",
        )
        self.assertEqual(inventory["skills/meta-harness/SKILL.md"]["category"], "agent-skill")
        self.assertEqual(inventory["install.sh"]["category"], "installer-script")
        self.assertTrue(any("governance inventory" in item for item in payload["warnings"]))
        self.assertTrue(any("MCP" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("devcontainer" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("environment" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("hook" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("skill" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("plugin" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("installer" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_effectiveness_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "evals").mkdir()
            (root / "evals" / "harness-effectiveness.md").write_text(
                "# Harness Effectiveness Eval\n",
                encoding="utf-8",
            )
            (root / "benchmarks").mkdir()
            (root / "benchmarks" / "run_log.jsonl").write_text(
                "{\"agent\":\"baseline\",\"quality\":1.0,\"cost\":100}\n",
                encoding="utf-8",
            )
            (root / "score_harness.py").write_text(
                "print('score')\n",
                encoding="utf-8",
            )
            (root / "results.jsonl").write_text(
                "{\"verdict\":\"planned\"}\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        inventory = {item["path"]: item for item in payload["effectivenessInventory"]}
        self.assertEqual(
            inventory["evals/harness-effectiveness.md"]["category"], "eval-spec"
        )
        self.assertEqual(
            inventory["benchmarks/run_log.jsonl"]["category"], "result-log"
        )
        self.assertEqual(inventory["score_harness.py"]["category"], "scorer")
        self.assertEqual(inventory["results.jsonl"]["category"], "result-log")
        self.assertTrue(any("effectiveness eval" in item for item in payload["warnings"]))
        self.assertTrue(
            any("candidate-sensitive" in item for item in payload["reviewRequired"])
        )
        self.assertTrue(any("held-out" in item for item in payload["reviewRequired"]))

    def test_quickstart_guides_first_run_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / "specs" / "001-demo").mkdir(parents=True)
            (root / "specs" / "001-demo" / "spec.md").write_text(
                "# Demo Spec\n",
                encoding="utf-8",
            )
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            manifest_exists = (root / "docs" / "harness" / "manifest.json").exists()

        self.assertEqual(code, 0)
        self.assertEqual(agents, "# Existing\n\nProject-owned instructions.\n")
        self.assertFalse(manifest_exists)
        self.assertIn(f"Quickstart for {root.name}", output)
        self.assertIn("Detected stack: python", output)
        self.assertIn("Readiness: warning", output)
        self.assertIn("Source of truth:", output)
        self.assertIn("Existing files preserved:", output)
        self.assertIn("AGENTS.md", output)
        self.assertIn("Files HarnessForge would create:", output)
        self.assertIn("docs/harness/manifest.json", output)
        self.assertIn("Generated files needing project review:", output)
        self.assertIn("docs/harness/change-contract.md", output)
        self.assertIn("Review required:", output)
        self.assertIn("MCP configuration detected", output)
        self.assertIn("Next commands:", output)
        self.assertIn("harnessforge init --target <repo> --dry-run", output)
        self.assertIn("harnessforge sync --check --target <repo>", output)

    def test_quickstart_reports_blocked_missing_verification_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertIn("Readiness: blocked", output)
        self.assertIn("Blocked reasons:", output)
        self.assertIn("No project verification check detected.", output)
        self.assertIn("--command", output)

    def test_quickstart_guides_existing_harness_to_audit_and_sync(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                quickstart_code = main(["quickstart", "--target", str(root)])

            output = stdout.getvalue()

        self.assertEqual(init_code, 0)
        self.assertEqual(quickstart_code, 0)
        self.assertIn("Existing files preserved:", output)
        self.assertNotIn("harnessforge init --target <repo>", output)
        self.assertIn("harnessforge audit --target <repo> --min-score 85", output)
        self.assertIn("harnessforge sync --check --target <repo>", output)

    def test_inspect_readiness_warns_for_specs_and_governance_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / "specs" / "architecture").mkdir(parents=True)
            (root / "specs" / "work-items").mkdir(parents=True)
            (root / "specs" / "foundation.md").write_text("# Foundation\n", encoding="utf-8")
            (root / "specs" / "architecture" / "design.md").write_text(
                "# Design\n",
                encoding="utf-8",
            )
            (root / "specs" / "work-items" / "0000-template.md").write_text(
                "# Work Item\n",
                encoding="utf-8",
            )
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "copilot-setup-steps.yml").write_text(
                "name: setup\n",
                encoding="utf-8",
            )
            (root / ".mcp.json").write_text("{}\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("structured project specs", payload["sourceOfTruth"])
        self.assertTrue(any("AGENTS.md" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("MCP" in item for item in payload["reviewRequired"]))
        self.assertTrue(any("agent setup workflow" in item for item in payload["warnings"]))

    def test_inspect_readiness_reports_spec_kit_quality_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nProject-owned instructions.\n",
                encoding="utf-8",
            )
            (root / ".specify" / "memory").mkdir(parents=True)
            (root / ".specify" / "memory" / "constitution.md").write_text(
                "# Constitution\n",
                encoding="utf-8",
            )
            (root / ".specify" / "feature.json").write_text(
                json.dumps({"feature_directory": "specs/001-login"}),
                encoding="utf-8",
            )
            feature = root / "specs" / "001-login"
            (feature / "checklists").mkdir(parents=True)
            (feature / "spec.md").write_text(
                "# Feature Specification\n\n"
                "- **FR-001**: System MUST support login via "
                "[NEEDS CLARIFICATION: auth method].\n",
                encoding="utf-8",
            )
            (feature / "checklists" / "requirements.md").write_text(
                "# Checklist\n\n- [ ] CHK001 Are auth requirements clear?\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("Spec Kit project (.specify)", payload["sourceOfTruth"])
        self.assertIn("active feature specs: specs/001-login", payload["sourceOfTruth"])
        self.assertTrue(any("NEEDS CLARIFICATION" in item for item in payload["warnings"]))
        self.assertTrue(any("incomplete requirement checklist" in item for item in payload["warnings"]))
        self.assertTrue(any("missing plan.md" in item for item in payload["warnings"]))
        self.assertTrue(any("missing tasks.md" in item for item in payload["warnings"]))
        self.assertTrue(any("source-of-truth specs" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_aspec_and_workflow_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nFollow AGENTS only.\n",
                encoding="utf-8",
            )
            (root / "aspec" / "architecture").mkdir(parents=True)
            (root / "aspec" / "work-items").mkdir(parents=True)
            (root / "aspec" / "workflows").mkdir()
            (root / "aspec" / "architecture" / "system.md").write_text(
                "# Architecture\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "0000-template.md").write_text(
                "# Work Item Template\n",
                encoding="utf-8",
            )
            (root / "aspec" / "workflows" / "repair.yml").write_text(
                "steps: []\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        self.assertIn("aspec", payload["sourceOfTruth"])
        self.assertIn(
            "work-item template: aspec/work-items/0000-template.md",
            payload["sourceOfTruth"],
        )
        self.assertTrue(any("workflow definitions" in item for item in payload["warnings"]))
        self.assertTrue(any("source-of-truth specs" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_workflow_and_work_item_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text("", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                "# Existing\n\nFollow AGENTS only.\n",
                encoding="utf-8",
            )
            (root / "aspec" / "workflows").mkdir(parents=True)
            (root / "aspec" / "work-items").mkdir()
            (root / "aspec" / "workflows" / "repair.toml").write_text(
                'name = "repair"\n'
                'setup = ["make setup"]\n'
                'teardown = ["make clean"]\n'
                'remediation = ["python scripts/fix.py"]\n'
                'push = true\n'
                'credentials = ["GH_TOKEN"]\n'
                "[pull_request]\n"
                "enabled = true\n"
                "[ci]\n"
                "poll = true\n",
                encoding="utf-8",
            )
            (root / "workflows").mkdir()
            (root / "workflows" / "release.yml").write_text(
                "name: release\n"
                "on:\n"
                "  push:\n"
                "  pull_request:\n"
                "jobs:\n"
                "  release:\n"
                "    steps:\n"
                "      - run: python scripts/remediate.py\n"
                "        env:\n"
                "          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "0000-template.md").write_text(
                "# Work Item Template\n",
                encoding="utf-8",
            )
            (root / "aspec" / "work-items" / "1001-repair.md").write_text(
                "# Repair Work Item\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        workflows = {item["path"]: item for item in payload["workflowInventory"]}
        repair = workflows["aspec/workflows/repair.toml"]
        self.assertEqual(repair["format"], "toml")
        for surface in (
            "setup",
            "teardown",
            "remediation",
            "push",
            "pull-request",
            "ci-polling",
            "credentials",
        ):
            self.assertIn(surface, repair["surfaces"])
        release = workflows["workflows/release.yml"]
        self.assertEqual(release["format"], "yaml")
        self.assertIn("pull-request", release["surfaces"])
        self.assertIn("credentials", release["surfaces"])
        work_items = {item["path"]: item for item in payload["workItemInventory"]}
        self.assertEqual(
            work_items["aspec/work-items/0000-template.md"]["kind"],
            "template",
        )
        self.assertEqual(
            work_items["aspec/work-items/1001-repair.md"]["kind"],
            "work-item",
        )
        self.assertTrue(any("workflow inventory" in item for item in payload["warnings"]))
        self.assertTrue(any("credential" in item for item in payload["reviewRequired"]))

    def test_inspect_readiness_reports_generated_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text("# edited\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness", "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "warning")
        drift = {item["path"]: item for item in payload["generatedDrift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")
        self.assertTrue(any("generated drift" in item for item in payload["warnings"]))

    def test_inspect_readiness_text_reports_verdict_and_next_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--target", str(root), "--readiness"])

        self.assertEqual(code, 0)
        self.assertIn("Readiness: blocked", stdout.getvalue())
        self.assertIn("Next actions:", stdout.getvalue())

    def test_sync_check_json_reports_ready_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "tests").mkdir()
            (root / "tests" / "test_demo.py").write_text(
                "import unittest\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            agents_exists = (root / "AGENTS.md").exists()

        self.assertEqual(code, 0)
        self.assertFalse(agents_exists)
        self.assertEqual(payload["mode"], "check")
        self.assertEqual(payload["verdict"], "ready")
        self.assertEqual(payload["exitCode"], 0)
        self.assertEqual(payload["readiness"]["generatedDrift"], [])
        self.assertIn(
            "python -m unittest discover",
            payload["readiness"]["runnableChecks"],
        )

    def test_sync_check_exits_warning_for_generated_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text("# edited\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root), "--json"])

            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "warning")
        self.assertEqual(payload["exitCode"], 1)
        drift = {item["path"]: item for item in payload["readiness"]["generatedDrift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")

    def test_sync_check_exits_blocked_for_missing_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Notes\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["sync", "--check", "--target", str(root)])

        self.assertEqual(code, 2)
        self.assertIn("Sync check: blocked", stdout.getvalue())
        self.assertIn("No project verification", stdout.getvalue())

    def test_sync_requires_check_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["sync", "--target", tmp])

        self.assertEqual(code, 2)
        self.assertIn("--check", stderr.getvalue())

    def test_init_can_scaffold_optional_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--with-ci-workflow",
                        "--with-self-heal-workflow",
                    ]
                )

            ci = root / ".github/workflows/harnessforge.yml"
            self_heal = root / ".github/workflows/harness-self-heal.yml"
            ci_exists = ci.exists()
            self_heal_exists = self_heal.exists()

        self.assertEqual(code, 0)
        self.assertTrue(ci_exists)
        self.assertTrue(self_heal_exists)
        self.assertIn("Optional workflow scaffold review required", stdout.getvalue())
        self.assertIn("<reviewed-commit-sha>", stdout.getvalue())
        self.assertIn("permissions", stdout.getvalue())

    def test_init_can_generate_macos_only_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "init",
                        "--target",
                        str(root),
                        "--platform-contract",
                        "macos-only",
                    ]
                )

            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            init_sh_exists = (root / "init.sh").exists()
            init_ps1_exists = (root / "init.ps1").exists()

        self.assertEqual(code, 0)
        self.assertTrue(init_sh_exists)
        self.assertFalse(init_ps1_exists)
        self.assertIn("macosOnly", manifest["supportedPlatforms"])
        self.assertNotIn("init.ps1", manifest["requiredFiles"])

    def test_init_records_platform_source_review_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["init", "--target", str(root)])

            manifest = json.loads(
                (root / "docs/harness/manifest.json").read_text(encoding="utf-8")
            )
            change_contract = (
                root / "docs/harness/change-contract.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        review = manifest["platformSourceReview"]
        self.assertEqual(review["lastReviewed"], "2026-06-15")
        self.assertTrue(review["reviewRequiredBeforePlatformChange"])
        source_ids = {source["id"] for source in review["sources"]}
        self.assertIn("python-devguide-versions", source_ids)
        self.assertIn("github-actions-hosted-runners", source_ids)
        self.assertIn("github-runner-images-windows-vs2026", source_ids)
        self.assertIn("current primary-source evidence", change_contract)
        self.assertIn("runner labels", change_contract)

    def test_update_drift_report_detects_modified_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "AGENTS.md").write_text(
                "# edited\n\nlocal change\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                report_code = main(
                    [
                        "update",
                        "--target",
                        str(root),
                        "--drift-report",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            claude_text = (root / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(init_code, 0)
        self.assertEqual(report_code, 0)
        drift = {item["path"]: item for item in payload["drift"]}
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "modified")
        self.assertEqual(drift["AGENTS.md"]["ownership"], "generated")
        self.assertFalse(claude_text.startswith("# edited"))

    def test_init_records_existing_files_as_project_owned_without_initial_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                "# Existing\n\nKeep local instructions.\n",
                encoding="utf-8",
            )
            init_stdout = io.StringIO()
            with contextlib.redirect_stdout(init_stdout):
                init_code = main(["init", "--target", str(root)])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                report_code = main(
                    [
                        "update",
                        "--target",
                        str(root),
                        "--drift-report",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())

        self.assertEqual(init_code, 0)
        self.assertEqual(report_code, 0)
        self.assertIn("Existing files preserved", init_stdout.getvalue())
        self.assertIn("HARNESSFORGE_AGENTS.md", init_stdout.getvalue())
        drift = {item["path"]: item for item in payload["drift"]}
        self.assertEqual(drift["AGENTS.md"]["ownership"], "project")
        self.assertEqual(drift["AGENTS.md"]["fileStatus"], "unchanged")

    def test_init_can_enhance_existing_instruction_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "[project]\nname='demo'\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "# Existing\n\nKeep local instructions.\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                init_code = main(
                    ["init", "--target", str(root), "--enhance-existing"]
                )
            with contextlib.redirect_stdout(io.StringIO()):
                audit_code = main(
                    ["audit", "--target", str(root), "--min-score", "100"]
                )
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual(init_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertIn("ENHANCED AGENTS.md", stdout.getvalue())
        self.assertIn("Keep local instructions.", agents)
        self.assertIn("HarnessForge Quality Addendum", agents)

    def test_audit_requires_explicit_override_for_local_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                init_code = main(["init", "--target", str(root)])
            (root / "README.md").write_text(
                "Local checkout was /Users/person/private/repo\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                strict_code = main(
                    ["audit", "--target", str(root), "--min-score", "100"]
                )
            with contextlib.redirect_stdout(io.StringIO()):
                allowed_code = main(
                    [
                        "audit",
                        "--target",
                        str(root),
                        "--min-score",
                        "85",
                        "--allow-local-absolute-paths",
                    ]
                )

        self.assertEqual(init_code, 0)
        self.assertEqual(strict_code, 1)
        self.assertEqual(allowed_code, 0)
        self.assertIn("Durable harness text avoids local absolute paths", stdout.getvalue())

    def test_update_without_apply_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["update", "--target", str(root)])

            self.assertEqual(code, 0)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertIn("No files changed", stdout.getvalue())

    def test_init_rejects_unsafe_agent_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(["init", "--target", tmp, "--agent-file", "../AGENTS.md"])

        self.assertEqual(code, 2)
        self.assertIn("--agent-file", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
