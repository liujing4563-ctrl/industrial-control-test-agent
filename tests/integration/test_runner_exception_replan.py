"""Runner failure classification and routing integration tests."""

from __future__ import annotations

from pathlib import Path

from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.runner.mock_runner import MockRunner


SENSITIVE_LOCAL_PATH = str(Path("/", "Users", "example", "private"))
SENSITIVE_KEY_NAME = "api_" + "key"
REDACTION_MARKER = "to" + "ken"


class TimeoutOnceRunner(MockRunner):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, intent: ActionIntent) -> Observation:
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("connection timeout")
        return super().execute(intent)


class FailedAssertionOnceRunner(MockRunner):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, intent: ActionIntent) -> Observation:
        self.calls += 1
        if self.calls == 1:
            return Observation(
                observation_id="obs-test-failed",
                case_id=intent.case_id,
                source="mock_runner",
                source_type="mock",
                payload={
                    "action_id": intent.intent_id,
                    "success": False,
                    "status": "completed",
                    "failure_kind": "test_failed",
                    "error_code": "expected_condition_not_met",
                },
                schema_id="observation",
                related_action_intent_id=intent.intent_id,
            )
        return super().execute(intent)


class SensitiveFailureRunner(MockRunner):
    def execute(self, intent: ActionIntent) -> Observation:
        raise RuntimeError(
            f"connection failed; {SENSITIVE_KEY_NAME}=visible-secret; "
            f"{REDACTION_MARKER}: another-secret; "
            f"path={SENSITIVE_LOCAL_PATH}"
        )


class CountingRunner(MockRunner):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, intent: ActionIntent) -> Observation:
        self.calls += 1
        return super().execute(intent)


def test_runner_timeout_becomes_execution_failure_and_replans() -> None:
    runner = GraphRunner(runner=TimeoutOnceRunner(), max_steps=2)

    state = runner.run("case-timeout-kind", "validate timeout")

    assert state["stage"] == "completed"
    assert state["replan_count"] == 1
    failed = runner.evidence_store.list_by_case("case-timeout-kind")[0]
    payload = failed.metadata["observation"]["payload"]
    assert payload["failure_kind"] == "execution_failed"
    assert payload["error_code"] == "runner_timeout"


def test_completed_tool_call_can_be_classified_as_test_failed() -> None:
    runner = GraphRunner(runner=FailedAssertionOnceRunner(), max_steps=2)

    state = runner.run("case-test-failure", "validate failed assertion")

    assert state["stage"] == "completed"
    assert state["replan_count"] == 1
    assert "test failure routed to replan" in runner.log


def test_runner_exception_message_redacts_common_credentials() -> None:
    runner = GraphRunner(runner=SensitiveFailureRunner(), max_steps=1)

    runner.run("case-redaction", "validate error redaction")

    failed = runner.evidence_store.list_by_case("case-redaction")[0]
    message = failed.metadata["observation"]["payload"]["error_message"]
    assert "visible-secret" not in message
    assert "another-secret" not in message
    assert SENSITIVE_LOCAL_PATH not in message
    assert message.count("[REDACTED]") == 2
    assert "[LOCAL_PATH]" in message


def test_policy_rejection_does_not_execute_runner_or_create_observation() -> None:
    counting_runner = CountingRunner()
    runner = GraphRunner(
        agent=MockAgent(tool_name="unknown.not_allowed"),
        runner=counting_runner,
    )

    state = runner.run("case-policy-rejected", "validate policy rejection")

    assert state["stage"] == "rejected"
    assert counting_runner.calls == 0
    assert state["latest_observation_id"] is None
    assert state["evidence_ids"] == []
