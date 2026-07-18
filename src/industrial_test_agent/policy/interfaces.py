from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState


class PolicyDecision(str):
    allowed = "allowed"
    rejected = "rejected"
    approval_required = "approval_required"


class PolicyEngineInterface(Protocol):
    def evaluate(self, case_state: CaseState, intent: ActionIntent) -> str:
        ...


class PolicyStore(ABC):
    @abstractmethod
    def load_policy(self, policy_id: str) -> dict:
        raise NotImplementedError
