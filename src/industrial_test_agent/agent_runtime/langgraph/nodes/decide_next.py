from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class DecideNextNode:
    name = "decide_next"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        status = "complete" if len(context.state.evidence_ids) >= 1 else "continue"
        print("[decide_next] decision=", status)
        if status == "complete":
            context.state.stage = "completed"
            return NodeExecutionResult(name=self.name, success=True, output={"decision": status}, next_node="finalize_case")
        return NodeExecutionResult(name=self.name, success=True, output={"decision": status}, next_node=None)


decide_next = DecideNextNode()
