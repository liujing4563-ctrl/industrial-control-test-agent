from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.domain.action_intent import ActionIntent


class RunnerInterface(Protocol):
    def execute(self, action_intent: ActionIntent) -> "RunnerResult":
        ...


class RunnerResult(ABC):
    @abstractmethod
    def is_success(self) -> bool:
        raise NotImplementedError
