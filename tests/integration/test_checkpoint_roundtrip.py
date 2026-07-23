"""Checkpoint Envelope roundtrip integration tests."""

from __future__ import annotations

import json

import pytest

from industrial_test_agent.agent_runtime.graph import GraphRunner


def test_checkpoint_envelope_contains_version_state_evidence_and_metadata() -> None:
    runner = GraphRunner()
    paused = runner.run(
        "case-envelope",
        "validate Checkpoint Envelope",
        max_node_executions=5,
    )

    payload = json.loads(runner.checkpoint(paused))

    assert payload["checkpoint_version"] == "2.0"
    assert payload["metadata"]["case_id"] == "case-envelope"
    assert payload["graph_state"]["evidence_ids"]
    assert [item["evidence_id"] for item in payload["evidence_snapshot"]] == (
        payload["graph_state"]["evidence_ids"]
    )


@pytest.mark.parametrize("pause_after", range(9))
def test_checkpoint_roundtrip_at_every_runtime_boundary(pause_after: int) -> None:
    original = GraphRunner()
    paused = original.run(
        f"case-boundary-{pause_after}",
        "validate every recovery boundary",
        max_node_executions=pause_after,
    )

    restored = GraphRunner()
    state = restored.resume(original.checkpoint(paused))

    assert state["stage"] == "completed"
    assert all(
        restored.evidence_store.get(evidence_id) is not None
        for evidence_id in state["evidence_ids"]
    )
