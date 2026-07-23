"""Evidence snapshot restore integration tests."""

from __future__ import annotations

from industrial_test_agent.agent_runtime.graph import GraphRunner


def test_fresh_store_resolves_every_restored_evidence_id() -> None:
    original = GraphRunner(required_evidence_count=3)
    completed = original.run("case-evidence-restore", "collect Evidence")
    checkpoint = original.checkpoint(completed)

    restored = GraphRunner()
    state = restored.resume(checkpoint)

    assert state["evidence_ids"] == completed["evidence_ids"]
    assert all(
        restored.evidence_store.get(evidence_id) is not None
        for evidence_id in state["evidence_ids"]
    )


def test_restored_nested_metadata_is_isolated_between_reads() -> None:
    original = GraphRunner()
    completed = original.run("case-isolated-restore", "restore Evidence")
    restored = GraphRunner()
    state = restored.resume(original.checkpoint(completed))
    evidence_id = state["evidence_ids"][0]

    first = restored.evidence_store.get(evidence_id)
    assert first is not None
    first.payload["data"]["all_clear"] = False

    second = restored.evidence_store.get(evidence_id)
    assert second is not None
    assert second.payload["data"]["all_clear"] is True
