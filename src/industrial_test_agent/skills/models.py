from enum import StrEnum
from typing import Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class CapabilityPackStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CapabilityPackManifest(ContractModel):
    """Platform-owned manifest shape; domain values remain domain-owned."""

    capability_pack_id: str = Field(min_length=1)
    name: str
    version: str
    domain: str
    owner: str
    approver: str
    status: CapabilityPackStatus
    risk_level: RiskLevel
    description: str
    supported_devices: list[str]
    required_mcp_tools: list[str]
    permissions: list[str]
    evidence_requirements: list[str]
    success_criteria: list[str]
    termination_criteria: list[str]
    regression_requirements: list[str]


class SkillManifest(ContractModel):
    skill_id: str = Field(min_length=1)
    name: str
    version: str
    description: str
    inputs: list[str]
    outputs: list[str]
    allowed_tools: list[str]
    owner: Optional[str] = None
