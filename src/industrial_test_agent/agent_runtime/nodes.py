"""Deterministic nodes for the Agent Runtime V0 execution loop."""

from __future__ import annotations

from dataclasses import dataclass
import re
import uuid
from typing import Any, Dict

from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import (
    Observation,
    ObservationSourceType,
    ObservationStatus,
)
from industrial_test_agent.evidence.interfaces import EvidenceStoreProtocol
from industrial_test_agent.policy.interfaces import PolicyValidatorProtocol
from industrial_test_agent.runner.interfaces import Runner


_SENSITIVE_VALUE = re.compile(
    r"(?i)\b(password|passwd|secret|token|api[_-]?key|authorization)\b"
    r"(\s*[:=]\s*)([^\n,;]+)"
)
_LOCAL_PATH = re.compile(
    r"(?:(?:/Users|/home)/[^\s,;]+|[A-Za-z]:\\Users\\[^\s,;]+)"
)


@dataclass(frozen=True)
class RuntimeContext:
    agent: MockAgent
    policy: PolicyValidatorProtocol
    runner: Runner
    evidence_store: EvidenceStoreProtocol
    max_steps: int
    required_evidence_count: int


def initialize_case(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    return {
        "stage": "planning",
        "remaining_steps": context.max_steps,
        "action_ids": [],
        "observation_ids": [],
        "evidence_ids": [],
        "hypotheses": [],
        "findings": [],
        "active_action": None,
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
    intent = context.agent.propose(state)
    action_ids = list(state.action_ids)
    if intent.action_id not in action_ids:
        action_ids.append(intent.action_id)
    return {
        "active_action": intent,
        "action_ids": action_ids,
        "latest_observation": None,
        "last_execution_success": None,
        "policy_decision": None,
        "policy_reason": None,
        "stage": "planning",
    }


def validate_action(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    intent = _get_current_intent(state)

    remaining_steps = state.get("remaining_steps", context.max_steps)
    result = context.policy.validate(
        state,
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

    try:
        observation = context.runner.execute(intent)
    except Exception as exc:
        error_code = (
            "runner_timeout" if isinstance(exc, TimeoutError) else "runner_exception"
        )
        observation = Observation(
            observation_id=f"obs-{uuid.uuid4().hex[:8]}",
            case_id=intent.case_id,
            action_id=intent.action_id,
            tool_id=intent.capability_id,
            status=ObservationStatus.EXECUTION_FAILED,
            success=False,
            error_code=error_code,
            error_message=_sanitize_error_message(exc),
            source_type=ObservationSourceType.RUNTIME,
            metadata={
                "source": "agent_runtime",
                "schema_id": "observation",
            },
        )
    else:
        observation = _normalize_failure_kind(observation)

    observation_ids = list(state.observation_ids)
    if observation.observation_id not in observation_ids:
        observation_ids.append(observation.observation_id)
    return {
        "latest_observation": observation,
        "observation_ids": observation_ids,
        "last_execution_success": observation.success,
        "remaining_steps": max(state.get("remaining_steps", 0) - 1, 0),
        "stage": "execution",
    }


def record_observation(
    state: CaseGraphState, context: RuntimeContext
) -> Dict[str, Any]:
    observation = _get_latest_observation(state)
    evidence = context.evidence_store.append_from_observation(observation)
    evidence_ids = list(state.get("evidence_ids", []))
    if evidence.evidence_id not in evidence_ids:
        evidence_ids.append(evidence.evidence_id)

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
        observation = _get_latest_observation(state)
        failure_kind = observation.status
        if remaining <= 0:
            failure_label = (
                "test failure"
                if failure_kind is ObservationStatus.TEST_FAILED
                else "runner failure"
            )
            return {
                "stage": "escalated",
                "termination_reason": (
                    f"Call budget exhausted after {failure_label} "
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
    if state.active_action is None:
        raise RuntimeError("No ActionIntent is available in graph state")
    return state.active_action


def _get_latest_observation(state: CaseGraphState) -> Observation:
    if state.latest_observation is None:
        raise RuntimeError("No Observation is available in graph state")
    return state.latest_observation


def _normalize_failure_kind(observation: Observation) -> Observation:
    """Classify unsuccessful Runner responses without changing successful data."""
    if observation.success:
        return observation
    if observation.status in {
        ObservationStatus.EXECUTION_FAILED,
        ObservationStatus.TEST_FAILED,
    }:
        return observation
    return observation.model_copy(
        update={"status": ObservationStatus.EXECUTION_FAILED},
        deep=True,
    )


def _sanitize_error_message(exc: Exception) -> str:
    """Retain actionable context while redacting common credential assignments."""
    message = str(exc).strip() or exc.__class__.__name__
    redacted = _SENSITIVE_VALUE.sub(
        lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
        message,
    )
    redacted = _LOCAL_PATH.sub("[LOCAL_PATH]", redacted)
    return redacted[:500]
