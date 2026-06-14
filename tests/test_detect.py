from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from repo_harness_creator.detect import detect_project


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


if __name__ == "__main__":
    unittest.main()
