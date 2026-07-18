from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.domain.case_state import CaseState


class WorkflowEngine(Protocol):
    def start_case(self, case_state: CaseState) -> CaseState:
        ...

    def advance(self, case_state: CaseState, action_intent_id: str) -> CaseState:
        ...


class OrchestratorBase(ABC):
    @abstractmethod
    def execute_transition(self, case_state: CaseState) -> CaseState:
        raise NotImplementedError
