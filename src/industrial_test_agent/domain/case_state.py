from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class CaseState(ContractModel):
    case_id: str = Field(min_length=1)
    current_phase: str
    test_objective: Optional[str] = None
    requirements: list[str] = Field(default_factory=list)
    test_cases: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)
    excluded_causes: list[str] = Field(default_factory=list)
    remaining_budget: Optional[float] = None
    approval_status: str = "pending"
    regression_status: str = "pending"
    root_cause_id: Optional[str] = None
    pending_approval_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
