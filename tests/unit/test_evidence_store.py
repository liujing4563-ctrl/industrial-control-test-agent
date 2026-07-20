"""Tests for append-only Evidence Store V0."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.evidence.in_memory_store import EvidenceStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store() -> EvidenceStore:
    return EvidenceStore()


def _obs(case_id: str = "case-001", obs_id: str = "obs-001") -> Observation:
    return Observation(
        observation_id=obs_id,
        case_id=case_id,
        source="test",
        source_type="mock",
        payload={"test": True},
        schema_id="observation",
        related_action_intent_id="act-001",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEvidenceStore:
    def test_append_from_observation(self, store):
        ev = store.append_from_observation(_obs())
        assert ev.evidence_id.startswith("ev-")
        assert ev.case_id == "case-001"

    def test_evidence_is_stored(self, store):
        ev = store.append_from_observation(_obs())
        retrieved = store.get(ev.evidence_id)
        assert retrieved is not None
        assert retrieved.evidence_id == ev.evidence_id

    def test_same_observation_is_appended_once(self, store):
        observation = _obs()
        first = store.append_from_observation(observation)
        second = store.append_from_observation(observation)

        assert second.evidence_id == first.evidence_id
        assert len(store.list_by_case(observation.case_id)) == 1

    def test_conflicting_replay_is_rejected(self, store):
        evidence = store.append_from_observation(_obs())
        conflicting = evidence.model_copy(update={"content_hash": "different"})

        with pytest.raises(ValueError, match="conflicts"):
            store.append_once(conflicting)

    def test_list_by_case(self, store):
        store.append_from_observation(_obs("case-A", "obs-A"))
        store.append_from_observation(_obs("case-A", "obs-B"))
        store.append_from_observation(_obs("case-B", "obs-C"))

        case_a = store.list_by_case("case-A")
        assert len(case_a) == 2

        case_b = store.list_by_case("case-B")
        assert len(case_b) == 1

    def test_duplicate_evidence_id_raises(self, store):
        ev = store.append_from_observation(_obs())
        with pytest.raises(ValueError, match="already exists"):
            store.append(ev)  # same evidence object → duplicate ID

    def test_evidence_is_immutable(self):
        ev = Evidence(
            evidence_id="ev-001",
            observation_id="obs-001",
            case_id="case-001",
            source="test",
            content_hash="abc123",
        )
        with pytest.raises(ValidationError):
            ev.evidence_id = "ev-002"

    def test_retrieved_metadata_cannot_mutate_stored_evidence(self, store):
        ev = store.append_from_observation(_obs())
        retrieved = store.get(ev.evidence_id)
        assert retrieved is not None
        retrieved.metadata["tampered"] = True

        stored_again = store.get(ev.evidence_id)
        assert stored_again is not None
        assert "tampered" not in stored_again.metadata

    def test_evidence_no_update_method(self, store):
        """Ensure EvidenceStore has no update/delete public API."""
        assert not hasattr(store, "update")
        assert not hasattr(store, "delete")
        assert not hasattr(store, "remove")

    def test_list_empty_case(self, store):
        assert store.list_by_case("nonexistent") == []

    def test_get_nonexistent(self, store):
        assert store.get("nonexistent") is None

    def test_snapshot_restore_is_idempotent(self, store):
        evidence = store.append_from_observation(_obs())
        restored = EvidenceStore()

        restored.restore_snapshot([evidence])
        restored.restore_snapshot([evidence])

        assert restored.get(evidence.evidence_id) == evidence
        assert len(restored.list_by_case(evidence.case_id)) == 1
