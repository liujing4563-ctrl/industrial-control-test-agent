"""Enums shared by platform-owned contracts."""

from enum import StrEnum
from typing import Literal


PolicyDecision = Literal["allowed", "rejected", "approval_required"]


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SideEffectType(StrEnum):
    READ_ONLY = "read_only"
    TEST_WRITE = "test_write"
    EXTERNAL_SIDE_EFFECT = "external_side_effect"
