from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from industrial_test_agent.domain import (
    ActionIntent,
    CaseState,
    Evidence,
    Finding,
    Hypothesis,
    Observation,
)
from industrial_test_agent.mcp.models import ToolCapability


def test_core_models_json_roundtrip(
    action: ActionIntent,
    observation: Observation,
    evidence: Evidence,
    case_state: CaseState,
    hypothesis: Hypothesis,
    finding: Finding,
    capability: ToolCapability,
) -> None:
    for model in (
        action,
        observation,
        evidence,
        case_state,
        hypothesis,
        finding,
        capability,
    ):
        restored = type(model).model_validate_json(model.model_dump_json())
        assert restored == model


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_hypothesis_confidence_out_of_range_is_rejected(
    hypothesis: Hypothesis,
    confidence: float,
) -> None:
    payload = hypothesis.model_dump(mode="python")
    payload["confidence"] = confidence
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(payload)


def test_invalid_enums_are_rejected(
    action: ActionIntent,
    observation: Observation,
    finding: Finding,
    capability: ToolCapability,
) -> None:
    invalid_payloads = [
        (ActionIntent, action.model_dump() | {"risk_level": "none"}),
        (Observation, observation.model_dump() | {"status": "ok"}),
        (Finding, finding.model_dump() | {"severity": "urgent"}),
        (
            ToolCapability,
            capability.model_dump() | {"side_effect_type": "unknown"},
        ),
    ]
    for model_type, payload in invalid_payloads:
        with pytest.raises(ValidationError):
            model_type.model_validate(payload)


@pytest.mark.parametrize(
    ("model_fixture", "field_name"),
    [
        ("action", "created_at"),
        ("observation", "received_at"),
        ("evidence", "created_at"),
        ("case_state", "created_at"),
        ("hypothesis", "created_at"),
        ("finding", "created_at"),
    ],
)
def test_naive_datetime_is_rejected(
    request: pytest.FixtureRequest,
    model_fixture: str,
    field_name: str,
) -> None:
    model = request.getfixturevalue(model_fixture)
    payload = model.model_dump(mode="python")
    payload[field_name] = datetime(2026, 1, 1)
    with pytest.raises(ValidationError):
        type(model).model_validate(payload)


def test_non_json_arguments_are_rejected(
    action: ActionIntent,
) -> None:
    payload = action.model_dump(mode="python")
    payload["arguments"] = {"value": object()}
    with pytest.raises(ValidationError):
        ActionIntent.model_validate(payload)


def test_empty_identifier_and_unknown_field_are_rejected(
    action: ActionIntent,
) -> None:
    empty_id = action.model_dump(mode="python")
    empty_id["action_id"] = ""
    with pytest.raises(ValidationError):
        ActionIntent.model_validate(empty_id)

    unknown_field = action.model_dump(mode="python")
    unknown_field["legacy_status"] = "draft"
    with pytest.raises(ValidationError):
        ActionIntent.model_validate(unknown_field)


def test_invalid_tool_input_schema_is_rejected(
    capability: ToolCapability,
) -> None:
    payload = capability.model_dump(mode="python")
    payload["input_schema"] = {
        "type": "object",
        "required": "must-be-an-array",
    }
    with pytest.raises(ValidationError):
        ToolCapability.model_validate(payload)


def test_observation_status_must_match_success(
    observation: Observation,
) -> None:
    payload = observation.model_dump(mode="python")
    payload["status"] = "execution_failed"
    with pytest.raises(ValidationError):
        Observation.model_validate(payload)


def test_finding_closure_rules_are_enforced(
    finding: Finding,
) -> None:
    open_with_closed_at = finding.model_dump(mode="python")
    open_with_closed_at["closed_at"] = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        Finding.model_validate(open_with_closed_at)

    closed_without_timestamp = finding.model_dump(mode="python")
    closed_without_timestamp["status"] = "closed"
    closed_without_timestamp["closed_at"] = None
    with pytest.raises(ValidationError):
        Finding.model_validate(closed_without_timestamp)
