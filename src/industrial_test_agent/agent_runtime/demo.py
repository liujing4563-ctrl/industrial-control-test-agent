"""Demo — run the minimal Agent Runtime V0 end-to-end."""

from __future__ import annotations

from industrial_test_agent.agent_runtime.graph import GraphRunner


def main() -> None:
    runner = GraphRunner()
    state = runner.run(case_id="case-001", goal="验证电机启动互锁条件")

    print("\n".join(runner.log))
    print(f"\nfinal state: stage={state['stage']}, reason={state['termination_reason']}")
    print(f"evidence count: {len(state['evidence_ids'])}")


if __name__ == "__main__":
    main()
