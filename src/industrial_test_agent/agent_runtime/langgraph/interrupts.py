"""Interrupt and approval support for LangGraph runtime."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InterruptSignal:
    reason: str
    case_id: str
    current_node: str
    approval_required: bool = False
    metadata: Optional[dict] = None
