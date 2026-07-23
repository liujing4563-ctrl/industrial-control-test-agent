"""Public protocols for Runtime execution and checkpoint persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Protocol, runtime_checkable

from industrial_test_agent.agent_runtime.checkpoint import CheckpointEnvelope
from industrial_test_agent.agent_runtime.state import CaseGraphState


@runtime_checkable
class AgentRuntime(Protocol):
    def run(
        self,
        case_id: str,
        goal: str,
        *,
        max_node_executions: Optional[int] = None,
    ) -> CaseGraphState:
        ...

    def resume(
        self,
        checkpoint: str | Mapping[str, Any],
        *,
        max_node_executions: Optional[int] = None,
    ) -> CaseGraphState:
        ...

    def checkpoint(self, state: CaseGraphState) -> str:
        ...


@runtime_checkable
class Checkpointer(Protocol):
    def save(
        self,
        checkpoint_id: str,
        envelope: CheckpointEnvelope,
    ) -> Path:
        ...

    def load(self, checkpoint_id: str) -> CheckpointEnvelope:
        ...


AgentRuntimeInterface = AgentRuntime
CheckpointerInterface = Checkpointer

__all__ = [
    "AgentRuntime",
    "AgentRuntimeInterface",
    "Checkpointer",
    "CheckpointerInterface",
]
