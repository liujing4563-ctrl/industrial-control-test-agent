"""Versioned checkpoint bundle and recovery validation."""

from __future__ import annotations

import hashlib
from typing import Any, Literal, Optional, Self, cast

from pydantic import ConfigDict, Field, model_validator

from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.contracts import ContractModel
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.policy.decisions import PolicyDecision


Stage = Literal[
    "initialized",
    "planning",
    "validation",
    "execution",
    "diagnosis",
    "replanning",
    "completed",
    "escalated",
    "rejected",
]
NodeName = Literal[
    "initialize_case",
    "propose_action",
    "validate_action",
    "execute_action",
    "record_observation",
    "decide_next",
    "finalize_case",
]
CHECKPOINT_VERSION = "1.0"


class CheckpointGraphState(ContractModel):
    """Validated serialized representation of CaseGraphState."""

    case_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    stage: Stage
    proposed_action_id: Optional[str]
    proposed_action: Optional[dict[str, Any]]
    latest_observation_id: Optional[str]
    latest_observation: Optional[dict[str, Any]]
    evidence_ids: list[str]
    hypothesis_ids: list[str]
    remaining_steps: int = Field(ge=0)
    replan_count: int = Field(ge=0)
    last_execution_success: Optional[bool]
    termination_reason: Optional[str]
    policy_decision: Optional[PolicyDecision]
    policy_reason: Optional[str]
    next_node: Optional[NodeName]

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_graph_consistency(self) -> Self:
        allowed_nodes: dict[Stage, set[Optional[NodeName]]] = {
            "initialized": {"initialize_case"},
            "planning": {"propose_action", "validate_action"},
            "validation": {"execute_action"},
            "execution": {"record_observation"},
            "diagnosis": {"decide_next"},
            "replanning": {"propose_action"},
            "completed": {"finalize_case", None},
            "escalated": {"finalize_case", None},
            "rejected": {"finalize_case", None},
        }
        terminal_stages = {"completed", "escalated", "rejected"}
        if self.stage in terminal_stages and not self.termination_reason:
            raise ValueError("Terminal checkpoint requires termination_reason")
        if self.stage not in terminal_stages and self.next_node is None:
            raise ValueError("Non-terminal checkpoint requires next_node")
        if self.next_node not in allowed_nodes[self.stage]:
            raise ValueError(
                f"Invalid stage/next_node combination: "
                f"{self.stage}/{self.next_node}"
            )

        if (self.proposed_action_id is None) != (self.proposed_action is None):
            raise ValueError("ActionIntent ID and payload must appear together")
        if self.proposed_action is not None:
            intent = ActionIntent.model_validate(self.proposed_action)
            if intent.intent_id != self.proposed_action_id:
                raise ValueError("ActionIntent ID does not match its payload")
            if intent.case_id != self.case_id:
                raise ValueError("ActionIntent case_id does not match checkpoint")
        if self.stage == "initialized" and self.proposed_action is not None:
            raise ValueError("Initialized checkpoint cannot contain an ActionIntent")

        if (self.latest_observation_id is None) != (
            self.latest_observation is None
        ):
            raise ValueError("Observation ID and payload must appear together")
        observation = None
        if self.latest_observation is not None:
            observation = Observation.model_validate(self.latest_observation)
            if observation.observation_id != self.latest_observation_id:
                raise ValueError("Observation ID does not match its payload")
            if observation.case_id != self.case_id:
                raise ValueError("Observation case_id does not match checkpoint")
            if (
                self.proposed_action_id is not None
                and observation.related_action_intent_id
                != self.proposed_action_id
            ):
                raise ValueError(
                    "Observation does not reference the active ActionIntent"
                )
        if observation is None and self.last_execution_success is not None:
            raise ValueError(
                "Execution result requires an Observation in the checkpoint"
            )
        if (
            observation is not None
            and self.last_execution_success
            is not bool(observation.payload.get("success", False))
        ):
            raise ValueError(
                "Execution result does not match the Observation payload"
            )
        if observation is not None and self.proposed_action is None:
            raise ValueError("Observation requires its ActionIntent in the checkpoint")
        if observation is not None and self.policy_decision != "allowed":
            raise ValueError("Observation requires an allowed policy decision")

        nodes_requiring_action = {
            "validate_action",
            "execute_action",
            "record_observation",
            "decide_next",
        }
        if self.next_node in nodes_requiring_action and self.proposed_action is None:
            raise ValueError(f"{self.next_node} requires an ActionIntent")
        if self.next_node == "execute_action" and self.policy_decision != "allowed":
            raise ValueError("execute_action requires an allowed policy decision")
        if self.next_node == "execute_action" and observation is not None:
            raise ValueError(
                "Checkpoint would repeat an ActionIntent that already has an Observation"
            )
        if (
            self.next_node in {"record_observation", "decide_next"}
            and self.latest_observation is None
        ):
            raise ValueError(f"{self.next_node} requires an Observation")

        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("Checkpoint contains duplicate Evidence IDs")
        if len(self.hypothesis_ids) != len(set(self.hypothesis_ids)):
            raise ValueError("Checkpoint contains duplicate hypothesis IDs")
        return self

    def to_runtime_state(self) -> CaseGraphState:
        return cast(CaseGraphState, self.model_dump(mode="json"))


class CheckpointMetadata(ContractModel):
    case_id: str = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class CheckpointEnvelope(ContractModel):
    """Self-contained state and Evidence snapshot used for recovery."""

    checkpoint_version: Literal["1.0"]
    graph_state: CheckpointGraphState
    evidence_snapshot: list[Evidence] = Field(default_factory=list)
    metadata: CheckpointMetadata

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_bundle_consistency(self) -> Self:
        state = self.graph_state
        if self.metadata.case_id != state.case_id:
            raise ValueError("Checkpoint metadata case_id does not match state")

        snapshot_ids = [evidence.evidence_id for evidence in self.evidence_snapshot]
        if len(snapshot_ids) != len(set(snapshot_ids)):
            raise ValueError("Checkpoint snapshot contains duplicate Evidence IDs")
        if snapshot_ids != state.evidence_ids:
            raise ValueError(
                "Checkpoint Evidence snapshot does not resolve state evidence_ids"
            )

        idempotency_keys = [
            evidence.idempotency_key
            for evidence in self.evidence_snapshot
            if evidence.idempotency_key is not None
        ]
        if len(idempotency_keys) != len(set(idempotency_keys)):
            raise ValueError(
                "Checkpoint snapshot contains duplicate Evidence idempotency keys"
            )

        for evidence in self.evidence_snapshot:
            self._validate_evidence(evidence, state.case_id)
        if (
            state.latest_observation_id is not None
            and state.next_node != "record_observation"
            and not any(
                evidence.observation_id == state.latest_observation_id
                for evidence in self.evidence_snapshot
            )
        ):
            raise ValueError(
                "Latest Observation is not resolved by the Evidence snapshot"
            )
        return self

    @staticmethod
    def _validate_evidence(evidence: Evidence, case_id: str) -> None:
        if evidence.case_id != case_id:
            raise ValueError("Checkpoint Evidence case_id does not match state")

        expected_key = (
            f"{evidence.case_id}:{evidence.observation_id}:tool-observation"
        )
        if evidence.idempotency_key != expected_key:
            raise ValueError("Checkpoint Evidence has an invalid idempotency key")

        expected_id = (
            f"ev-{hashlib.sha256(expected_key.encode()).hexdigest()[:16]}"
        )
        if evidence.evidence_id != expected_id:
            raise ValueError("Checkpoint Evidence ID is not deterministic")

        observation_payload = evidence.metadata.get("observation")
        if observation_payload is None:
            raise ValueError("Checkpoint Evidence is missing its Observation")
        observation = Observation.model_validate(observation_payload)
        if observation.observation_id != evidence.observation_id:
            raise ValueError("Checkpoint Evidence Observation ID does not match")
        if observation.case_id != evidence.case_id:
            raise ValueError("Checkpoint Evidence Observation case_id does not match")

        expected_hash = hashlib.sha256(
            observation.model_dump_json().encode()
        ).hexdigest()
        if evidence.content_hash != expected_hash:
            raise ValueError("Checkpoint Evidence content hash does not match")
