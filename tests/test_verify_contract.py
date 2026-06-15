from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class VerifyContractTests(unittest.TestCase):
    def test_verify_contract_doc_records_no_execute_default(self) -> None:
        contract = (
            REPO_ROOT / "docs" / "harness" / "verify-json-contract.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Default mode: plan", contract)
        self.assertIn("MUST NOT run target repository commands", contract)
        self.assertIn("explicit run mode", contract)

    def test_verify_schema_and_example_define_stable_contract(self) -> None:
        schema = json.loads(
            (
                REPO_ROOT / "docs" / "harness" / "verify-json.schema.json"
            ).read_text(encoding="utf-8")
        )
        example = json.loads(
            (
                REPO_ROOT / "docs" / "harness" / "verify-json-example.json"
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


if __name__ == "__main__":
    unittest.main()
