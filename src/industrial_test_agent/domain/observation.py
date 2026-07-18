from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class Observation(BaseModel):
    observation_id: str
    case_id: str
    source: str
    source_type: str
    payload: Dict[str, Any]
    schema_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    related_action_intent_id: Optional[str] = None

    model_config = ConfigDict(frozen=False)
