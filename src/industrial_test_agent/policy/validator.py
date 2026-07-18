"""Policy Validator V0 — Four deterministic rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState


@dataclass
class PolicyResult:
    decision: str  # allowed | rejected | approval_required
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


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

    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        self.tool_registry = tool_registry or ToolRegistry()

    def validate(
        self, case_state: CaseState, intent: ActionIntent, steps_taken: int = 0
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

        # Rule 3: Call budget
        if steps_taken >= self.MAX_STEPS:
            return PolicyResult(
                decision="rejected",
                reason=f"Step budget exhausted ({steps_taken}/{self.MAX_STEPS})",
            )

        # Rule 4: Risk level → write operations require approval
        if tool_info.get("write_operation", False):
            return PolicyResult(
                decision="approval_required",
                reason=f"Tool '{tool_name}' is a write operation – human approval required",
                details={"tool": tool_name, "risk_level": tool_info.get("risk_level")},
            )

        return PolicyResult(
            decision="allowed",
            reason=f"Tool '{tool_name}' allowed (risk={tool_info.get('risk_level')})",
        )

    @staticmethod
    def _validate_params(tool_info: Dict[str, Any], arguments: Dict[str, Any]) -> bool:
        schema = tool_info.get("input_schema")
        if not schema:
            return True  # no schema → pass
        required = schema.get("required", [])
        for key in required:
            if key not in arguments:
                return False
        return True
