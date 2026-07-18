from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


@dataclass
class CaseGraphState:
    case_id: str
    stage: Literal[
        "intake",
        "planning",
        "execution",
        "diagnosis",
        "approval",
        "regression",
        "completed",
        "escalated",
    ] = "intake"
    goal: str = ""
    selected_capability_ids: List[str] = field(default_factory=list)
    active_domain: Optional[Literal["mcu", "plc_io", "cross_domain"]] = None
    hypothesis_ids: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    proposed_action_id: Optional[str] = None
    latest_observation_id: Optional[str] = None
    pending_approval_id: Optional[str] = None
    remaining_steps: int = 10
    root_cause_id: Optional[str] = None
    termination_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "stage": self.stage,
            "goal": self.goal,
            "selected_capability_ids": self.selected_capability_ids,
            "active_domain": self.active_domain,
            "hypothesis_ids": self.hypothesis_ids,
            "evidence_ids": self.evidence_ids,
            "proposed_action_id": self.proposed_action_id,
            "latest_observation_id": self.latest_observation_id,
            "pending_approval_id": self.pending_approval_id,
            "remaining_steps": self.remaining_steps,
            "root_cause_id": self.root_cause_id,
            "termination_reason": self.termination_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
