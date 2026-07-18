import json
import unittest

from pydantic import BaseModel

from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation


class TestSchemaContracts(unittest.TestCase):
    def test_case_state_model(self):
        case = CaseState(case_id="case-001", current_phase="intake")
        self.assertEqual(case.case_id, "case-001")

    def test_action_intent_model(self):
        intent = ActionIntent(
            intent_id="intent-001",
            case_id="case-001",
            action_type="probe",
            action_details={"command": "read"},
            reason="test",
            requested_by="agent"
        )
        self.assertEqual(intent.status, "draft")

    def test_observation_model(self):
        obs = Observation(
            observation_id="obs-001",
            case_id="case-001",
            source="mock_runner",
            source_type="mcp",
            payload={"result": "ok"},
            schema_id="observation"
        )
        self.assertEqual(obs.source, "mock_runner")

    def test_load_schema_files(self):
        for path in [
            "schemas/case-state.schema.json",
            "schemas/action-intent.schema.json",
            "schemas/observation.schema.json",
            "schemas/evidence.schema.json",
            "schemas/hypothesis.schema.json",
            "schemas/finding.schema.json",
            "schemas/capability-pack.schema.json",
            "schemas/tool-capability.schema.json",
        ]:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                self.assertIn("$schema", data)
                self.assertIn("title", data)


if __name__ == "__main__":
    unittest.main()
