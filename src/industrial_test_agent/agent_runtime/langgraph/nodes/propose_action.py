from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class ProposeActionNode:
    name = "propose_action"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        context.state.proposed_action_id = "action-001"
        print("[propose_action] tool=plc.read_interlock")
        return NodeExecutionResult(
            name=self.name,
            success=True,
            output={"action_intent_id": context.state.proposed_action_id},
            next_node="policy_validate",
        )


propose_action = ProposeActionNode()
