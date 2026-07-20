"""Append-only in-memory Evidence Store V0."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.domain.observation import Observation


class EvidenceStore:
    """Append-only evidence repository.

    Constraints:
    - Evidence can only be appended (no update/delete).
    - Evidence ID must be unique within a case.
    - Agents must not write raw Evidence fields directly.
    """

    def __init__(self) -> None:
        self._store: Dict[str, str] = {}
        self._by_case: Dict[str, List[str]] = {}
        self._by_idempotency_key: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append_from_observation(self, obs: Observation) -> Evidence:
        """Create an immutable Evidence record from an Observation."""
        content = obs.model_dump_json()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        idempotency_key = (
            f"{obs.case_id}:{obs.observation_id}:tool-observation"
        )
        evidence_id = f"ev-{hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]}"

        evidence = Evidence(
            evidence_id=evidence_id,
            idempotency_key=idempotency_key,
            observation_id=obs.observation_id,
            case_id=obs.case_id,
            source=obs.source,
            content_hash=content_hash,
            metadata={"observation": obs.model_dump(mode="json")},
            created_at=datetime.now(timezone.utc),
        )

        return self.append_once(evidence)

    def append(self, evidence: Evidence) -> None:
        """Append a single Evidence record and reject every duplicate."""
        if evidence.evidence_id in self._store:
            raise ValueError(
                f"Evidence {evidence.evidence_id} already exists (append-only store)"
            )
        if (
            evidence.idempotency_key is not None
            and evidence.idempotency_key in self._by_idempotency_key
        ):
            raise ValueError(
                f"Evidence idempotency key {evidence.idempotency_key} already exists"
            )

        self._store[evidence.evidence_id] = evidence.model_dump_json()
        self._by_case.setdefault(evidence.case_id, []).append(evidence.evidence_id)
        if evidence.idempotency_key is not None:
            self._by_idempotency_key[evidence.idempotency_key] = evidence.evidence_id

    def append_once(self, evidence: Evidence) -> Evidence:
        """Append once, returning an identical record during recovery replay."""
        existing_id = None
        if evidence.idempotency_key is not None:
            existing_id = self._by_idempotency_key.get(evidence.idempotency_key)
        if existing_id is None and evidence.evidence_id in self._store:
            existing_id = evidence.evidence_id

        if existing_id is not None:
            existing = self.get(existing_id)
            if existing is None:
                raise RuntimeError(f"Evidence index is corrupted for {existing_id}")
            if not self._same_content(existing, evidence):
                raise ValueError(
                    "Evidence replay conflicts with the existing append-only record"
                )
            return existing

        self.append(evidence)
        return evidence

    def restore_snapshot(self, evidences: Iterable[Evidence]) -> None:
        """Restore a validated checkpoint snapshot without duplicating records."""
        records = list(evidences)

        # Check every record before mutating the append-only store.
        for evidence in records:
            existing_id = None
            if evidence.idempotency_key is not None:
                existing_id = self._by_idempotency_key.get(evidence.idempotency_key)
            if existing_id is None and evidence.evidence_id in self._store:
                existing_id = evidence.evidence_id
            if existing_id is None:
                continue

            existing = self.get(existing_id)
            if existing is None or not self._same_content(existing, evidence):
                raise ValueError(
                    "Checkpoint Evidence conflicts with the existing append-only store"
                )

        for evidence in records:
            self.append_once(evidence)

    def get(self, evidence_id: str) -> Optional[Evidence]:
        """Retrieve a single Evidence by ID."""
        payload = self._store.get(evidence_id)
        if payload is None:
            return None
        return Evidence.model_validate_json(payload)

    def list_by_case(self, case_id: str) -> List[Evidence]:
        """Return all Evidence records for a case, in insertion order."""
        ids = self._by_case.get(case_id, [])
        return [
            Evidence.model_validate_json(self._store[eid])
            for eid in ids
            if eid in self._store
        ]

    @staticmethod
    def _same_content(left: Evidence, right: Evidence) -> bool:
        """Compare immutable record content, excluding insertion time."""
        fields = (
            "evidence_id",
            "idempotency_key",
            "observation_id",
            "case_id",
            "source",
            "content_hash",
            "metadata",
        )
        return all(getattr(left, field) == getattr(right, field) for field in fields)

    # ------------------------------------------------------------------
    # Safety: no update / delete methods exposed
    # ------------------------------------------------------------------
