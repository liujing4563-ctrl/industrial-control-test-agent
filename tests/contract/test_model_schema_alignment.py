import json
from pathlib import Path

from industrial_test_agent.schemas.generate import find_schema_drift
from industrial_test_agent.schemas.registry import SCHEMA_MODELS


SCHEMA_DIR = Path("schemas")


def test_all_canonical_models_have_repository_schemas() -> None:
    expected = {
        "action-intent.schema.json",
        "observation.schema.json",
        "evidence.schema.json",
        "case-state.schema.json",
        "hypothesis.schema.json",
        "finding.schema.json",
        "tool-capability.schema.json",
        "capability-pack.schema.json",
        "checkpoint-envelope.schema.json",
    }
    assert set(SCHEMA_MODELS) == expected
    assert {path.name for path in SCHEMA_DIR.glob("*.json")} == expected


def test_repository_schemas_match_pydantic_models() -> None:
    assert find_schema_drift(SCHEMA_DIR) == []


def test_schema_titles_and_ids_are_stable() -> None:
    for filename, model in SCHEMA_MODELS.items():
        schema = model.model_json_schema()
        assert schema["title"] == model.__name__
        repository_schema = json.loads(
            (SCHEMA_DIR / filename).read_text(encoding="utf-8")
        )
        assert repository_schema["title"] == model.__name__
        assert repository_schema["$id"].startswith(
            "urn:industrial-test-agent:schema:"
        )
