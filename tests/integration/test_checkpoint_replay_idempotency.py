"""Checkpoint replay idempotency integration tests."""

from __future__ import annotations

import json

from industrial_test_agent.agent_runtime.graph import GraphRunner


def test_repeated_checkpoint_resume_reuses_original_evidence() -> None:
    runner = GraphRunner()
    paused = runner.run(
        "case-repeat-resume",
        "validate repeated recovery",
        max_node_executions=4,
    )
    checkpoint = runner.checkpoint(paused)

    first = runner.resume(checkpoint)
    second = runner.resume(checkpoint)

    assert first["evidence_ids"] == second["evidence_ids"]
    assert len(runner.evidence_store.list_by_case("case-repeat-resume")) == 1


def test_short_lived_m1_envelope_format_remains_recoverable() -> None:
    runner = GraphRunner()
    paused = runner.run(
        "case-legacy-envelope",
        "validate legacy Envelope migration",
        max_node_executions=4,
    )
    payload = json.loads(runner.checkpoint(paused))
    case_id = payload.pop("metadata")["case_id"]
    payload.pop("checkpoint_version")
    payload["checkpoint_metadata"] = {
        "format_version": 1,
        "case_id": case_id,
    }

    state = GraphRunner().resume(payload)

    assert state["stage"] == "completed"
    assert state["case_id"] == "case-legacy-envelope"
