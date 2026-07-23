from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class Finding(ContractModel):
    finding_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    summary: str
    severity: str
    status: str = "open"
    related_evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None
