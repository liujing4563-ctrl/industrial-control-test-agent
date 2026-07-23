"""Tests for Mock Agent V0."""

from __future__ import annotations

import pytest

from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.agents.mock_agent import MockAgent


@pytest.fixture
def case() -> CaseState:
    return CaseState(case_id="case-001", current_phase="planning")


class TestMockAgent:
    def test_propose_returns_action_intent(self, case):
        agent = MockAgent()
        intent = agent.propose(case)
        assert isinstance(intent, ActionIntent)
        assert intent.metadata["action_type"] == "test_request"
        assert intent.case_id == "case-001"

    def test_default_tool_is_interlock(self, case):
        agent = MockAgent()
        intent = agent.propose(case)
        assert intent.capability_id == "plc.read_interlock"

    def test_custom_tool(self, case):
        agent = MockAgent(tool_name="plc.read_signal", arguments={"signal_name": "x"})
        intent = agent.propose(case)
        assert intent.capability_id == "plc.read_signal"
        assert intent.arguments == {"signal_name": "x"}

    def test_intent_has_unique_id(self, case):
        agent = MockAgent()
        i1 = agent.propose(case)
        i2 = agent.propose(case)
        assert i1.intent_id != i2.intent_id

    def test_intent_has_idempotency_key(self, case):
        agent = MockAgent()
        intent = agent.propose(case)
        assert intent.idempotency_key == f"{case.case_id}:{intent.action_id}"

    def test_agent_name_in_intent(self, case):
        agent = MockAgent()
        intent = agent.propose(case)
        assert intent.requested_by == "mock_agent"
