from __future__ import annotations

from typing import Dict, List

from industrial_test_agent.agent_runtime.base import GraphContext, GraphNode, NodeExecutionResult
from industrial_test_agent.agent_runtime.state import CaseGraphState


class GraphRunner:
    def __init__(self, nodes: Dict[str, GraphNode], start_node: str):
        self.nodes = nodes
        self.current_node = start_node

    def run(self, context: GraphContext) -> GraphContext:
        while self.current_node is not None:
            node = self.nodes[self.current_node]
            result = node.execute(context)
            context.history.append(result)

            if result.interrupt:
                context.metadata["interrupted_at"] = self.current_node
                break

            self.current_node = result.next_node

        return context


def build_demo_graph() -> Dict[str, GraphNode]:
    from industrial_test_agent.agent_runtime.langgraph.nodes import (
        decide_next,
        finalize_case,
        initialize_case,
        mock_execute,
        policy_validate,
        propose_action,
        record_observation,
    )

    return {
        initialize_case.name: initialize_case,
        propose_action.name: propose_action,
        policy_validate.name: policy_validate,
        mock_execute.name: mock_execute,
        record_observation.name: record_observation,
        decide_next.name: decide_next,
        finalize_case.name: finalize_case,
    }
