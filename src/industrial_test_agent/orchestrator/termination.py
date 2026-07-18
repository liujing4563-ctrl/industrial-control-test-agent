from typing import Any, Dict


def evaluate_termination(status: str, metrics: Dict[str, Any]) -> bool:
    return status in {"completed", "escalated"}
