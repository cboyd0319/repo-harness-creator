from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_pins import check_root


class PinCheckTests(unittest.TestCase):
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
                "  - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6\n"
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


if __name__ == "__main__":
    unittest.main()
