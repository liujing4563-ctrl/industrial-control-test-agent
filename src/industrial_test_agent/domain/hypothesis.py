from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class Hypothesis(BaseModel):
    hypothesis_id: str
    case_id: str
    description: str
    confidence: float
    status: str = "open"
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(frozen=False)
