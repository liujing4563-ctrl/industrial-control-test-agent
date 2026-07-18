from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class MockExecuteNode:
    name = "mock_execute"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        print("[mock_execute] result=all_clear")
        context.state.evidence_ids.append("ev-001")
        return NodeExecutionResult(name=self.name, success=True, output={"result": "all_clear"}, next_node="record_observation")


mock_execute = MockExecuteNode()
