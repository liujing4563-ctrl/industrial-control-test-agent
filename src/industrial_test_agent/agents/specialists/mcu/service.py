from industrial_test_agent.agents.base import SpecialistAgent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent


class MCUSpecialistService(SpecialistAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        return ActionIntent(
            intent_id="mcu-001",
            case_id=case_state.case_id,
            action_type="mcu_diagnosis",
            action_details={"domain": "mcu"},
            reason="analyze mcu evidence",
            requested_by="mcu_specialist",
        )
