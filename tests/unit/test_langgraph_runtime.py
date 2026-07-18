"""Tests for the LangGraph-inspired Agent Runtime demo."""

import unittest

from industrial_test_agent.agent_runtime.demo import main
from industrial_test_agent.agent_runtime.graph import GraphRunner


class TestLangGraphRuntime(unittest.TestCase):
    def test_demo_runs_to_completion(self):
        runner = GraphRunner()
        state = runner.run("case-001", "test goal")
        self.assertEqual(state["stage"], "completed")
        self.assertGreaterEqual(len(state["evidence_ids"]), 1)
        self.assertIn("case completed", runner.log[-1])


if __name__ == "__main__":
    unittest.main()
