import unittest

from industrial_test_agent.agent_runtime.langgraph.demo import run_demo


class TestLangGraphRuntime(unittest.TestCase):
    def test_demo_runs_to_completion(self):
        context = run_demo()
        self.assertEqual(context.state.stage, "completed")
        self.assertTrue(len(context.history) >= 1)
        self.assertEqual(context.history[-1].name, "finalize_case")


if __name__ == "__main__":
    unittest.main()
