from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.mcp.models import MCPRegistration


class MCPGatewayInterface(Protocol):
    def invoke(self, registration: MCPRegistration, action_intent: ActionIntent) -> dict:
        ...


class MCPRegistry(ABC):
    @abstractmethod
    def register(self, registration: MCPRegistration) -> None:
        raise NotImplementedError
