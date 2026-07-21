"""Integration coverage for checkpoint recovery and runner failures."""

from __future__ import annotations

import json

import pytest

from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.runner.mock_runner import MockRunner


class TimeoutOnceRunner(MockRunner):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, intent):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("injected timeout")
        return super().execute(intent)


def test_replaying_same_checkpoint_does_not_duplicate_evidence():
    runner = GraphRunner()
    paused = runner.run(
        "case-replay",
        "test idempotent recovery",
        max_node_executions=4,
    )
    checkpoint = runner.checkpoint(paused)

    first = runner.resume(checkpoint)
    second = runner.resume(checkpoint)

    assert first["evidence_ids"] == second["evidence_ids"]
    assert len(runner.evidence_store.list_by_case("case-replay")) == 1


def test_checkpoint_restores_evidence_into_new_runner():
    original = GraphRunner()
    paused = original.run(
        "case-snapshot",
        "test Evidence recovery",
        max_node_executions=5,
    )
    checkpoint = original.checkpoint(paused)

    restored = GraphRunner()
    state = restored.resume(checkpoint)

    assert state["stage"] == "completed"
    assert state["evidence_ids"] == paused["evidence_ids"]
    for evidence_id in state["evidence_ids"]:
        assert restored.evidence_store.get(evidence_id) is not None


def test_checkpoint_rejects_invalid_stage_and_next_node():
    runner = GraphRunner()
    paused = runner.run(
        "case-invalid-route",
        "test checkpoint validation",
        max_node_executions=3,
    )
    payload = json.loads(runner.checkpoint(paused))
    payload["graph_state"]["stage"] = "planning"
    payload["graph_state"]["next_node"] = "record_observation"

    with pytest.raises(ValueError, match="Invalid stage/next_node combination"):
        GraphRunner().resume(payload)


def test_checkpoint_rejects_terminal_state_without_reason():
    runner = GraphRunner()
    completed = runner.run("case-invalid-terminal", "test terminal validation")
    payload = json.loads(runner.checkpoint(completed))
    payload["graph_state"]["termination_reason"] = None

    with pytest.raises(ValueError, match="requires termination_reason"):
        GraphRunner().resume(payload)


def test_checkpoint_rejects_missing_evidence_snapshot():
    runner = GraphRunner()
    paused = runner.run(
        "case-missing-evidence",
        "test snapshot validation",
        max_node_executions=5,
    )
    payload = json.loads(runner.checkpoint(paused))
    payload["evidence_snapshot"] = []

    with pytest.raises(ValueError, match="does not resolve"):
        GraphRunner().resume(payload)


def test_checkpoint_rejects_execution_result_mismatch():
    runner = GraphRunner()
    paused = runner.run(
        "case-result-mismatch",
        "test Observation validation",
        max_node_executions=4,
    )
    payload = json.loads(runner.checkpoint(paused))
    payload["graph_state"]["last_execution_success"] = False

    with pytest.raises(ValueError, match="does not match"):
        GraphRunner().resume(payload)


def test_runner_exception_becomes_observation_and_enters_replan():
    runner = GraphRunner(
        runner=TimeoutOnceRunner(),
        required_evidence_count=1,
        max_steps=2,
    )

    state = runner.run("case-timeout", "test runner timeout")

    assert state["stage"] == "completed"
    assert state["replan_count"] == 1
    assert "runner failure routed to replan" in runner.log

    records = runner.evidence_store.list_by_case("case-timeout")
    assert len(records) == 2
    failed_observation = records[0].metadata["observation"]
    assert failed_observation["payload"]["failure_kind"] == "execution"
    assert failed_observation["payload"]["error_code"] == "runner_timeout"
    assert failed_observation["payload"]["error_message"] == "injected timeout"
