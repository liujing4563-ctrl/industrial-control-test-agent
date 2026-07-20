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

    def test_demo_output_matches_m1_contract(self):
        from contextlib import redirect_stdout
        from io import StringIO

        output = StringIO()
        with redirect_stdout(output):
            main()

        text = output.getvalue()
        self.assertIn("case initialized", text)
        self.assertIn("action proposed: plc.read_interlock", text)
        self.assertIn("policy decision: allowed", text)
        self.assertIn("mock runner executed", text)
        self.assertIn("observation recorded", text)
        self.assertIn("evidence appended:", text)
        self.assertIn("case completed", text)


if __name__ == "__main__":
    unittest.main()
