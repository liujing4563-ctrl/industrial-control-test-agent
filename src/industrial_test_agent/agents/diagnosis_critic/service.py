from industrial_test_agent.agents.base import CriticAgent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent


class DiagnosisCriticService(CriticAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        return ActionIntent(
            intent_id="critic-001",
            case_id=case_state.case_id,
            action_type="critique",
            action_details={"review": True},
            reason="review evidence and proposals",
            requested_by="diagnosis_critic",
        )
