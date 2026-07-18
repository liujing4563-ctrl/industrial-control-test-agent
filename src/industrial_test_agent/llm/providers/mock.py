from typing import Any, Dict

from industrial_test_agent.llm.provider import LLMProvider


class MockLLMProvider(LLMProvider):
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "prompt": prompt,
            "output": {
                "tool_capability": "plc.read_interlock",
                "arguments": {"group": "motor_start"},
                "purpose": "排除互锁阻塞",
                "expected_information": ["all_clear", "estop_active", "overload_active"],
            },
        }
