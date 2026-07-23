from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import AwareDatetime, Field, field_validator, model_validator

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)
from industrial_test_agent.domain.enums import RiskLevel


class ActionIntent(ContractModel):
    action_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    capability_id: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    requested_by: str = Field(min_length=1)
    reason: str = ""
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    idempotency_key: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "action_id" in value:
            return value
        if "intent_id" not in value:
            return value

        legacy = dict(value)
        action_id = legacy.pop("intent_id")
        case_id = legacy.pop("case_id")
        details = dict(legacy.pop("action_details", {}))
        action_type = legacy.pop("action_type", None)
        capability_id = details.pop("tool_capability", None) or action_type
        arguments = details.pop("arguments", {})
        priority = legacy.pop("priority", RiskLevel.MEDIUM)
        if priority not in {level.value for level in RiskLevel}:
            priority = RiskLevel.MEDIUM

        metadata = dict(legacy.pop("metadata", {}))
        legacy_metadata = {
            "action_type": action_type,
            "status": legacy.pop("status", None),
            "target_resource": legacy.pop("target_resource", None),
            "related_evidence_ids": legacy.pop(
                "related_evidence_ids", None
            ),
            "approved_by": legacy.pop("approved_by", None),
            "approved_at": legacy.pop("approved_at", None),
        }
        if details:
            legacy_metadata["action_details"] = details
        for key, item in legacy_metadata.items():
            if item is not None:
                if isinstance(item, datetime):
                    item = item.isoformat()
                metadata[key] = item

        migrated = {
            "action_id": action_id,
            "case_id": case_id,
            "capability_id": capability_id,
            "arguments": arguments,
            "risk_level": priority,
            "requested_by": legacy.pop("requested_by"),
            "reason": legacy.pop("reason", ""),
            "created_at": legacy.pop(
                "created_at", datetime.now(timezone.utc)
            ),
            "idempotency_key": legacy.pop(
                "idempotency_key", f"{case_id}:{action_id}"
            ),
            "metadata": metadata,
            **legacy,
        }
        return migrated

    @field_validator("arguments", "metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)

    @property
    def intent_id(self) -> str:
        return self.action_id

    @property
    def action_details(self) -> dict[str, Any]:
        return {
            "tool_capability": self.capability_id,
            "arguments": self.arguments,
        }
