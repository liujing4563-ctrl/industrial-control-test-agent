from pathlib import Path

from industrial_test_agent.schemas.generate import write_schema_documents


def _snapshot(directory: Path) -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(directory.glob("*.json"))
    }


def test_schema_generation_is_idempotent(tmp_path: Path) -> None:
    write_schema_documents(tmp_path)
    first = _snapshot(tmp_path)

    write_schema_documents(tmp_path)
    second = _snapshot(tmp_path)

    assert first
    assert second == first
