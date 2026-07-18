from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class InitializeCaseNode:
    name = "initialize_case"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        context.state.stage = "planning"
        context.state.goal = "Identify failure root cause and validate test coverage"
        print("[initialize_case] case_id=", context.state.case_id)
        return NodeExecutionResult(name=self.name, success=True, output={}, next_node="propose_action")


initialize_case = InitializeCaseNode()
