"""Tests for Mock Runner V0."""

from __future__ import annotations

import pytest

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.runner.mock_runner import MockRunner


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def runner() -> MockRunner:
    return MockRunner()


def _intent(case_id: str, tool: str, args: dict | None = None) -> ActionIntent:
    if args is None:
        args = {}
    return ActionIntent(
        intent_id="act-001",
        case_id=case_id,
        action_type="test_request",
        action_details={"tool_capability": tool, "arguments": args},
        reason="test",
        requested_by="tester",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMockRunner:
    def test_read_interlock_returns_success(self, runner):
        obs = runner.execute(_intent("case-001", "plc.read_interlock", {"group": "motor"}))
        assert obs.payload["success"] is True
        assert obs.payload["data"]["all_clear"] is True
        assert "motor" in obs.payload["data"]["group"]

    def test_read_signal_returns_value(self, runner):
        obs = runner.execute(_intent("case-001", "plc.read_signal", {"signal_name": "x"}))
        assert obs.payload["success"] is True
        assert obs.payload["data"]["value"] is True

    def test_wait_feedback_returns_received(self, runner):
        obs = runner.execute(_intent("case-001", "plc.wait_feedback", {"feedback_name": "fb1"}))
        assert obs.payload["success"] is True
        assert obs.payload["data"]["received"] is True

    def test_unsupported_tool_returns_error(self, runner):
        obs = runner.execute(_intent("case-001", "nonexistent.tool"))
        assert obs.payload["success"] is False
        assert "error" in obs.payload

    def test_observation_has_action_ref(self, runner):
        obs = runner.execute(_intent("case-002", "plc.read_interlock"))
        assert obs.related_action_intent_id == "act-001"
        assert obs.case_id == "case-002"

    def test_observation_schema_id(self, runner):
        obs = runner.execute(_intent("case-001", "plc.read_interlock"))
        assert obs.schema_id == "observation"

    def test_observation_ids_are_unique(self, runner):
        obs1 = runner.execute(_intent("case-001", "plc.read_interlock"))
        obs2 = runner.execute(_intent("case-001", "plc.read_interlock"))
        assert obs1.observation_id != obs2.observation_id
