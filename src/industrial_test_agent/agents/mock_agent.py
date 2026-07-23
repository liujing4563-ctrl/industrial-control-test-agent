"""Mock Agent V0 — generates a deterministic ActionIntent without LLM."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState


class MockAgent:
    """Deterministic agent that always proposes a safe PLC read."""

    DEFAULT_TOOL = "plc.read_interlock"
    DEFAULT_ARGS: Dict[str, Any] = {"group": "motor_start"}

    def __init__(
        self,
        tool_name: str = DEFAULT_TOOL,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.tool_name = tool_name
        self.arguments = arguments or dict(self.DEFAULT_ARGS)

    def propose(self, case_state: CaseState) -> ActionIntent:
        action_id = f"act-{uuid.uuid4().hex[:8]}"
        return ActionIntent(
            action_id=action_id,
            case_id=case_state.case_id,
            capability_id=self.tool_name,
            arguments=self.arguments,
            reason=f"Confirm {self.tool_name} status for case {case_state.case_id}",
            requested_by="mock_agent",
            created_at=datetime.now(timezone.utc),
            idempotency_key=f"{case_state.case_id}:{action_id}",
            metadata={"action_type": "test_request"},
        )
