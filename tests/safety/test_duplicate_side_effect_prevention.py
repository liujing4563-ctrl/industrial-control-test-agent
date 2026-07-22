"""Safety tests preventing Runner side effects during recovery replay."""

from __future__ import annotations

from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.runner.mock_runner import MockRunner


class CountingRunner(MockRunner):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, intent: ActionIntent) -> Observation:
        self.calls += 1
        return super().execute(intent)


def test_resume_after_execution_does_not_execute_completed_action_again() -> None:
    original_runner = CountingRunner()
    original = GraphRunner(runner=original_runner)
    paused = original.run(
        "case-side-effect",
        "validate side-effect boundary",
        max_node_executions=4,
    )
    checkpoint = original.checkpoint(paused)
    assert original_runner.calls == 1
    assert paused["next_node"] == "record_observation"

    recovery_runner = CountingRunner()
    recovered = GraphRunner(runner=recovery_runner)
    first = recovered.resume(checkpoint)
    second = recovered.resume(checkpoint)

    assert first["stage"] == "completed"
    assert first["evidence_ids"] == second["evidence_ids"]
    assert recovery_runner.calls == 0
    assert len(recovered.evidence_store.list_by_case("case-side-effect")) == 1
