"""Append-only Evidence contracts and storage."""

from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.evidence.in_memory_store import EvidenceStore
from industrial_test_agent.evidence.interfaces import (
    EvidenceStoreInterface,
    EvidenceStoreProtocol,
)

__all__ = [
    "Evidence",
    "EvidenceStore",
    "EvidenceStoreInterface",
    "EvidenceStoreProtocol",
]
