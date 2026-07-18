from industrial_test_agent.agents.base import ExecutiveAgent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent


class ExecutiveService(ExecutiveAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        return ActionIntent(
            intent_id="exec-001",
            case_id=case_state.case_id,
            action_type="plan_test",
            action_details={"summary": "Executive plan placeholder"},
            reason="initialize case",
            requested_by="executive_agent",
        )
