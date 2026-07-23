from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Self

from pydantic import (
    AwareDatetime,
    Field,
    field_validator,
    model_validator,
)

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)


class FindingSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(StrEnum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Finding(ContractModel):
    finding_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str
    severity: FindingSeverity
    status: FindingStatus = FindingStatus.OPEN
    evidence_ids: list[str] = Field(default_factory=list)
    hypothesis_ids: list[str] = Field(default_factory=list)
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    closed_at: AwareDatetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "summary" not in value:
            return value
        legacy = dict(value)
        summary = legacy.pop("summary")
        legacy["title"] = summary
        legacy.setdefault("description", summary)
        if "related_evidence_ids" in legacy:
            legacy["evidence_ids"] = legacy.pop(
                "related_evidence_ids"
            )
        return legacy

    @model_validator(mode="after")
    def validate_closure(self) -> Self:
        closed_statuses = {
            FindingStatus.RESOLVED,
            FindingStatus.CLOSED,
        }
        if self.closed_at is not None and self.status not in closed_statuses:
            raise ValueError(
                "closed_at is only valid for resolved or closed findings"
            )
        if self.status is FindingStatus.CLOSED and self.closed_at is None:
            raise ValueError("closed finding requires closed_at")
        return self

    @field_validator("metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)
