import unittest

import industrial_test_agent.agent_runtime.interfaces
import industrial_test_agent.agents.base
import industrial_test_agent.policy.interfaces
import industrial_test_agent.runner.interfaces
import industrial_test_agent.evidence.interfaces
import industrial_test_agent.mcp.gateway.interfaces


class TestImports(unittest.TestCase):
    def test_interfaces_import(self):
        self.assertIsNotNone(industrial_test_agent.agent_runtime.interfaces)
        self.assertIsNotNone(industrial_test_agent.agents.base)
        self.assertIsNotNone(industrial_test_agent.policy.interfaces)
        self.assertIsNotNone(industrial_test_agent.runner.interfaces)
        self.assertIsNotNone(industrial_test_agent.evidence.interfaces)
        self.assertIsNotNone(industrial_test_agent.mcp.gateway.interfaces)


if __name__ == "__main__":
    unittest.main()
