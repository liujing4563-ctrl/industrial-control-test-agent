from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionIntent(BaseModel):
    intent_id: str
    case_id: str
    action_type: str
    action_details: Dict[str, Any]
    reason: str
    requested_by: str
    priority: str = "medium"
    status: str = "draft"
    target_resource: Optional[str] = None
    related_evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    model_config = ConfigDict(frozen=False)
