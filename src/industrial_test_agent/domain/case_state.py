from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseState(BaseModel):
    case_id: str
    current_phase: str
    test_objective: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)
    test_cases: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    hypothesis_ids: List[str] = Field(default_factory=list)
    excluded_causes: List[str] = Field(default_factory=list)
    remaining_budget: Optional[float] = None
    approval_status: str = "pending"
    regression_status: str = "pending"
    root_cause_id: Optional[str] = None
    pending_approval_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(frozen=False)
