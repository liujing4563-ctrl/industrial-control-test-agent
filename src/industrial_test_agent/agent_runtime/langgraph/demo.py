from industrial_test_agent.agent_runtime.base import GraphContext
from industrial_test_agent.agent_runtime.langgraph.graph import GraphRunner, build_demo_graph
from industrial_test_agent.agent_runtime.state import CaseGraphState


def run_demo() -> GraphContext:
    state = CaseGraphState(case_id="case-001")
    context = GraphContext(state=state, history=[], metadata={})
    graph = build_demo_graph()
    runner = GraphRunner(nodes=graph, start_node="initialize_case")
    final_context = runner.run(context)
    return final_context


def main() -> None:
    final_context = run_demo()
    print("\n[demo] final stage=", final_context.state.stage)


if __name__ == "__main__":
    main()
