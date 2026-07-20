"""Policy Validator V0 — Four deterministic rules."""

from __future__ import annotations

from typing import Any, Dict, Optional

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.policy.decisions import PolicyResult


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registered tool capabilities with schemas and risk levels."""

    _tools: Dict[str, Dict[str, Any]] = {
        "plc.read_interlock": {
            "tool_id": "plc.read_interlock",
            "name": "plc.read_interlock",
            "risk_level": "low",
            "write_operation": False,
            "input_schema": {
                "type": "object",
                "properties": {
                    "group": {"type": "string"},
                },
                "required": ["group"],
                "additionalProperties": False,
            },
        },
        "plc.read_signal": {
            "tool_id": "plc.read_signal",
            "name": "plc.read_signal",
            "risk_level": "low",
            "write_operation": False,
            "input_schema": {
                "type": "object",
                "properties": {
                    "signal_name": {"type": "string"},
                },
                "required": ["signal_name"],
                "additionalProperties": False,
            },
        },
        "plc.wait_feedback": {
            "tool_id": "plc.wait_feedback",
            "name": "plc.wait_feedback",
            "risk_level": "low",
            "write_operation": False,
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback_name": {"type": "string"},
                    "timeout_ms": {"type": "integer"},
                },
                "required": ["feedback_name"],
                "additionalProperties": False,
            },
        },
        "plc.write_test_signal": {
            "tool_id": "plc.write_test_signal",
            "name": "plc.write_test_signal",
            "risk_level": "medium",
            "write_operation": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "signal_name": {"type": "string"},
                    "value": {"type": "boolean"},
                },
                "required": ["signal_name", "value"],
                "additionalProperties": False,
            },
        },
    }

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[Dict[str, Any]]:
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
        tool_name = intent.action_details.get("tool_capability", "")
        if not self.tool_registry.is_allowed_tool(tool_name):
            return PolicyResult(
                decision="rejected",
                reason=f"Tool '{tool_name}' not in whitelist",
            )

        tool_info = self.tool_registry.get_tool(tool_name)
        assert tool_info is not None

        # Rule 2: Parameter schema validation
        if not self._validate_params(tool_info, intent.action_details.get("arguments", {})):
            return PolicyResult(
                decision="rejected",
                reason="Action arguments do not match tool schema",
                details={"tool": tool_name},
            )

        # Rule 3: Risk level
        risk_level = tool_info.get("risk_level", "unknown")
        requires_approval = (
            tool_info.get("write_operation", False)
            or risk_level not in self.allowed_risk_levels
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
                details={"tool": tool_name, "risk_level": risk_level},
            )

        return PolicyResult(
            decision="allowed",
            reason=f"Tool '{tool_name}' allowed (risk={risk_level})",
        )

    @staticmethod
    def _validate_params(tool_info: Dict[str, Any], arguments: Dict[str, Any]) -> bool:
        schema = tool_info.get("input_schema")
        if not schema:
            return True
        if not isinstance(arguments, dict):
            return False

        required = schema.get("required", [])
        if any(key not in arguments for key in required):
            return False

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            if any(key not in properties for key in arguments):
                return False

        for key, value in arguments.items():
            expected_type = properties.get(key, {}).get("type")
            if expected_type and not PolicyValidator._matches_json_type(
                value, expected_type
            ):
                return False
        return True

    @staticmethod
    def _matches_json_type(value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type == "object":
            return isinstance(value, dict)
        if expected_type == "array":
            return isinstance(value, list)
        return False
