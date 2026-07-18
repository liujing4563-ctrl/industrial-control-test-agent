"""LangGraph nodes — minimal case execution loop."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.policy.validator import PolicyValidator, PolicyResult
from industrial_test_agent.runner.mock_runner import MockRunner
from industrial_test_agent.evidence.in_memory_store import EvidenceStore
from industrial_test_agent.domain.action_intent import ActionIntent


# ---------------------------------------------------------------------------
# Shared context (injected at graph build time)
# ---------------------------------------------------------------------------

_agent: MockAgent | None = None
_policy: PolicyValidator | None = None
_runner: MockRunner | None = None
_evidence_store: EvidenceStore | None = None

# Configurable termination criteria
_max_steps: int = 20
_required_evidence_count: int = 3


def set_runtime_context(
    agent: MockAgent,
    policy: PolicyValidator,
    runner: MockRunner,
    evidence_store: EvidenceStore,
    max_steps: int = 20,
    required_evidence_count: int = 3,
) -> None:
    global _agent, _policy, _runner, _evidence_store
    global _max_steps, _required_evidence_count
    _agent = agent
    _policy = policy
    _runner = runner
    _evidence_store = evidence_store
    _max_steps = max_steps
    _required_evidence_count = required_evidence_count


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def initialize_case(state: CaseGraphState) -> Dict[str, Any]:
    return {
        "stage": "planning",
        "remaining_steps": _max_steps,
        "evidence_ids": [],
        "hypothesis_ids": [],
        "proposed_action_id": None,
        "latest_observation_id": None,
        "termination_reason": None,
        "policy_decision": None,
    }


def propose_action(state: CaseGraphState) -> Dict[str, Any]:
    from industrial_test_agent.domain.case_state import CaseState

    case = CaseState(
        case_id=state["case_id"],
        current_phase=state["stage"],
        test_objective=state["goal"],
    )

    intent = _agent.propose(case)  # type: ignore[union-attr]
    return {
        "proposed_action_id": intent.intent_id,
        "stage": "planning",
    }


def validate_action(state: CaseGraphState) -> Dict[str, Any]:
    from industrial_test_agent.domain.case_state import CaseState

    intent = _get_current_intent(state)

    case = CaseState(
        case_id=state["case_id"],
        current_phase=state["stage"],
    )

    steps = state.get("remaining_steps", _max_steps)
    result = _policy.validate(case, intent, steps_taken=_max_steps - steps)  # type: ignore[union-attr]

    return {
        "policy_decision": result.decision,
        "stage": "validation",
    }


def execute_action(state: CaseGraphState) -> Dict[str, Any]:
    intent = _get_current_intent(state)

    obs = _runner.execute(intent)  # type: ignore[union-attr]
    evidence = _evidence_store.append_from_observation(obs)  # type: ignore[union-attr]

    new_evidence_ids = list(state.get("evidence_ids", []))
    new_evidence_ids.append(evidence.evidence_id)

    return {
        "latest_observation_id": obs.observation_id,
        "evidence_ids": new_evidence_ids,
        "remaining_steps": state.get("remaining_steps", 20) - 1,
        "stage": "execution",
    }


def record_observation(state: CaseGraphState) -> Dict[str, Any]:
    return {
        "stage": "diagnosis",
    }


def decide_next(state: CaseGraphState) -> Dict[str, Any]:
    """Decide next phase based on evidence sufficiency, budget, and policy."""
    remaining = state.get("remaining_steps", 0)
    decision = state.get("policy_decision", "")
    evidence_count = len(state.get("evidence_ids", []))

    # Hard stop: policy rejection
    if decision == "rejected":
        return {
            "stage": "rejected",
            "termination_reason": "Policy rejected: action not allowed",
        }

    # Hard stop: budget exhausted
    if remaining <= 0:
        return {
            "stage": "escalated",
            "termination_reason": f"Step budget exhausted ({evidence_count} evidence collected)",
        }

    # Success: sufficient evidence collected
    if evidence_count >= _required_evidence_count:
        return {
            "stage": "completed",
            "termination_reason": f"Case completed — {evidence_count} evidence records collected (threshold={_required_evidence_count})",
        }

    # Continue collecting evidence
    return {
        "stage": "planning",
    }


def finalize_case(state: CaseGraphState) -> Dict[str, Any]:
    if state.get("stage") not in ("completed", "escalated", "rejected"):
        return {}
    return {}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_after_validation(state: CaseGraphState) -> str:
    decision = state.get("policy_decision", "")
    if decision == "allowed":
        return "execute_action"
    if decision == "approval_required":
        return "finalize_case"  # simplified: pause for human
    return "finalize_case"  # rejected → stop


def route_after_decision(state: CaseGraphState) -> str:
    stage = state.get("stage", "")
    if stage == "planning":
        return "propose_action"
    if stage in ("completed", "escalated", "rejected"):
        return "finalize_case"
    return "finalize_case"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_current_intent(state: CaseGraphState) -> ActionIntent:
    """Rebuild ActionIntent from what mock agent would propose (deterministic)."""
    from industrial_test_agent.domain.case_state import CaseState

    case = CaseState(
        case_id=state["case_id"],
        current_phase=state["stage"],
    )
    return _agent.propose(case)  # type: ignore[union-attr]
