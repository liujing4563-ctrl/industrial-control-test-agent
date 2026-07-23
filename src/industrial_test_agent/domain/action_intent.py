from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class ActionPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"


class ActionIntent(ContractModel):
    intent_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    action_type: str
    action_details: dict[str, Any]
    reason: str
    requested_by: str
    priority: ActionPriority = ActionPriority.MEDIUM
    status: ActionStatus = ActionStatus.DRAFT
    target_resource: Optional[str] = None
    related_evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
