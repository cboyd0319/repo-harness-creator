from __future__ import annotations

import unittest

from harnessforge.maturity import build_maturity_report


def _base_report() -> dict[str, object]:
    return {
        "audit": {"overall": 100},
        "instructionQuality": {"summary": {"status": "strong"}},
        "firstAgentTask": {"lifecycle": {"status": "completed"}},
        "readiness": {
            "verdict": "ready",
            "reviewRequiredCount": 0,
        },
        "verifyEvidence": {
            "latest": {
                "mode": "run",
                "verdict": "passed",
                "issues": [],
                "summary": {
                    "blocked": 0,
                    "failed": 0,
                    "timedOut": 0,
                    "errors": 0,
                },
            }
        },
        "drift": {"summary": {"actionable": 0}},
        "docsFanout": {"contract": {"verdict": "not_required"}},
        "releaseControls": {"present": True},
        "effectiveness": {"verdict": "blocked"},
    }


class MaturityTests(unittest.TestCase):
    def test_maturity_is_release_ready_without_optional_effectiveness(self) -> None:
        payload = build_maturity_report(_base_report())

        self.assertEqual(payload["schemaVersion"], "harnessforge.maturity.v1")
        self.assertEqual(payload["currentLevel"], "release-ready")
        self.assertEqual(payload["nextLevel"], "measured")
        self.assertEqual(
            payload["blockedRequirements"][0]["id"],
            "effectiveness-evidence-reviewable",
        )

    def test_maturity_reaches_measured_with_reviewable_effectiveness(self) -> None:
        report = _base_report()
        report["effectiveness"] = {"verdict": "reviewable"}

        payload = build_maturity_report(report)

        self.assertEqual(payload["currentLevel"], "measured")
        self.assertIsNone(payload["nextLevel"])
        self.assertEqual(payload["blockedRequirements"], [])

    def test_maturity_is_cumulative_not_best_effort(self) -> None:
        report = _base_report()
        report["firstAgentTask"] = {"lifecycle": {"status": "pending"}}
        report["readiness"] = {
            "verdict": "ready",
            "reviewRequiredCount": 1,
        }

        payload = build_maturity_report(report)

        self.assertEqual(payload["currentLevel"], "generated")
        self.assertEqual(payload["nextLevel"], "reviewed")
        blocked = {item["id"] for item in payload["blockedRequirements"]}
        self.assertEqual(
            blocked,
            {"first-agent-review", "readiness-review-surfaces"},
        )


if __name__ == "__main__":
    unittest.main()
