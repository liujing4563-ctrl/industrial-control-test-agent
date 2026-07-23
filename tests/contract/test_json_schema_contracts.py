from pathlib import Path

import pytest
from pydantic import ValidationError

from industrial_test_agent.contracts.json_schema import (
    SCHEMA_MODELS,
    find_schema_drift,
)
from industrial_test_agent.domain.action_intent import ActionIntent


SCHEMA_DIR = Path("schemas")


def test_checked_in_json_schemas_match_pydantic_models() -> None:
    assert find_schema_drift(SCHEMA_DIR) == []


def test_schema_registry_owns_every_checked_in_schema() -> None:
    checked_in = {path.name for path in SCHEMA_DIR.glob("*.json")}
    assert checked_in == set(SCHEMA_MODELS)


def test_generated_contracts_use_snake_case() -> None:
    for model in SCHEMA_MODELS.values():
        properties = model.model_json_schema().get("properties", {})
        assert all(name == name.lower() for name in properties)
        assert all("-" not in name for name in properties)


def test_camel_case_payload_is_not_accepted_as_action_intent() -> None:
    with pytest.raises(ValidationError):
        ActionIntent.model_validate(
            {
                "intentId": "intent-001",
                "caseId": "case-001",
                "actionType": "probe",
                "actionDetails": {},
                "reason": "test",
                "requestedBy": "contract-test",
            }
        )
