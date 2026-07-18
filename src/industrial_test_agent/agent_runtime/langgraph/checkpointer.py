"""Simple JSON checkpoint persistence for LangGraph runtime."""

import json
from pathlib import Path
from typing import Any, Dict


class JsonCheckpointer:
    def __init__(self, directory: str = "checkpoints"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, checkpoint_id: str, payload: Dict[str, Any]) -> Path:
        path = self.directory / f"{checkpoint_id}.json"
        path.write_text(json.dumps(payload, indent=2))
        return path

    def load(self, checkpoint_id: str) -> Dict[str, Any]:
        path = self.directory / f"{checkpoint_id}.json"
        return json.loads(path.read_text())
