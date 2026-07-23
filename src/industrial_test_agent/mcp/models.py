from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from pydantic import Field, field_validator, model_validator

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)
from industrial_test_agent.domain.enums import RiskLevel, SideEffectType


class RetryPolicy(ContractModel):
    max_attempts: int = Field(default=1, ge=1)
    backoff_seconds: float = Field(default=0, ge=0)


class ToolCapability(ContractModel):
    capability_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    description: str
    input_schema: dict[str, Any]
    risk_level: RiskLevel
    requires_approval: bool
    side_effect_type: SideEffectType
    timeout_seconds: float = Field(default=30, gt=0)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "tool_id" not in value:
            return value
        legacy = dict(value)
        capability_id = legacy.pop("tool_id")
        display_name = legacy.pop("name")
        metadata = dict(legacy.pop("metadata", {}))
        for key in ("transport", "output_schema", "permissions"):
            if key in legacy:
                metadata[key] = legacy.pop(key)
        return {
            "capability_id": capability_id,
            "display_name": display_name,
            "description": legacy.pop("description", display_name),
            "input_schema": legacy.pop("input_schema"),
            "risk_level": legacy.pop("risk_level", RiskLevel.LOW),
            "requires_approval": legacy.pop(
                "requires_approval", False
            ),
            "side_effect_type": legacy.pop(
                "side_effect_type", SideEffectType.READ_ONLY
            ),
            "timeout_seconds": legacy.pop("timeout_seconds", 30),
            "retry_policy": legacy.pop("retry_policy", {}),
            "tags": legacy.pop("tags", []),
            "metadata": metadata,
            **legacy,
        }

    @field_validator("input_schema")
    @classmethod
    def require_valid_json_schema(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        validate_json_object(value)
        try:
            Draft202012Validator.check_schema(value)
        except SchemaError as exc:
            raise ValueError("input_schema must be valid JSON Schema") from exc
        return value

    @field_validator("metadata")
    @classmethod
    def require_json_metadata(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)

    @property
    def tool_id(self) -> str:
        return self.capability_id

    @property
    def name(self) -> str:
        return self.display_name


class MCPRegistration(ContractModel):
    server_id: str = Field(min_length=1)
    version: str
    tools: list[ToolCapability]
    network_scope: str | None = None
    timeout_seconds: int = Field(default=30, gt=0)
    max_calls: int = Field(default=10, ge=1)
    environment_type: str = "test"
