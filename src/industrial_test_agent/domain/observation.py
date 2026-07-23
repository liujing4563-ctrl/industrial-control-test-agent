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


class ObservationStatus(StrEnum):
    POLICY_REJECTED = "policy_rejected"
    EXECUTION_FAILED = "execution_failed"
    TEST_FAILED = "test_failed"
    SUCCEEDED = "succeeded"


class ObservationSourceType(StrEnum):
    MOCK = "mock"
    RUNTIME = "runtime"
    MCP = "mcp"
    SIMULATOR = "simulator"
    HARDWARE = "hardware"


class Observation(ContractModel):
    observation_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    tool_id: str = Field(min_length=1)
    status: ObservationStatus
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    received_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source_type: ObservationSourceType
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "payload" not in value:
            return value

        legacy = dict(value)
        payload = dict(legacy.pop("payload", {}))
        action_id = (
            legacy.pop("action_id", None)
            or legacy.pop("related_action_intent_id", None)
            or payload.pop("action_id", None)
            or "unknown-action"
        )
        data = payload.pop("data", None)
        success = bool(payload.pop("success", True))
        failure_kind = payload.pop("failure_kind", None)
        legacy_status = payload.pop("status", None)

        if success:
            status = ObservationStatus.SUCCEEDED
        elif failure_kind == "test_failed" or legacy_status == "completed":
            status = ObservationStatus.TEST_FAILED
        else:
            status = ObservationStatus.EXECUTION_FAILED

        if data is None:
            excluded = {
                "error",
                "error_code",
                "error_message",
                "timestamp",
            }
            data = {
                key: item
                for key, item in payload.items()
                if key not in excluded
            }
        tool_id = (
            legacy.pop("tool_id", None)
            or data.get("tool")
            or "unknown-tool"
        )
        metadata = dict(legacy.pop("metadata", {}))
        source = legacy.pop("source", None)
        schema_id = legacy.pop("schema_id", None)
        if source is not None:
            metadata["source"] = source
        if schema_id is not None:
            metadata["schema_id"] = schema_id

        return {
            "observation_id": legacy.pop("observation_id"),
            "case_id": legacy.pop("case_id"),
            "action_id": action_id,
            "tool_id": tool_id,
            "status": status,
            "success": success,
            "data": data,
            "error_code": payload.pop("error_code", None),
            "error_message": payload.pop(
                "error_message", payload.pop("error", None)
            ),
            "received_at": legacy.pop(
                "timestamp",
                payload.pop("timestamp", datetime.now(timezone.utc)),
            ),
            "source_type": legacy.pop("source_type"),
            "metadata": metadata,
            **legacy,
        }

    @model_validator(mode="after")
    def validate_status_consistency(self) -> Self:
        if self.status is ObservationStatus.SUCCEEDED and not self.success:
            raise ValueError("succeeded Observation must have success=true")
        if self.status is not ObservationStatus.SUCCEEDED and self.success:
            raise ValueError(
                "non-succeeded Observation must have success=false"
            )
        return self

    @field_validator("data", "metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)

    @property
    def source(self) -> str:
        return str(self.metadata.get("source", self.source_type.value))

    @property
    def schema_id(self) -> str:
        return str(self.metadata.get("schema_id", "observation"))

    @property
    def related_action_intent_id(self) -> str:
        return self.action_id

    @property
    def payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "action_id": self.action_id,
            "success": self.success,
            "status": (
                "completed"
                if self.status
                in {
                    ObservationStatus.SUCCEEDED,
                    ObservationStatus.TEST_FAILED,
                }
                else "failed"
            ),
            "data": self.data,
            "timestamp": self.received_at.isoformat(),
        }
        if self.status in {
            ObservationStatus.EXECUTION_FAILED,
            ObservationStatus.TEST_FAILED,
        }:
            payload["failure_kind"] = self.status.value
        if self.error_code is not None:
            payload["error_code"] = self.error_code
        if self.error_message is not None:
            payload["error_message"] = self.error_message
            payload["error"] = self.error_message
        return payload
