from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState


class BaseAgent(ABC):
    @abstractmethod
    def decide(self, case_state: CaseState) -> ActionIntent:
        raise NotImplementedError


class ExecutiveAgent(BaseAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        raise NotImplementedError


class SpecialistAgent(BaseAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        raise NotImplementedError


class CriticAgent(BaseAgent):
    def decide(self, case_state: CaseState) -> ActionIntent:
        raise NotImplementedError
