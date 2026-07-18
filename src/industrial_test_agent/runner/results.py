from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RunnerResult:
    success: bool
    details: Dict[str, Any]
    output: Dict[str, Any] = None
