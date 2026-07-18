from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class PolicyValidateNode:
    name = "policy_validate"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        print("[policy_validate] decision=allowed")
        return NodeExecutionResult(name=self.name, success=True, output={}, next_node="mock_execute")


policy_validate = PolicyValidateNode()
