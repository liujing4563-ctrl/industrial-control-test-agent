from typing import Any

from pydantic import ConfigDict, Field

from industrial_test_agent.contracts import ContractModel
from industrial_test_agent.domain.enums import PolicyDecision


class PolicyResult(ContractModel):
    decision: PolicyDecision
    reason: str
    details: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", frozen=True)


def default_policy_result() -> PolicyResult:
    return PolicyResult(decision="allowed", reason="default allow", details={})
