"""Deterministic nodes for the Agent Runtime V0 execution loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.policy.validator import PolicyValidator
from industrial_test_agent.runner.mock_runner import MockRunner
from industrial_test_agent.evidence.in_memory_store import EvidenceStore
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation


@dataclass(frozen=True)
class RuntimeContext:
    agent: MockAgent
    policy: PolicyValidator
    runner: MockRunner
    evidence_store: EvidenceStore
    max_steps: int
    required_evidence_count: int


def initialize_case(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    return {
        "stage": "planning",
        "remaining_steps": context.max_steps,
        "evidence_ids": [],
        "hypothesis_ids": [],
        "proposed_action_id": None,
        "proposed_action": None,
        "latest_observation_id": None,
        "latest_observation": None,
        "last_execution_success": None,
        "replan_count": 0,
        "termination_reason": None,
        "policy_decision": None,
        "policy_reason": None,
    }


def propose_action(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    from industrial_test_agent.domain.case_state import CaseState

    case = CaseState(
        case_id=state["case_id"],
        current_phase=state["stage"],
        test_objective=state["goal"],
    )

    intent = context.agent.propose(case)
    return {
        "proposed_action_id": intent.intent_id,
        "proposed_action": intent.model_dump(mode="json"),
        "latest_observation_id": None,
        "latest_observation": None,
        "last_execution_success": None,
        "stage": "planning",
    }


def validate_action(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    from industrial_test_agent.domain.case_state import CaseState

    intent = _get_current_intent(state)

    case = CaseState(
        case_id=state["case_id"],
        current_phase=state["stage"],
    )

    remaining_steps = state.get("remaining_steps", context.max_steps)
    result = context.policy.validate(
        case,
        intent,
        steps_taken=context.max_steps - remaining_steps,
        remaining_call_budget=remaining_steps,
    )

    return {
        "policy_decision": result.decision,
        "policy_reason": result.reason,
        "stage": "validation",
    }


def execute_action(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    intent = _get_current_intent(state)

    observation = context.runner.execute(intent)

    return {
        "latest_observation_id": observation.observation_id,
        "latest_observation": observation.model_dump(mode="json"),
        "last_execution_success": bool(observation.payload.get("success", False)),
        "remaining_steps": max(state.get("remaining_steps", 0) - 1, 0),
        "stage": "execution",
    }


def record_observation(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    observation = _get_latest_observation(state)
    evidence = context.evidence_store.append_from_observation(observation)
    evidence_ids = [*state.get("evidence_ids", []), evidence.evidence_id]

    return {
        "evidence_ids": evidence_ids,
        "stage": "diagnosis",
    }


def decide_next(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    """Decide next phase based on evidence sufficiency, budget, and policy."""
    remaining = state.get("remaining_steps", 0)
    evidence_count = len(state.get("evidence_ids", []))
    execution_succeeded = state.get("last_execution_success") is True

    if not execution_succeeded:
        if remaining <= 0:
            return {
                "stage": "escalated",
                "termination_reason": (
                    f"Call budget exhausted after runner failure "
                    f"({evidence_count} evidence collected)"
                ),
            }
        return {
            "stage": "replanning",
            "replan_count": state.get("replan_count", 0) + 1,
            "termination_reason": None,
        }

    if evidence_count >= context.required_evidence_count:
        record_label = "record" if evidence_count == 1 else "records"
        return {
            "stage": "completed",
            "termination_reason": (
                f"Case completed - {evidence_count} evidence {record_label} collected "
                f"(threshold={context.required_evidence_count})"
            ),
        }

    if remaining <= 0:
        return {
            "stage": "escalated",
            "termination_reason": (
                f"Call budget exhausted ({evidence_count} evidence collected)"
            ),
        }

    return {
        "stage": "planning",
    }


def finalize_case(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    if state.get("stage") not in ("completed", "escalated", "rejected"):
        return {}
    return {}


def _get_current_intent(state: CaseGraphState) -> ActionIntent:
    payload = state.get("proposed_action")
    if payload is None:
        raise RuntimeError("No ActionIntent is available in graph state")
    return ActionIntent.model_validate(payload)


def _get_latest_observation(state: CaseGraphState) -> Observation:
    payload = state.get("latest_observation")
    if payload is None:
        raise RuntimeError("No Observation is available in graph state")
    return Observation.model_validate(payload)
