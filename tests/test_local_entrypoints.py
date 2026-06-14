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
