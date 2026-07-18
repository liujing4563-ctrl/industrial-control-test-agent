from industrial_test_agent.agents.base import SpecialistAgent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent


class PLCSpecialistService(SpecialistAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        return ActionIntent(
            intent_id="plc-001",
            case_id=case_state.case_id,
            action_type="plc_diagnosis",
            action_details={"domain": "plc_io"},
            reason="analyze plc evidence",
            requested_by="plc_specialist",
        )
