"""Append-only in-memory Evidence Store V0."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append_from_observation(self, obs: Observation) -> Evidence:
        """Create an immutable Evidence record from an Observation."""
        content = obs.model_dump_json()
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        evidence = Evidence(
            evidence_id=f"ev-{uuid.uuid4().hex[:8]}",
            observation_id=obs.observation_id,
            case_id=obs.case_id,
            source=obs.source,
            content_hash=content_hash,
            metadata={"observation": obs.model_dump()},
            created_at=datetime.now(timezone.utc),
        )

        self.append(evidence)
        return evidence

    def append(self, evidence: Evidence) -> None:
        """Append a single Evidence record (idempotent check on evidence_id)."""
        if evidence.evidence_id in self._store:
            raise ValueError(
                f"Evidence {evidence.evidence_id} already exists (append-only store)"
            )
        self._store[evidence.evidence_id] = evidence.model_dump_json()
        self._by_case.setdefault(evidence.case_id, []).append(evidence.evidence_id)

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

    # ------------------------------------------------------------------
    # Safety: no update / delete methods exposed
    # ------------------------------------------------------------------
