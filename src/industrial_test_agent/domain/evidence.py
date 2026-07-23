from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import (
    AwareDatetime,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)
from industrial_test_agent.domain.observation import Observation


class EvidenceType(StrEnum):
    TOOL_OBSERVATION = "tool_observation"


class Evidence(ContractModel):
    evidence_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    observation_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    evidence_type: EvidenceType
    payload: dict[str, Any]
    source: str
    content_hash: str = Field(min_length=1)
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    idempotency_key: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", frozen=True)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "evidence_type" in value:
            return value

        legacy = dict(value)
        metadata = dict(legacy.pop("metadata", {}))
        observation_payload = legacy.pop(
            "payload", metadata.pop("observation", None)
        )
        if observation_payload is None:
            return value
        observation = Observation.model_validate(observation_payload)
        canonical_payload = observation.model_dump(mode="json")
        content_hash = hashlib.sha256(
            observation.model_dump_json().encode()
        ).hexdigest()
        case_id = legacy.get("case_id", observation.case_id)
        observation_id = legacy.get(
            "observation_id", observation.observation_id
        )
        return {
            "evidence_id": legacy.pop("evidence_id"),
            "case_id": legacy.pop("case_id", observation.case_id),
            "observation_id": legacy.pop(
                "observation_id", observation.observation_id
            ),
            "action_id": legacy.pop("action_id", observation.action_id),
            "evidence_type": EvidenceType.TOOL_OBSERVATION,
            "payload": canonical_payload,
            "source": legacy.pop("source", observation.source),
            "content_hash": content_hash,
            "created_at": legacy.pop(
                "created_at", datetime.now(timezone.utc)
            ),
            "idempotency_key": legacy.pop(
                "idempotency_key",
                f"{case_id}:{observation_id}:tool-observation",
            ),
            "metadata": metadata,
            **legacy,
        }

    @field_validator("payload", "metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)
