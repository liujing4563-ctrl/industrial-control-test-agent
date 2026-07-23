from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.policy.decisions import PolicyResult


@runtime_checkable
class PolicyValidatorProtocol(Protocol):
    """Validate one action using the shared PolicyResult contract."""

    def validate(
        self,
        case_state: CaseState,
        intent: ActionIntent,
        steps_taken: int = 0,
        remaining_call_budget: Optional[int] = None,
    ) -> PolicyResult:
        ...


PolicyEngineInterface = PolicyValidatorProtocol

__all__ = ["PolicyEngineInterface", "PolicyValidatorProtocol"]
