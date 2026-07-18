from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ActionIntentCommand:
    intent_id: str
    case_id: str
    action_type: str
    action_details: Dict[str, object]
    reason: str
    requested_by: str
    priority: str = "medium"
    target_resource: Optional[str] = None


@dataclass
class ApprovalCommand:
    approval_id: str
    case_id: str
    requested_by: str
    action_intent_id: str
    reason: str
    suggested_resolution: Optional[str] = None
