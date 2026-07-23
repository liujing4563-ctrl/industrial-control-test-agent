from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, field_validator

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)
from industrial_test_agent.domain.enums import RiskLevel


class CapabilityPackStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class ImplementationStatus(StrEnum):
    PLANNED = "planned"
    IMPLEMENTED = "implemented"


class DomainReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HardwareValidationStatus(StrEnum):
    NOT_STARTED = "not_started"
    PASSED = "passed"
    FAILED = "failed"


class CapabilityPackEntrypoints(ContractModel):
    instructions: str
    workflow: str
    fault_catalog: str
    examples: str
    evaluations: str


class CapabilityPackOwnership(ContractModel):
    implementation_owner: str
    domain_owner: str
    platform_reviewer: str
    domain_reviewer: str


class CapabilityPackReview(ContractModel):
    implementation_status: ImplementationStatus
    domain_review_status: DomainReviewStatus
    hardware_validation_status: HardwareValidationStatus


class CapabilityPackSafety(ContractModel):
    risk_level: RiskLevel
    permissions: list[str]


class CapabilityPackMetadata(ContractModel):
    supported_devices: list[str]
    required_mcp_tools: list[str]
    evidence_requirements: list[str]
    success_criteria: list[str]
    termination_criteria: list[str]
    regression_requirements: list[str]


class CapabilityPackManifest(ContractModel):
    """Platform structure only; nested domain values remain domain-owned."""

    schema_version: Literal["1.0"]
    pack_id: str = Field(min_length=1)
    name: str
    domain: str
    version: str
    status: CapabilityPackStatus
    description: str
    entrypoints: CapabilityPackEntrypoints
    ownership: CapabilityPackOwnership
    review: CapabilityPackReview
    safety: CapabilityPackSafety
    metadata: CapabilityPackMetadata


class SkillManifest(ContractModel):
    skill_id: str = Field(min_length=1)
    name: str
    version: str
    description: str
    inputs: list[str]
    outputs: list[str]
    allowed_tools: list[str]
    owner: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def require_json_metadata(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)
