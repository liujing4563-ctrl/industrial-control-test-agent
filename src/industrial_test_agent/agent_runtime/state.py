"""CaseGraphState — lightweight runtime state for LangGraph.

Only stores IDs and references. Full Evidence / Observation payloads live
in the Evidence Store, not in graph state.
"""

from __future__ import annotations

from typing import Literal, Optional
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
        "completed",
        "escalated",
        "rejected",
    ]

    proposed_action_id: Optional[str]
    latest_observation_id: Optional[str]

    evidence_ids: list[str]
    hypothesis_ids: list[str]

    remaining_steps: int
    termination_reason: Optional[str]
    policy_decision: Optional[str]
