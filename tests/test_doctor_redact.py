from __future__ import annotations

import unittest
from unittest.mock import patch

from repo_harness_creator.doctor import doctor_report
from repo_harness_creator.redact import redact_local_paths


class DoctorRedactTests(unittest.TestCase):
    def test_redacts_common_home_paths(self) -> None:
        text = "/Users/alice/project C:\\Users\\Bob\\repo /home/casey/src"
        redacted = redact_local_paths(text)

        self.assertNotIn("alice", redacted)
        self.assertNotIn("Bob", redacted)
        self.assertNotIn("casey", redacted)
        self.assertEqual(redacted.count("<home>"), 3)

    def test_doctor_report_shape(self) -> None:
        report = doctor_report()

        self.assertIn("python", report)
        self.assertIn("platform", report)
        self.assertIn("ok", report)

    def test_windows_server_2025_runner_is_supported_ci_proxy(self) -> None:
        with (
            patch("repo_harness_creator.doctor.platform.system", return_value="Windows"),
            patch("repo_harness_creator.doctor.platform.release", return_value="2025"),
            patch("repo_harness_creator.doctor.platform.version", return_value="10.0.26100"),
        ):
            report = doctor_report()

        self.assertTrue(report["platform"]["ok"])


if __name__ == "__main__":
    unittest.main()
