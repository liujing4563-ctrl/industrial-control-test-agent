from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class PolicyResult:
    decision: str
    reason: str
    details: Dict[str, Any] = None


def default_policy_result() -> PolicyResult:
    return PolicyResult(decision="allowed", reason="default allow", details={})
