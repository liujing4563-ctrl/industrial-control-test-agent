"""Safety tests for rejecting invalid or unsafe checkpoints."""

from __future__ import annotations

import json
from typing import Any

import pytest

from industrial_test_agent.agent_runtime.graph import GraphRunner


def _checkpoint_payload(*, pause_after: int = 3) -> dict[str, Any]:
    runner = GraphRunner()
    state = runner.run(
        "case-invalid-checkpoint",
        "validate checkpoint rejection",
        max_node_executions=pause_after,
    )
    return json.loads(runner.checkpoint(state))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("stage", "unknown-stage"),
        ("next_node", "unknown-node"),
    ],
)
def test_unknown_stage_or_node_is_rejected(field: str, value: str) -> None:
    payload = _checkpoint_payload()
    payload["graph_state"][field] = value

    with pytest.raises(ValueError):
        GraphRunner().resume(payload)


def test_invalid_stage_and_node_combination_is_rejected() -> None:
    payload = _checkpoint_payload()
    payload["graph_state"]["stage"] = "planning"
    payload["graph_state"]["next_node"] = "record_observation"

    with pytest.raises(ValueError, match="Invalid stage/next_node combination"):
        GraphRunner().resume(payload)


def test_non_terminal_state_without_next_node_is_rejected() -> None:
    payload = _checkpoint_payload()
    payload["graph_state"]["next_node"] = None

    with pytest.raises(ValueError, match="Non-terminal checkpoint"):
        GraphRunner().resume(payload)


def test_corrupted_json_is_rejected_with_clear_error() -> None:
    with pytest.raises(ValueError, match="Checkpoint JSON is invalid"):
        GraphRunner().resume('{"checkpoint_version":')


def test_unknown_checkpoint_version_is_rejected() -> None:
    payload = _checkpoint_payload()
    payload["checkpoint_version"] = "99.0"

    with pytest.raises(ValueError, match="Unsupported checkpoint version"):
        GraphRunner().resume(payload)


def test_missing_required_field_is_rejected() -> None:
    payload = _checkpoint_payload()
    payload["graph_state"].pop("remaining_steps")

    with pytest.raises(ValueError, match="remaining_steps"):
        GraphRunner().resume(payload)


def test_unknown_extra_field_is_rejected() -> None:
    payload = _checkpoint_payload()
    payload["unexpected"] = True

    with pytest.raises(ValueError, match="unexpected"):
        GraphRunner().resume(payload)


def test_terminal_state_without_reason_is_rejected() -> None:
    runner = GraphRunner()
    completed = runner.run("case-terminal", "validate terminal checkpoint")
    payload = json.loads(runner.checkpoint(completed))
    payload["graph_state"]["termination_reason"] = None

    with pytest.raises(ValueError, match="requires termination_reason"):
        GraphRunner().resume(payload)


def test_checkpoint_cannot_mark_observed_action_for_execution_again() -> None:
    payload = _checkpoint_payload(pause_after=4)
    payload["graph_state"]["stage"] = "validation"
    payload["graph_state"]["next_node"] = "execute_action"

    with pytest.raises(ValueError, match="would repeat an ActionIntent"):
        GraphRunner().resume(payload)


def test_observation_without_action_intent_is_rejected() -> None:
    payload = _checkpoint_payload(pause_after=4)
    payload["graph_state"]["active_action"] = None

    with pytest.raises(ValueError, match="active ActionIntent"):
        GraphRunner().resume(payload)
