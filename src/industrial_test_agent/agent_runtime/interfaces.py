from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.agent_runtime.base import GraphContext


class AgentRuntimeInterface(Protocol):
    def run(self, context: GraphContext) -> GraphContext:
        ...


class CheckpointerInterface(ABC):
    @abstractmethod
    def save(self, context: GraphContext) -> str:
        raise NotImplementedError

    @abstractmethod
    def load(self, checkpoint_id: str) -> GraphContext:
        raise NotImplementedError
