"""Policy Validator V0 — Four deterministic rules."""

from __future__ import annotations

from typing import Optional

from jsonschema import Draft202012Validator

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.enums import RiskLevel, SideEffectType
from industrial_test_agent.mcp.models import ToolCapability
from industrial_test_agent.policy.decisions import PolicyResult


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registered tool capabilities with schemas and risk levels."""

    _tools: dict[str, ToolCapability] = {
        "plc.read_interlock": ToolCapability(
            capability_id="plc.read_interlock",
            display_name="plc.read_interlock",
            description="M1 Mock capability for Runtime validation",
            risk_level=RiskLevel.LOW,
            requires_approval=False,
            side_effect_type=SideEffectType.READ_ONLY,
            input_schema={
                "type": "object",
                "properties": {
                    "group": {"type": "string"},
                },
                "required": ["group"],
                "additionalProperties": False,
            },
        ),
        "plc.read_signal": ToolCapability(
            capability_id="plc.read_signal",
            display_name="plc.read_signal",
            description="M1 Mock capability for Runtime validation",
            risk_level=RiskLevel.LOW,
            requires_approval=False,
            side_effect_type=SideEffectType.READ_ONLY,
            input_schema={
                "type": "object",
                "properties": {
                    "signal_name": {"type": "string"},
                },
                "required": ["signal_name"],
                "additionalProperties": False,
            },
        ),
        "plc.wait_feedback": ToolCapability(
            capability_id="plc.wait_feedback",
            display_name="plc.wait_feedback",
            description="M1 Mock capability for Runtime validation",
            risk_level=RiskLevel.LOW,
            requires_approval=False,
            side_effect_type=SideEffectType.READ_ONLY,
            input_schema={
                "type": "object",
                "properties": {
                    "feedback_name": {"type": "string"},
                    "timeout_ms": {"type": "integer"},
                },
                "required": ["feedback_name"],
                "additionalProperties": False,
            },
        ),
        "plc.write_test_signal": ToolCapability(
            capability_id="plc.write_test_signal",
            display_name="plc.write_test_signal",
            description="M1 Mock write capability requiring approval",
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            side_effect_type=SideEffectType.TEST_WRITE,
            input_schema={
                "type": "object",
                "properties": {
                    "signal_name": {"type": "string"},
                    "value": {"type": "boolean"},
                },
                "required": ["signal_name", "value"],
                "additionalProperties": False,
            },
        ),
    }

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[ToolCapability]:
        return cls._tools.get(tool_name)

    @classmethod
    def is_allowed_tool(cls, tool_name: str) -> bool:
        return tool_name in cls._tools


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class PolicyValidator:
    """Apply four deterministic safety rules to an ActionIntent."""

    MAX_STEPS = 20

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        allowed_risk_levels: Optional[set[str]] = None,
    ) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.allowed_risk_levels = (
            {"low"} if allowed_risk_levels is None else allowed_risk_levels
        )

    def validate(
        self,
        case_state: CaseState,
        intent: ActionIntent,
        steps_taken: int = 0,
        remaining_call_budget: Optional[int] = None,
    ) -> PolicyResult:
        # Rule 1: Tool whitelist
        tool_name = intent.capability_id
        if not self.tool_registry.is_allowed_tool(tool_name):
            return PolicyResult(
                decision="rejected",
                reason=f"Tool '{tool_name}' not in whitelist",
            )

        tool_info = self.tool_registry.get_tool(tool_name)
        assert tool_info is not None

        # Rule 2: Parameter schema validation
        if not self._validate_params(tool_info, intent.arguments):
            return PolicyResult(
                decision="rejected",
                reason="Action arguments do not match tool schema",
                details={"tool": tool_name},
            )

        # Rule 3: Risk level
        risk_level = tool_info.risk_level
        requires_approval = (
            tool_info.requires_approval
            or risk_level.value not in self.allowed_risk_levels
        )

        # Rule 4: Remaining call budget
        budget_exhausted = (
            remaining_call_budget is not None and remaining_call_budget <= 0
        ) or (
            remaining_call_budget is None and steps_taken >= self.MAX_STEPS
        )
        if budget_exhausted:
            return PolicyResult(
                decision="rejected",
                reason="Call budget exhausted",
                details={
                    "remaining_call_budget": remaining_call_budget,
                    "steps_taken": steps_taken,
                },
            )

        if requires_approval:
            return PolicyResult(
                decision="approval_required",
                reason=f"Tool '{tool_name}' requires human approval",
                details={
                    "tool": tool_name,
                    "risk_level": risk_level.value,
                },
            )

        return PolicyResult(
            decision="allowed",
            reason=f"Tool '{tool_name}' allowed (risk={risk_level.value})",
        )

    @staticmethod
    def _validate_params(
        tool_info: ToolCapability,
        arguments: dict[str, object],
    ) -> bool:
        return Draft202012Validator(tool_info.input_schema).is_valid(
            arguments
        )
