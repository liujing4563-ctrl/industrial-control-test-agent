from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    finding_id: str
    case_id: str
    summary: str
    severity: str
    status: str = "open"
    related_evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(frozen=False)
