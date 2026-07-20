from dataclasses import dataclass, field
from typing import Any, Dict, Literal


PolicyDecision = Literal["allowed", "rejected", "approval_required"]


@dataclass
class PolicyResult:
    decision: PolicyDecision
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


def default_policy_result() -> PolicyResult:
    return PolicyResult(decision="allowed", reason="default allow", details={})
