from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harnessforge.evidence.feature_state import analyze_feature_state
from harnessforge.project.planner import DiffPlanReport


class FeatureStateTests(unittest.TestCase):
    def test_state_files_count_as_docs_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "feature_list.json").write_text(
                json.dumps(
                    {
                        "rules": {
                            "single_active_feature": True,
                            "passing_requires_evidence": True,
                        },
                        "features": [
                            {
                                "id": "cli-core",
                                "area": "cli",
                                "title": "CLI",
                                "status": "active",
                                "user_visible_behavior": "CLI behavior changes.",
                                "verification": ["focused CLI test"],
                                "evidence": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            diff_plan = DiffPlanReport(
                target="demo",
                base="HEAD",
                changed_files=("feature_list.json", "current-state.md"),
                checks=(),
                blocked_reasons=(),
                warnings=(),
            )

            report = analyze_feature_state(root, diff_plan=diff_plan)

        self.assertEqual(report.status, "aligned")
        self.assertEqual(report.scope_drift["touchedAreas"], ["docs"])
        self.assertEqual(report.scope_drift["unexpectedAreas"], [])

    def test_verified_completion_rate_is_advisory_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "feature_list.json").write_text(
                json.dumps(
                    {
                        "rules": {"passing_requires_evidence": True},
                        "features": [
                            {
                                "id": "done",
                                "area": "cli",
                                "title": "Done",
                                "status": "passing",
                                "user_visible_behavior": "Behavior.",
                                "verification": ["test"],
                                "evidence": ["2026-06-24: passed"],
                            },
                            {
                                "id": "wip",
                                "area": "cli",
                                "title": "WIP",
                                "status": "active",
                                "user_visible_behavior": "Behavior.",
                                "verification": ["test"],
                                "evidence": [],
                            },
                            {
                                "id": "later",
                                "area": "cli",
                                "title": "Later",
                                "status": "not_started",
                                "user_visible_behavior": "Behavior.",
                                "verification": ["test"],
                                "evidence": [],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = analyze_feature_state(root)

        # Activated = passing + active (not_started excluded); verified = passing
        # with evidence. 1 verified / 2 activated = 0.5.
        self.assertEqual(report.summary["activatedCount"], 2)
        self.assertEqual(report.summary["verifiedCount"], 1)
        self.assertEqual(report.summary["verifiedCompletionRate"], 0.5)


if __name__ == "__main__":
    unittest.main()
