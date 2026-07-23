from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, ClassVar, Self

from pydantic import (
    AwareDatetime,
    Field,
    field_validator,
    model_validator,
)

from industrial_test_agent.contracts.base import (
    ContractModel,
    validate_json_object,
)
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.enums import PolicyDecision
from industrial_test_agent.domain.observation import Observation


class CaseStage(StrEnum):
    INTAKE = "intake"
    INITIALIZED = "initialized"
    PLANNING = "planning"
    VALIDATION = "validation"
    EXECUTION = "execution"
    DIAGNOSIS = "diagnosis"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    REJECTED = "rejected"


class RuntimeNode(StrEnum):
    INITIALIZE_CASE = "initialize_case"
    PROPOSE_ACTION = "propose_action"
    VALIDATE_ACTION = "validate_action"
    EXECUTE_ACTION = "execute_action"
    RECORD_OBSERVATION = "record_observation"
    DECIDE_NEXT = "decide_next"
    FINALIZE_CASE = "finalize_case"


class CaseState(ContractModel):
    case_id: str = Field(min_length=1)
    goal: str = ""
    stage: CaseStage = CaseStage.INITIALIZED
    next_node: RuntimeNode | None = None
    action_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    remaining_steps: int = Field(default=20, ge=0)
    termination_reason: str | None = None
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    active_action: ActionIntent | None = None
    latest_observation: Observation | None = None
    replan_count: int = Field(default=0, ge=0)
    last_execution_success: bool | None = None
    policy_decision: PolicyDecision | None = None
    policy_reason: str | None = None

    _COMPATIBILITY_KEYS: ClassVar[set[str]] = {
        "proposed_action_id",
        "proposed_action",
        "latest_observation_id",
        "hypothesis_ids",
    }

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        legacy = dict(value)

        if "current_phase" in legacy and "stage" not in legacy:
            legacy["stage"] = legacy.pop("current_phase")
        if "test_objective" in legacy and "goal" not in legacy:
            legacy["goal"] = legacy.pop("test_objective") or ""
        if "hypothesis_ids" in legacy and "hypotheses" not in legacy:
            legacy["hypotheses"] = legacy.pop("hypothesis_ids")

        if "active_action" not in legacy and "proposed_action" in legacy:
            legacy["active_action"] = legacy["proposed_action"]
        legacy.pop("proposed_action", None)
        proposed_action_id = legacy.pop("proposed_action_id", None)
        active_action = legacy.get("active_action")
        if active_action is not None:
            active_action = ActionIntent.model_validate(active_action)
            legacy["active_action"] = active_action
            action_ids = list(legacy.get("action_ids", []))
            action_id = proposed_action_id or active_action.action_id
            if action_id not in action_ids:
                action_ids.append(action_id)
            legacy["action_ids"] = action_ids

        latest_observation_id = legacy.pop(
            "latest_observation_id", None
        )
        latest_observation = legacy.get("latest_observation")
        if latest_observation is not None:
            observation_payload = dict(latest_observation)
            if (
                "payload" in observation_payload
                and "tool_id" not in observation_payload
                and active_action is not None
            ):
                observation_payload["tool_id"] = (
                    active_action.capability_id
                )
            latest_observation = Observation.model_validate(
                observation_payload
            )
            legacy["latest_observation"] = latest_observation
            observation_ids = list(legacy.get("observation_ids", []))
            observation_id = (
                latest_observation_id
                or latest_observation.observation_id
            )
            if observation_id not in observation_ids:
                observation_ids.append(observation_id)
            legacy["observation_ids"] = observation_ids

        metadata = dict(legacy.pop("metadata", {}))
        legacy_metadata_keys = {
            "requirements",
            "test_cases",
            "excluded_causes",
            "remaining_budget",
            "approval_status",
            "regression_status",
            "root_cause_id",
            "pending_approval_id",
        }
        for key in legacy_metadata_keys:
            if key in legacy:
                metadata[key] = legacy.pop(key)
        legacy["metadata"] = metadata
        return legacy

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        for field_name in (
            "action_ids",
            "observation_ids",
            "evidence_ids",
            "hypotheses",
            "findings",
        ):
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} cannot contain duplicates")
        return self

    @field_validator("metadata")
    @classmethod
    def require_json_object(
        cls, value: dict[str, Any]
    ) -> dict[str, Any]:
        return validate_json_object(value)

    @property
    def current_phase(self) -> str:
        return self.stage.value

    @current_phase.setter
    def current_phase(self, value: str) -> None:
        self.stage = CaseStage(value)

    @property
    def test_objective(self) -> str:
        return self.goal

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and (
            key in self.__class__.model_fields
            or key in self._COMPATIBILITY_KEYS
        )

    def __getitem__(self, key: str) -> Any:
        if key == "proposed_action_id":
            return self.active_action.action_id if self.active_action else None
        if key == "proposed_action":
            return (
                self.active_action.model_dump(mode="json")
                if self.active_action
                else None
            )
        if key == "latest_observation_id":
            return (
                self.latest_observation.observation_id
                if self.latest_observation
                else None
            )
        if key == "hypothesis_ids":
            return self.hypotheses
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "proposed_action":
            self.active_action = (
                ActionIntent.model_validate(value)
                if value is not None
                else None
            )
            return
        if key == "latest_observation":
            self.latest_observation = (
                Observation.model_validate(value)
                if value is not None
                else None
            )
            return
        if key in {"proposed_action_id", "latest_observation_id"}:
            return
        if key == "hypothesis_ids":
            self.hypotheses = list(value)
            return
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            value = self[key]
        except (AttributeError, KeyError):
            return default
        return default if value is None and key not in self else value
