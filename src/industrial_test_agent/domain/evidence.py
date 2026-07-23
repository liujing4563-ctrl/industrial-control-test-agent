from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import ConfigDict, Field

from industrial_test_agent.contracts import ContractModel


class Evidence(ContractModel):
    evidence_id: str = Field(min_length=1)
    idempotency_key: Optional[str] = None
    observation_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    source: str
    content_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(extra="forbid", frozen=True)
