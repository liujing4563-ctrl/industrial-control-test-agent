import unittest

from pydantic import ValidationError

from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.evidence import Evidence


class TestDomainModels(unittest.TestCase):
    def test_evidence_is_immutable(self):
        evidence = Evidence(
            evidence_id="ev-001",
            observation_id="obs-001",
            case_id="case-001",
            source="source",
            content_hash="hash",
        )
        with self.assertRaises(ValidationError):
            evidence.evidence_id = "ev-002"

    def test_case_state_read_write(self):
        case = CaseState(case_id="case-001", current_phase="intake")
        case.current_phase = "planning"
        self.assertEqual(case.current_phase, "planning")


if __name__ == "__main__":
    unittest.main()
