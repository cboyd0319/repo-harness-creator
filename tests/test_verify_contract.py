from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class VerifyContractTests(unittest.TestCase):
    def test_verify_contract_doc_records_no_execute_default(self) -> None:
        contract = (
            REPO_ROOT / "docs" / "harness" / "feedback" / "verify-json-contract.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Default mode: plan", contract)
        self.assertIn("MUST NOT run target repository commands", contract)
        self.assertIn("explicit run mode", contract)

    def test_verify_schema_and_example_define_stable_contract(self) -> None:
        schema = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "feedback"
                / "verify-json.schema.json"
            ).read_text(encoding="utf-8")
        )
        example = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "feedback"
                / "verify-json-example.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(schema["$id"], "https://harnessforge.dev/schemas/verify-json.v1")
        self.assertEqual(example["schemaVersion"], "harnessforge.verify.v1")
        self.assertEqual(example["mode"], "plan")
        self.assertFalse(example["execution"]["commandsExecuted"])
        self.assertEqual(example["checks"][0]["status"], "planned")
        self.assertIsNone(example["checks"][0]["exitCode"])
        self.assertIn("planned", schema["$defs"]["checkStatus"]["enum"])
        self.assertIn("timed_out", schema["$defs"]["checkStatus"]["enum"])

    def test_effectiveness_eval_contract_records_evidence_boundaries(self) -> None:
        contract = (
            REPO_ROOT
            / "docs"
            / "harness"
            / "feedback"
            / "effectiveness-eval-contract.md"
        ).read_text(encoding="utf-8")

        self.assertIn("candidate-sensitive metric", contract)
        self.assertIn("held-out", contract)
        self.assertIn("frozen replay", contract)
        self.assertIn("worst-case quality", contract)
        self.assertIn("structural audit", contract)
        self.assertIn("permissioned state transitions", contract)
        self.assertIn("Feedback Channels", contract)
        self.assertIn("convergence rule", contract)
        self.assertIn("canonical URLs", contract)
        self.assertIn("effectiveness-evidence.schema.json", contract)
        self.assertIn("effectiveness-evidence-example.json", contract)
        self.assertIn("harnessforge effectiveness --target . --json", contract)

    def test_effectiveness_evidence_schema_and_example_define_claim_contract(
        self,
    ) -> None:
        schema = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "feedback"
                / "effectiveness-evidence.schema.json"
            ).read_text(encoding="utf-8")
        )
        example = json.loads(
            (
                REPO_ROOT
                / "docs"
                / "harness"
                / "feedback"
                / "effectiveness-evidence-example.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            schema["$id"],
            "https://harnessforge.dev/schemas/effectiveness-evidence.v1",
        )
        self.assertEqual(
            example["schemaVersion"], "harnessforge.effectivenessEvidence.v1"
        )
        for field in (
            "claim",
            "target",
            "candidate",
            "baseline",
            "evaluation",
            "metrics",
            "safety",
            "cost",
            "evidence",
            "promotion",
        ):
            self.assertIn(field, schema["required"])
            self.assertIn(field, example)
        self.assertTrue(example["evaluation"]["taskSet"]["heldOut"])
        self.assertIn(
            example["evaluation"]["replayType"],
            schema["$defs"]["replayType"]["enum"],
        )
        self.assertIn("trajectory", example["evaluation"]["feedbackChannels"])
        self.assertTrue(example["metrics"]["primary"]["candidateSensitive"])
        self.assertIn("worstCase", example["metrics"])
        self.assertFalse(example["promotion"]["humanApproved"])


if __name__ == "__main__":
    unittest.main()
