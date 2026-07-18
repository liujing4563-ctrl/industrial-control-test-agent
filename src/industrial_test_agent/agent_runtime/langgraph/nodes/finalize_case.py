from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class FinalizeCaseNode:
    name = "finalize_case"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        context.state.stage = "completed"
        print("[finalize_case] status=completed")
        return NodeExecutionResult(name=self.name, success=True, output={"status": "completed"}, next_node=None)


finalize_case = FinalizeCaseNode()
