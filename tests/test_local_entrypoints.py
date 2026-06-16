from __future__ import annotations

import unittest
from pathlib import Path


class LocalEntrypointTests(unittest.TestCase):
    def test_repo_and_generated_scripts_have_purpose_headers(self) -> None:
        root = Path(__file__).resolve().parents[1]
        paths = [
            root / "init.sh",
            root / "init.ps1",
            *sorted((root / "scripts").glob("*.py")),
        ]
        template_root = root / "src/harnessforge/templates"
        for pattern in ("*.py.tmpl", "*.ps1.tmpl", "*.sh.tmpl"):
            paths.extend(sorted(template_root.glob(pattern)))

        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path.relative_to(root).as_posix()):
                header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:6])
                self.assertIn("Purpose:", header)

    def test_gitignore_covers_local_cache_build_and_scratch_outputs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        gitignore = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
        patterns = set(gitignore)

        for pattern in (
            ".DS_Store",
            "__pycache__/",
            "*.py[cod]",
            ".pytest_cache/",
            ".ruff_cache/",
            ".mypy_cache/",
            ".venv/",
            "node_modules/",
            "build/",
            "dist/",
            "*.whl",
            ".harnessforge/",
            "htmlcov/",
            "coverage/",
            ".coverage",
            "coverage.xml",
            "*.json.tmp",
            "harness-report.*",
            "harness-action-report.*",
            "!.env.example",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, patterns)

    def test_posix_entrypoint_prepends_src_to_existing_pythonpath(self) -> None:
        root = Path(__file__).resolve().parents[1]
        init_sh = (root / "init.sh").read_text(encoding="utf-8")

        self.assertIn(
            'export PYTHONPATH="src${PYTHONPATH:+:${PYTHONPATH}}"',
            init_sh,
        )
        self.assertNotIn('export PYTHONPATH="${PYTHONPATH:-src}"', init_sh)

    def test_root_entrypoints_compile_scripts_as_product_code(self) -> None:
        root = Path(__file__).resolve().parents[1]
        init_sh = (root / "init.sh").read_text(encoding="utf-8")
        init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")

        self.assertIn("-m compileall scripts src tests", init_sh)
        self.assertIn("-m compileall scripts src tests", init_ps1)

    def test_root_entrypoints_check_research_source_ledgers(self) -> None:
        root = Path(__file__).resolve().parents[1]
        init_sh = (root / "init.sh").read_text(encoding="utf-8")
        init_ps1 = (root / "init.ps1").read_text(encoding="utf-8")

        self.assertIn("scripts/refresh_research.py --root . --check", init_sh)
        self.assertIn("scripts/refresh_research.py --root . --check", init_ps1)

    def test_powershell_entrypoints_prefer_python3_before_python(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in (
            root / "init.ps1",
            root / "src/harnessforge/templates/init.ps1.tmpl",
        ):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertLess(
                    text.index("Get-Command python3"),
                    text.index("Get-Command python -ErrorAction"),
                )
