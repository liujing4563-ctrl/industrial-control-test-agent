from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionResult:
    action_intent_id: str
    success: bool
    details: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None


@dataclass
class ObservationRecord:
    observation_id: str
    case_id: str
    source: str
    payload: Dict[str, Any]
    schema_id: str
    related_action_intent_id: Optional[str] = None
