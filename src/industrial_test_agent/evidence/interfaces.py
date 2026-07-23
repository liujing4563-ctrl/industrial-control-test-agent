from __future__ import annotations

from typing import Iterable, Optional, Protocol, runtime_checkable

from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.domain.observation import Observation


@runtime_checkable
class EvidenceStoreProtocol(Protocol):
    """Append-only Evidence operations required by the Runtime."""

    def append_from_observation(self, observation: Observation) -> Evidence:
        ...

    def append(self, evidence: Evidence) -> None:
        ...

    def append_once(self, evidence: Evidence) -> Evidence:
        ...

    def snapshot(self, case_id: str) -> list[Evidence]:
        ...

    def restore(self, evidences: Iterable[Evidence]) -> None:
        ...

    def restore_snapshot(self, evidences: Iterable[Evidence]) -> None:
        ...

    def get(self, evidence_id: str) -> Optional[Evidence]:
        ...

    def list_by_case(self, case_id: str) -> list[Evidence]:
        ...


EvidenceStoreInterface = EvidenceStoreProtocol

__all__ = ["EvidenceStoreInterface", "EvidenceStoreProtocol"]
