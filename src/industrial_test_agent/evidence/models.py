from pydantic import BaseModel

from industrial_test_agent.domain.evidence import Evidence


class EvidenceMetadata(BaseModel):
    created_by: str
    source: str
    tags: list[str] = []


class EvidenceRecord(Evidence):
    metadata: EvidenceMetadata
