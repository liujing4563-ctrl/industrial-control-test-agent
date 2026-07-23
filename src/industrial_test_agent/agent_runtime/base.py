from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol

if TYPE_CHECKING:
    from industrial_test_agent.agent_runtime.state import CaseGraphState


@dataclass
class NodeExecutionResult:
    name: str
    success: bool
    output: Dict[str, Any]
    next_node: Optional[str] = None
    interrupt: bool = False


@dataclass
class GraphContext:
    state: "CaseGraphState"
    history: List[NodeExecutionResult]
    metadata: Dict[str, Any]


class GraphNode(Protocol):
    name: str

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        ...


class AgentRuntime(Protocol):
    def run(self, context: GraphContext) -> GraphContext:
        ...
