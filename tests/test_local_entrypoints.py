from __future__ import annotations

import unittest
from pathlib import Path


class LocalEntrypointTests(unittest.TestCase):
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
