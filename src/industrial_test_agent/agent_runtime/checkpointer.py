"""Validated JSON persistence for CheckpointEnvelope."""

from pathlib import Path

from industrial_test_agent.agent_runtime.checkpoint import CheckpointEnvelope


class JsonCheckpointer:
    def __init__(self, directory: str | Path = "checkpoints") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        checkpoint_id: str,
        envelope: CheckpointEnvelope,
    ) -> Path:
        path = self._path_for(checkpoint_id)
        path.write_text(envelope.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, checkpoint_id: str) -> CheckpointEnvelope:
        path = self._path_for(checkpoint_id)
        return CheckpointEnvelope.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def _path_for(self, checkpoint_id: str) -> Path:
        if not checkpoint_id or Path(checkpoint_id).name != checkpoint_id:
            raise ValueError("checkpoint_id must be a non-empty file name")
        return self.directory / f"{checkpoint_id}.json"
