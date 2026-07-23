from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import AwareDatetime, Field, field_validator, model_validator

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)


class HypothesisStatus(StrEnum):
    OPEN = "open"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Hypothesis(ContractModel):
    hypothesis_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.OPEN
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "description" not in value:
            return value
        legacy = dict(value)
        metadata = dict(legacy.pop("metadata", {}))
        created_by = legacy.pop("created_by", None)
        if created_by is not None:
            metadata["created_by"] = created_by
        legacy["statement"] = legacy.pop("description")
        legacy.setdefault("updated_at", legacy.get("created_at"))
        legacy["metadata"] = metadata
        return legacy

    @field_validator("metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)
