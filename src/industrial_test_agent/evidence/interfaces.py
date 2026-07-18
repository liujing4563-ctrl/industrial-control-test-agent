from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.domain.evidence import Evidence


class EvidenceStoreInterface(Protocol):
    def append(self, evidence: Evidence) -> None:
        ...

    def query(self, case_id: str) -> list[Evidence]:
        ...


class EvidenceRepository(ABC):
    @abstractmethod
    def save(self, evidence: Evidence) -> None:
        raise NotImplementedError
