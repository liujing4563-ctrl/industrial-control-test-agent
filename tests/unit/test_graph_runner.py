"""Tests for Agent Runtime Graph (end-to-end flows)."""

from __future__ import annotations

from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.evidence.in_memory_store import EvidenceStore
from industrial_test_agent.runner.mock_runner import MockRunner


class FailOnceRunner(MockRunner):
    def __init__(self):
        self.calls = 0

    def execute(self, intent):
        self.calls += 1
        if self.calls == 1:
            return Observation(
                observation_id="obs-failed",
                case_id=intent.case_id,
                source="mock_runner",
                source_type="mock",
                payload={
                    "action_id": intent.intent_id,
                    "success": False,
                    "status": "error",
                    "error": "injected failure",
                },
                schema_id="observation",
                related_action_intent_id=intent.intent_id,
            )
        return super().execute(intent)


class TestGraphRunner:
    def test_normal_flow_completes(self):
        runner = GraphRunner(required_evidence_count=3)
        state = runner.run("case-001", "test goal")
        assert state["stage"] == "completed"
        assert len(state["evidence_ids"]) >= 3
        assert "case completed" in runner.log[-1]

    def test_evidence_sufficiency_triggers_completion(self):
        """Graph completes when enough evidence is collected."""
        runner = GraphRunner(required_evidence_count=2, max_steps=10)
        state = runner.run("case-001", "test")
        assert state["stage"] == "completed"
        assert len(state["evidence_ids"]) >= 2
        assert "evidence records collected" in state["termination_reason"]

    def test_budget_exhausted_escalates(self):
        """Graph escalates when step budget runs out before enough evidence."""
        runner = GraphRunner(required_evidence_count=100, max_steps=2)
        state = runner.run("case-001", "test")
        assert state["stage"] == "escalated"
        assert "budget" in state["termination_reason"].lower()

    def test_configurable_max_steps(self):
        """Verify max_steps is configurable and terminates correctly."""
        runner = GraphRunner(required_evidence_count=1, max_steps=5)
        state = runner.run("case-001", "test")
        assert state["stage"] == "completed"
        assert len(state["evidence_ids"]) >= 1

    def test_unknown_tool_rejected(self):
        agent = MockAgent(tool_name="unknown.bad_tool")
        runner = GraphRunner(agent=agent)
        state = runner.run("case-001", "test")
        assert state["stage"] == "rejected"
        assert "policy decision: rejected" in runner.log

    def test_approval_required_stops(self):
        agent = MockAgent(tool_name="plc.write_test_signal", arguments={"signal_name": "x", "value": True})
        runner = GraphRunner(agent=agent)
        state = runner.run("case-001", "test")
        assert state["stage"] == "escalated"
        assert "approval" in state.get("termination_reason", "").lower()

    def test_evidence_is_appended(self):
        runner = GraphRunner()
        state = runner.run("case-001", "test")
        assert len(state["evidence_ids"]) >= 1
        for eid in state["evidence_ids"]:
            assert eid.startswith("ev-")

    def test_case_state_has_id(self):
        runner = GraphRunner()
        state = runner.run("case-xyz", "goal")
        assert state["case_id"] == "case-xyz"
        assert state["goal"] == "goal"

    def test_evidence_store_has_records(self):
        store = EvidenceStore()
        runner = GraphRunner(evidence_store=store)
        state = runner.run("case-001", "test")
        records = store.list_by_case("case-001")
        assert len(records) == len(state["evidence_ids"])

    def test_log_contains_expected_messages(self):
        runner = GraphRunner()
        runner.run("case-001", "test")
        assert "case initialized" in runner.log
        assert any(message.startswith("action proposed:") for message in runner.log)
        assert "mock runner executed" in runner.log

    def test_action_intent_id_is_stable_through_execution(self):
        store = EvidenceStore()
        runner = GraphRunner(evidence_store=store)
        state = runner.run("case-001", "test")
        evidence = store.get(state["evidence_ids"][0])
        assert evidence is not None
        observation = evidence.metadata["observation"]
        assert observation["related_action_intent_id"] == state["proposed_action_id"]

    def test_runner_failure_enters_replan_then_recovers(self):
        runner = GraphRunner(
            runner=FailOnceRunner(),
            required_evidence_count=1,
            max_steps=3,
        )
        state = runner.run("case-001", "test")
        assert state["stage"] == "completed"
        assert state["replan_count"] == 1
        assert "runner failure routed to replan" in runner.log

    def test_execute_and_record_are_separate_nodes(self):
        store = EvidenceStore()
        runner = GraphRunner(evidence_store=store)
        state = runner.run(
            "case-001",
            "test",
            max_node_executions=4,
        )
        assert state["next_node"] == "record_observation"
        assert state["latest_observation_id"] is not None
        assert state["evidence_ids"] == []
        assert store.list_by_case("case-001") == []

    def test_graph_can_resume_serialized_state(self):
        runner = GraphRunner()
        paused = runner.run(
            "case-restore",
            "test recovery",
            max_node_executions=3,
        )
        checkpoint = runner.checkpoint(paused)

        restored_runner = GraphRunner()
        state = restored_runner.resume(checkpoint)
        assert state["stage"] == "completed"
        assert state["case_id"] == "case-restore"
        assert len(state["evidence_ids"]) == 1
