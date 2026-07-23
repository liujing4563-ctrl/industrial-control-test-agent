from typing import Any, Literal

from pydantic import ConfigDict, Field

from industrial_test_agent.contracts import ContractModel


PolicyDecision = Literal["allowed", "rejected", "approval_required"]


class PolicyResult(ContractModel):
    decision: PolicyDecision
    reason: str
    details: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", frozen=True)


def default_policy_result() -> PolicyResult:
    return PolicyResult(decision="allowed", reason="default allow", details={})
