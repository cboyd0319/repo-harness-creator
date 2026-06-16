from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from harnessforge.core.doctor import doctor_report
from harnessforge.core.redact import redact_local_paths


class DoctorRedactTests(unittest.TestCase):
    def test_redacts_common_home_paths(self) -> None:
        text = (
            "/Users/alice/project "
            "/Users/Chad Boyd/project "
            "C:\\Users\\Bob\\repo "
            "C:\\Users\\Chad Boyd\\repo "
            "/home/casey/src"
        )
        redacted = redact_local_paths(text)

        self.assertNotIn("alice", redacted)
        self.assertNotIn("Chad Boyd", redacted)
        self.assertNotIn("Bob", redacted)
        self.assertNotIn("casey", redacted)
        self.assertEqual(redacted.count("<home>"), 5)

    def test_redacts_current_home_path(self) -> None:
        home = str(Path.home())
        if not home or home == ".":
            self.skipTest("home path unavailable")

        redacted = redact_local_paths(f"{home}/repo")

        self.assertNotIn(home, redacted)
        self.assertIn("<home>", redacted)

    def test_doctor_report_shape(self) -> None:
        report = doctor_report()

        self.assertIn("python", report)
        self.assertIn("platform", report)
        self.assertIn("ok", report)

    def test_windows_server_2025_runner_is_supported_ci_proxy(self) -> None:
        with (
            patch("harnessforge.core.doctor.platform.system", return_value="Windows"),
            patch("harnessforge.core.doctor.platform.release", return_value="2025"),
            patch("harnessforge.core.doctor.platform.version", return_value="10.0.26100"),
        ):
            report = doctor_report()

        self.assertTrue(report["platform"]["ok"])


if __name__ == "__main__":
    unittest.main()
