import json

import pytest

from industrial_test_agent.agent_runtime.checkpoint import (
    CHECKPOINT_VERSION,
    CheckpointEnvelope,
)
from industrial_test_agent.agent_runtime.graph import GraphRunner


def test_checkpoint_envelope_json_roundtrip() -> None:
    runtime = GraphRunner()
    state = runtime.run(
        "case-v2",
        "validate canonical checkpoint",
        max_node_executions=5,
    )
    checkpoint = runtime.checkpoint(state)
    envelope = CheckpointEnvelope.model_validate_json(checkpoint)

    assert envelope.checkpoint_version == CHECKPOINT_VERSION
    assert CheckpointEnvelope.model_validate_json(
        envelope.model_dump_json()
    ) == envelope


def test_v1_checkpoint_is_migrated_and_resumed() -> None:
    legacy = {
        "checkpoint_version": "1.0",
        "graph_state": {
            "case_id": "case-v1",
            "goal": "validate legacy checkpoint",
            "stage": "validation",
            "proposed_action_id": "act-v1",
            "proposed_action": {
                "intent_id": "act-v1",
                "case_id": "case-v1",
                "action_type": "test_request",
                "action_details": {
                    "tool_capability": "plc.read_interlock",
                    "arguments": {"group": "motor_start"},
                },
                "reason": "legacy fixture",
                "requested_by": "legacy-test",
            },
            "latest_observation_id": None,
            "latest_observation": None,
            "evidence_ids": [],
            "hypothesis_ids": [],
            "remaining_steps": 20,
            "replan_count": 0,
            "last_execution_success": None,
            "termination_reason": None,
            "policy_decision": "allowed",
            "policy_reason": "legacy allowed",
            "next_node": "execute_action",
        },
        "evidence_snapshot": [],
        "metadata": {"case_id": "case-v1"},
    }

    resumed = GraphRunner().resume(legacy)

    assert resumed.stage == "completed"
    assert len(resumed.evidence_ids) == 1


def test_unknown_checkpoint_version_is_rejected() -> None:
    runtime = GraphRunner()
    state = runtime.run("case-version", "reject unknown version")
    payload = json.loads(runtime.checkpoint(state))
    payload["checkpoint_version"] = "99.0"

    with pytest.raises(ValueError, match="Unsupported checkpoint version"):
        GraphRunner().resume(payload)
