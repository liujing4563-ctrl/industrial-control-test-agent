"""Mock Test Runner V0 — returns deterministic Observations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation


class MockRunner:
    """Simulates three PLC tools and returns uniform Observations."""

    SUPPORTED_TOOLS = {
        "plc.read_interlock",
        "plc.read_signal",
        "plc.wait_feedback",
    }

    def execute(self, intent: ActionIntent) -> Observation:
        tool_name = intent.action_details.get("tool_capability", "unknown")
        arguments = intent.action_details.get("arguments", {})

        if tool_name not in self.SUPPORTED_TOOLS:
            return self._error_obs(intent, f"Unsupported tool: {tool_name}")

        handler = getattr(self, f"_handle_{tool_name.replace('.', '_')}", None)
        if handler:
            data = handler(arguments)
        else:
            data = {"result": "ok"}

        obs_id = f"obs-{uuid.uuid4().hex[:8]}"
        return Observation(
            observation_id=obs_id,
            case_id=intent.case_id,
            source="mock_runner",
            source_type="mock",
            payload={
                "action_id": intent.intent_id,
                "success": True,
                "status": "completed",
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            schema_id="observation",
            related_action_intent_id=intent.intent_id,
        )

    # ---- tool-specific handlers ----

    @staticmethod
    def _handle_plc_read_interlock(args: Dict[str, Any]) -> Dict[str, Any]:
        group = args.get("group", "default")
        return {
            "tool": "plc.read_interlock",
            "group": group,
            "all_clear": True,
            "interlocks": {
                "estop": "ok",
                "guard_door": "ok",
                "thermal": "ok",
            },
        }

    @staticmethod
    def _handle_plc_read_signal(args: Dict[str, Any]) -> Dict[str, Any]:
        signal = args.get("signal_name", "unknown")
        return {
            "tool": "plc.read_signal",
            "signal": signal,
            "value": True,
        }

    @staticmethod
    def _handle_plc_wait_feedback(args: Dict[str, Any]) -> Dict[str, Any]:
        feedback = args.get("feedback_name", "unknown")
        return {
            "tool": "plc.wait_feedback",
            "feedback": feedback,
            "received": True,
            "latency_ms": 42,
        }

    @staticmethod
    def _error_obs(intent: ActionIntent, message: str) -> Observation:
        obs_id = f"obs-{uuid.uuid4().hex[:8]}"
        return Observation(
            observation_id=obs_id,
            case_id=intent.case_id,
            source="mock_runner",
            source_type="mock",
            payload={
                "action_id": intent.intent_id,
                "success": False,
                "status": "error",
                "error": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            schema_id="observation",
            related_action_intent_id=intent.intent_id,
        )
