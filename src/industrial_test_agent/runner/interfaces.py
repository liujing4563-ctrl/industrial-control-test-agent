from __future__ import annotations

from typing import Protocol, runtime_checkable

from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.observation import Observation


@runtime_checkable
class Runner(Protocol):
    """Execute one validated action and return the canonical Observation."""

    def execute(self, action_intent: ActionIntent) -> Observation:
        ...


RunnerInterface = Runner

__all__ = ["Runner", "RunnerInterface"]
