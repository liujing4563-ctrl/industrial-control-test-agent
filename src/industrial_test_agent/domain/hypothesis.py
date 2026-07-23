from __future__ import annotations

from datetime import datetime, timezone

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class Hypothesis(ContractModel):
    hypothesis_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    description: str
    confidence: float
    status: str = "open"
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
