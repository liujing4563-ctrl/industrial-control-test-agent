"""Serializable state for the deterministic Agent Runtime V0 graph.

The active ActionIntent and Observation are retained for checkpoint recovery.
Historical evidence remains append-only and is referenced by ID.
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from typing_extensions import TypedDict


class CaseGraphState(TypedDict):
    case_id: str
    goal: str

    stage: Literal[
        "initialized",
        "planning",
        "validation",
        "execution",
        "diagnosis",
        "replanning",
        "completed",
        "escalated",
        "rejected",
    ]

    proposed_action_id: Optional[str]
    proposed_action: Optional[dict[str, Any]]
    latest_observation_id: Optional[str]
    latest_observation: Optional[dict[str, Any]]

    evidence_ids: list[str]
    hypothesis_ids: list[str]

    remaining_steps: int
    replan_count: int
    last_execution_success: Optional[bool]
    termination_reason: Optional[str]
    policy_decision: Optional[str]
    policy_reason: Optional[str]
    next_node: Optional[str]
