from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class Observation(ContractModel):
    observation_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    source: str
    source_type: str
    payload: dict[str, Any]
    schema_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    related_action_intent_id: Optional[str] = None
