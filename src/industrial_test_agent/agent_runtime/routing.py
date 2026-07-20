"""Routing decisions for the deterministic Agent Runtime V0 graph."""

from industrial_test_agent.agent_runtime.state import CaseGraphState


def route_after_validation(state: CaseGraphState) -> str:
    if state.get("policy_decision") == "allowed":
        return "execute_action"
    return "finalize_case"


def route_after_decision(state: CaseGraphState) -> str:
    if state.get("stage") in ("planning", "replanning"):
        return "propose_action"
    return "finalize_case"
