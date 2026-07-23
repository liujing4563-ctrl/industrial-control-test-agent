"""Versioned checkpoint bundle and controlled M1 migration."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from industrial_test_agent.contracts import ContractModel
from industrial_test_agent.domain.case_state import (
    CaseStage,
    CaseState,
    RuntimeNode,
)
from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.domain.observation import Observation


CHECKPOINT_VERSION = "2.0"
LEGACY_CHECKPOINT_VERSION = "1.0"
CheckpointGraphState = CaseState
_CANONICAL_STATE_FIELDS = {
    "case_id",
    "goal",
    "stage",
    "next_node",
    "action_ids",
    "observation_ids",
    "evidence_ids",
    "hypotheses",
    "findings",
    "remaining_steps",
    "termination_reason",
    "created_at",
    "updated_at",
    "metadata",
}


class CheckpointMetadata(ContractModel):
    case_id: str = Field(min_length=1)


class CheckpointEnvelope(ContractModel):
    """Self-contained Runtime state and Evidence snapshot."""

    checkpoint_version: Literal["2.0"]
    graph_state: CaseState
    evidence_snapshot: list[Evidence] = Field(default_factory=list)
    metadata: CheckpointMetadata

    @model_validator(mode="before")
    @classmethod
    def migrate_v1_envelope(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = deepcopy(value)
        if payload.get("checkpoint_version") == CHECKPOINT_VERSION:
            graph_state = payload.get("graph_state")
            if isinstance(graph_state, dict):
                missing = _CANONICAL_STATE_FIELDS.difference(graph_state)
                if missing:
                    raise ValueError(
                        "Checkpoint graph_state is missing canonical "
                        f"fields: {sorted(missing)}"
                    )
            return payload
        if payload.get("checkpoint_version") != LEGACY_CHECKPOINT_VERSION:
            return payload

        graph_state = CaseState.model_validate(payload.get("graph_state"))
        evidence_snapshot = []
        for evidence_payload in payload.get("evidence_snapshot", []):
            legacy_evidence = deepcopy(evidence_payload)
            metadata = legacy_evidence.get("metadata")
            if (
                isinstance(metadata, dict)
                and isinstance(metadata.get("observation"), dict)
                and graph_state.active_action is not None
            ):
                metadata["observation"].setdefault(
                    "tool_id",
                    graph_state.active_action.capability_id,
                )
            evidence_snapshot.append(Evidence.model_validate(legacy_evidence))

        return {
            "checkpoint_version": CHECKPOINT_VERSION,
            "graph_state": graph_state,
            "evidence_snapshot": evidence_snapshot,
            "metadata": payload.get("metadata"),
        }

    @model_validator(mode="after")
    def validate_bundle_consistency(self) -> Self:
        state = self.graph_state
        self._validate_graph_consistency(state)

        if self.metadata.case_id != state.case_id:
            raise ValueError(
                "Checkpoint metadata case_id does not match state"
            )

        snapshot_ids = [
            evidence.evidence_id for evidence in self.evidence_snapshot
        ]
        if len(snapshot_ids) != len(set(snapshot_ids)):
            raise ValueError(
                "Checkpoint snapshot contains duplicate Evidence IDs"
            )
        if snapshot_ids != state.evidence_ids:
            raise ValueError(
                "Checkpoint Evidence snapshot does not resolve "
                "state evidence_ids"
            )

        idempotency_keys = [
            evidence.idempotency_key for evidence in self.evidence_snapshot
        ]
        if len(idempotency_keys) != len(set(idempotency_keys)):
            raise ValueError(
                "Checkpoint snapshot contains duplicate Evidence "
                "idempotency keys"
            )

        for evidence in self.evidence_snapshot:
            self._validate_evidence(evidence, state)
        if (
            state.latest_observation is not None
            and state.next_node is not RuntimeNode.RECORD_OBSERVATION
            and not any(
                evidence.observation_id
                == state.latest_observation.observation_id
                for evidence in self.evidence_snapshot
            )
        ):
            raise ValueError(
                "Latest Observation is not resolved by the Evidence snapshot"
            )
        return self

    @staticmethod
    def _validate_graph_consistency(state: CaseState) -> None:
        allowed_nodes: dict[
            CaseStage, set[RuntimeNode | None]
        ] = {
            CaseStage.INITIALIZED: {RuntimeNode.INITIALIZE_CASE},
            CaseStage.PLANNING: {
                RuntimeNode.PROPOSE_ACTION,
                RuntimeNode.VALIDATE_ACTION,
            },
            CaseStage.VALIDATION: {RuntimeNode.EXECUTE_ACTION},
            CaseStage.EXECUTION: {RuntimeNode.RECORD_OBSERVATION},
            CaseStage.DIAGNOSIS: {RuntimeNode.DECIDE_NEXT},
            CaseStage.REPLANNING: {RuntimeNode.PROPOSE_ACTION},
            CaseStage.COMPLETED: {RuntimeNode.FINALIZE_CASE, None},
            CaseStage.ESCALATED: {RuntimeNode.FINALIZE_CASE, None},
            CaseStage.REJECTED: {RuntimeNode.FINALIZE_CASE, None},
        }
        terminal_stages = {
            CaseStage.COMPLETED,
            CaseStage.ESCALATED,
            CaseStage.REJECTED,
        }
        if state.stage not in allowed_nodes:
            raise ValueError(
                f"Checkpoint stage is not a Runtime stage: {state.stage}"
            )
        if state.stage in terminal_stages and not state.termination_reason:
            raise ValueError("Terminal checkpoint requires termination_reason")
        if state.stage not in terminal_stages and state.next_node is None:
            raise ValueError("Non-terminal checkpoint requires next_node")
        if state.next_node not in allowed_nodes[state.stage]:
            raise ValueError(
                "Invalid stage/next_node combination: "
                f"{state.stage}/{state.next_node}"
            )

        action = state.active_action
        observation = state.latest_observation
        if action is not None:
            if action.case_id != state.case_id:
                raise ValueError(
                    "ActionIntent case_id does not match checkpoint"
                )
            if action.action_id not in state.action_ids:
                raise ValueError(
                    "Active ActionIntent is missing from action_ids"
                )
        if state.stage is CaseStage.INITIALIZED and action is not None:
            raise ValueError(
                "Initialized checkpoint cannot contain an ActionIntent"
            )

        if observation is not None:
            if observation.case_id != state.case_id:
                raise ValueError(
                    "Observation case_id does not match checkpoint"
                )
            if observation.observation_id not in state.observation_ids:
                raise ValueError(
                    "Latest Observation is missing from observation_ids"
                )
            if action is None or observation.action_id != action.action_id:
                raise ValueError(
                    "Observation does not reference the active ActionIntent"
                )
        if observation is None and state.last_execution_success is not None:
            raise ValueError(
                "Execution result requires an Observation in the checkpoint"
            )
        if (
            observation is not None
            and state.last_execution_success is not observation.success
        ):
            raise ValueError(
                "Execution result does not match the Observation"
            )
        if observation is not None and state.policy_decision != "allowed":
            raise ValueError(
                "Observation requires an allowed policy decision"
            )

        nodes_requiring_action = {
            RuntimeNode.VALIDATE_ACTION,
            RuntimeNode.EXECUTE_ACTION,
            RuntimeNode.RECORD_OBSERVATION,
            RuntimeNode.DECIDE_NEXT,
        }
        if state.next_node in nodes_requiring_action and action is None:
            raise ValueError(
                f"{state.next_node} requires an ActionIntent"
            )
        if (
            state.next_node is RuntimeNode.EXECUTE_ACTION
            and state.policy_decision != "allowed"
        ):
            raise ValueError(
                "execute_action requires an allowed policy decision"
            )
        if (
            state.next_node is RuntimeNode.EXECUTE_ACTION
            and observation is not None
        ):
            raise ValueError(
                "Checkpoint would repeat an ActionIntent that already "
                "has an Observation"
            )
        if (
            state.next_node
            in {
                RuntimeNode.RECORD_OBSERVATION,
                RuntimeNode.DECIDE_NEXT,
            }
            and observation is None
        ):
            raise ValueError(
                f"{state.next_node} requires an Observation"
            )

    @staticmethod
    def _validate_evidence(
        evidence: Evidence,
        state: CaseState,
    ) -> None:
        if evidence.case_id != state.case_id:
            raise ValueError(
                "Checkpoint Evidence case_id does not match state"
            )
        if evidence.action_id not in state.action_ids:
            raise ValueError(
                "Checkpoint Evidence action_id is not in state"
            )
        if evidence.observation_id not in state.observation_ids:
            raise ValueError(
                "Checkpoint Evidence observation_id is not in state"
            )

        expected_key = (
            f"{evidence.case_id}:{evidence.observation_id}:"
            "tool-observation"
        )
        if evidence.idempotency_key != expected_key:
            raise ValueError(
                "Checkpoint Evidence has an invalid idempotency key"
            )

        expected_id = (
            f"ev-{hashlib.sha256(expected_key.encode()).hexdigest()[:16]}"
        )
        if evidence.evidence_id != expected_id:
            raise ValueError(
                "Checkpoint Evidence ID is not deterministic"
            )

        observation = Observation.model_validate(evidence.payload)
        if observation.observation_id != evidence.observation_id:
            raise ValueError(
                "Checkpoint Evidence Observation ID does not match"
            )
        if observation.case_id != evidence.case_id:
            raise ValueError(
                "Checkpoint Evidence Observation case_id does not match"
            )
        if observation.action_id != evidence.action_id:
            raise ValueError(
                "Checkpoint Evidence ActionIntent ID does not match"
            )

        expected_hash = hashlib.sha256(
            observation.model_dump_json().encode()
        ).hexdigest()
        if evidence.content_hash != expected_hash:
            raise ValueError(
                "Checkpoint Evidence content hash does not match"
            )
