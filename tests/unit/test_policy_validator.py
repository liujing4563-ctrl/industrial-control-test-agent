"""Tests for Policy Validator V0."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.policy.validator import PolicyValidator, PolicyResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def case() -> CaseState:
    return CaseState(case_id="case-001", current_phase="planning")


@pytest.fixture
def validator() -> PolicyValidator:
    return PolicyValidator()


def _intent(case: CaseState, tool: str, args: dict | None = None) -> ActionIntent:
    if args is None:
        args = {"group": "motor_start"}
    return ActionIntent(
        intent_id="act-001",
        case_id=case.case_id,
        action_type="test_request",
        action_details={"tool_capability": tool, "arguments": args},
        reason="test",
        requested_by="tester",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPolicyValidator:
    def test_allowed_tool_passes(self, case, validator):
        """Rule 1+2: whitelisted tool with valid args → allowed."""
        result = validator.validate(case, _intent(case, "plc.read_interlock"))
        assert result.decision == "allowed"
        assert "plc.read_interlock" in result.reason

    def test_unknown_tool_rejected(self, case, validator):
        """Rule 1: tool not in whitelist → rejected."""
        result = validator.validate(case, _intent(case, "unknown.tool"))
        assert result.decision == "rejected"
        assert "not in whitelist" in result.reason

    def test_missing_required_arg_rejected(self, case, validator):
        """Rule 2: missing required parameter → rejected."""
        result = validator.validate(
            case,
            _intent(case, "plc.read_interlock", args={"extra": "value"}),
        )
        assert result.decision == "rejected"

    def test_wrong_argument_type_rejected(self, case, validator):
        result = validator.validate(
            case,
            _intent(case, "plc.read_interlock", args={"group": 123}),
        )
        assert result.decision == "rejected"

    def test_unexpected_argument_rejected(self, case, validator):
        result = validator.validate(
            case,
            _intent(
                case,
                "plc.read_interlock",
                args={"group": "motor_start", "unsafe_extra": True},
            ),
        )
        assert result.decision == "rejected"

    def test_write_operation_requires_approval(self, case, validator):
        """Rule 4: write tool → approval_required."""
        result = validator.validate(
            case,
            _intent(case, "plc.write_test_signal", args={"signal_name": "x", "value": True}),
        )
        assert result.decision == "approval_required"

    def test_budget_exhausted_rejected(self, case, validator):
        """Rule 3: steps taken >= max → rejected."""
        result = validator.validate(
            case, _intent(case, "plc.read_interlock"), steps_taken=20
        )
        assert result.decision == "rejected"
        assert "budget" in result.reason.lower()

    def test_remaining_budget_exhausted_rejected(self, case, validator):
        result = validator.validate(
            case,
            _intent(case, "plc.read_interlock"),
            remaining_call_budget=0,
        )
        assert result.decision == "rejected"

    def test_read_signal_allowed(self, case, validator):
        result = validator.validate(
            case,
            _intent(case, "plc.read_signal", args={"signal_name": "motor_run"}),
        )
        assert result.decision == "allowed"

    def test_wait_feedback_allowed(self, case, validator):
        result = validator.validate(
            case,
            _intent(case, "plc.wait_feedback", args={"feedback_name": "start_fb"}),
        )
        assert result.decision == "allowed"

    def test_policy_result_dataclass(self):
        pr = PolicyResult(decision="allowed", reason="ok")
        assert pr.decision == "allowed"
        assert isinstance(pr.reason, str)
