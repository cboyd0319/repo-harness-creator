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


if __name__ == "__main__":
    unittest.main()
