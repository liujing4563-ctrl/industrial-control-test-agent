"""Mock Test Runner V0 — returns deterministic Observations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import (
    Observation,
    ObservationSourceType,
    ObservationStatus,
)


class MockRunner:
    """Simulates three PLC tools and returns uniform Observations."""

    SUPPORTED_TOOLS = {
        "plc.read_interlock",
        "plc.read_signal",
        "plc.wait_feedback",
    }

    def execute(self, intent: ActionIntent) -> Observation:
        tool_name = intent.capability_id
        arguments = intent.arguments

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
            action_id=intent.action_id,
            tool_id=tool_name,
            status=ObservationStatus.SUCCEEDED,
            success=True,
            data=data,
            received_at=datetime.now(timezone.utc),
            source_type=ObservationSourceType.MOCK,
            metadata={
                "source": "mock_runner",
                "schema_id": "observation",
            },
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
            action_id=intent.action_id,
            tool_id=intent.capability_id,
            status=ObservationStatus.EXECUTION_FAILED,
            success=False,
            error_code="unsupported_tool",
            error_message=message,
            received_at=datetime.now(timezone.utc),
            source_type=ObservationSourceType.MOCK,
            metadata={
                "source": "mock_runner",
                "schema_id": "observation",
            },
        )
