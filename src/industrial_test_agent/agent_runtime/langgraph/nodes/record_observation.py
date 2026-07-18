from industrial_test_agent.agent_runtime.base import GraphContext, NodeExecutionResult


class RecordObservationNode:
    name = "record_observation"

    def execute(self, context: GraphContext) -> NodeExecutionResult:
        observation_id = f"obs-{len(context.state.evidence_ids):03d}"
        print("[record_observation] evidence_id=", observation_id)
        context.state.latest_observation_id = observation_id
        return NodeExecutionResult(name=self.name, success=True, output={"observation_id": observation_id}, next_node="decide_next")


record_observation = RecordObservationNode()
