"""Minimal deterministic case execution graph."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from industrial_test_agent.agent_runtime.checkpoint import (
    CheckpointEnvelope,
    CheckpointGraphState,
    CheckpointMetadata,
)
from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.agent_runtime import nodes
from industrial_test_agent.agent_runtime.routing import (
    route_after_decision,
    route_after_validation,
)
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.policy.validator import PolicyValidator
from industrial_test_agent.runner.mock_runner import MockRunner
from industrial_test_agent.evidence.in_memory_store import EvidenceStore


class GraphRunner:
    """Execute the case graph step-by-step (deterministic loop, no LangGraph dep)."""

    def __init__(
        self,
        agent: Optional[MockAgent] = None,
        policy: Optional[PolicyValidator] = None,
        runner: Optional[MockRunner] = None,
        evidence_store: Optional[EvidenceStore] = None,
        max_steps: int = 20,
        required_evidence_count: int = 1,
    ) -> None:
        if max_steps < 0:
            raise ValueError("max_steps must be non-negative")
        if required_evidence_count < 1:
            raise ValueError("required_evidence_count must be at least 1")

        self.context = nodes.RuntimeContext(
            agent=agent or MockAgent(),
            policy=policy or PolicyValidator(),
            runner=runner or MockRunner(),
            evidence_store=evidence_store or EvidenceStore(),
            max_steps=max_steps,
            required_evidence_count=required_evidence_count,
        )

        self.log: list[str] = []

    @property
    def evidence_store(self) -> EvidenceStore:
        return self.context.evidence_store

    @property
    def agent(self) -> MockAgent:
        return self.context.agent

    @property
    def policy(self) -> PolicyValidator:
        return self.context.policy

    @property
    def runner(self) -> MockRunner:
        return self.context.runner

    @property
    def max_steps(self) -> int:
        return self.context.max_steps

    @property
    def required_evidence_count(self) -> int:
        return self.context.required_evidence_count

    def run(
        self,
        case_id: str,
        goal: str,
        *,
        max_node_executions: Optional[int] = None,
    ) -> CaseGraphState:
        """Start a case and run until completion or an optional pause point."""
        self.log = []
        state = self._new_state(case_id, goal)
        return self._run_state(state, max_node_executions=max_node_executions)

    def resume(
        self,
        checkpoint: str | Mapping[str, Any],
        *,
        max_node_executions: Optional[int] = None,
    ) -> CaseGraphState:
        """Resume a validated JSON or dictionary checkpoint bundle."""
        if isinstance(checkpoint, str):
            payload = json.loads(checkpoint)
        else:
            payload = deepcopy(dict(checkpoint))

        envelope = self._load_checkpoint(payload)
        self.evidence_store.restore_snapshot(envelope.evidence_snapshot)
        state = envelope.graph_state.to_runtime_state()
        return self._run_state(state, max_node_executions=max_node_executions)

    def checkpoint(self, state: CaseGraphState) -> str:
        """Serialize graph state and its Evidence records as a versioned bundle."""
        graph_state = CheckpointGraphState.model_validate(state)
        evidence_snapshot = []
        for evidence_id in graph_state.evidence_ids:
            evidence = self.evidence_store.get(evidence_id)
            if evidence is None:
                raise ValueError(
                    f"Checkpoint references missing Evidence: {evidence_id}"
                )
            evidence_snapshot.append(evidence)

        envelope = CheckpointEnvelope(
            graph_state=graph_state,
            evidence_snapshot=evidence_snapshot,
            checkpoint_metadata=CheckpointMetadata(case_id=graph_state.case_id),
        )
        return envelope.model_dump_json()

    def _new_state(self, case_id: str, goal: str) -> CaseGraphState:
        return {
            "case_id": case_id,
            "goal": goal,
            "stage": "initialized",
            "proposed_action_id": None,
            "proposed_action": None,
            "latest_observation_id": None,
            "latest_observation": None,
            "evidence_ids": [],
            "hypothesis_ids": [],
            "remaining_steps": self.context.max_steps,
            "replan_count": 0,
            "last_execution_success": None,
            "termination_reason": None,
            "policy_decision": None,
            "policy_reason": None,
            "next_node": "initialize_case",
        }

    def _run_state(
        self,
        state: CaseGraphState,
        *,
        max_node_executions: Optional[int],
    ) -> CaseGraphState:
        executed = 0
        while state.get("next_node") is not None:
            if max_node_executions is not None and executed >= max_node_executions:
                break
            self._execute_node(state, state["next_node"])
            executed += 1
        return state

    def _execute_node(self, state: CaseGraphState, node_name: str) -> None:
        if node_name == "initialize_case":
            self._apply(state, nodes.initialize_case(state, self.context))
            state["next_node"] = "propose_action"
            self._log("case initialized")
            return

        if node_name == "propose_action":
            self._apply(state, nodes.propose_action(state, self.context))
            tool_name = state["proposed_action"]["action_details"]["tool_capability"]
            state["next_node"] = "validate_action"
            self._log(f"action proposed: {tool_name}")
            return

        if node_name == "validate_action":
            self._apply(state, nodes.validate_action(state, self.context))
            decision = state.get("policy_decision")
            self._log(f"policy decision: {decision}")
            if decision == "approval_required":
                state["stage"] = "escalated"
                state["termination_reason"] = state.get("policy_reason")
            elif decision == "rejected":
                state["stage"] = "rejected"
                state["termination_reason"] = state.get("policy_reason")
            state["next_node"] = route_after_validation(state)
            return

        if node_name == "execute_action":
            self._apply(state, nodes.execute_action(state, self.context))
            state["next_node"] = "record_observation"
            if state.get("last_execution_success"):
                self._log("mock runner executed")
            else:
                self._log("mock runner failed")
            return

        if node_name == "record_observation":
            self._apply(state, nodes.record_observation(state, self.context))
            state["next_node"] = "decide_next"
            self._log("observation recorded")
            self._log(f"evidence appended: {state['evidence_ids'][-1]}")
            return

        if node_name == "decide_next":
            self._apply(state, nodes.decide_next(state, self.context))
            if state["stage"] == "replanning":
                self._log("runner failure routed to replan")
            state["next_node"] = route_after_decision(state)
            return

        if node_name == "finalize_case":
            self._apply(state, nodes.finalize_case(state, self.context))
            state["next_node"] = None
            self._log("case " + state["stage"])
            return

        raise ValueError(f"Unknown graph node: {node_name}")

    @staticmethod
    def _apply(state: CaseGraphState, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if key in state:
                state[key] = value  # type: ignore[literal-required]

    def _load_checkpoint(self, payload: Mapping[str, Any]) -> CheckpointEnvelope:
        if "graph_state" in payload:
            return CheckpointEnvelope.model_validate(payload)

        # Backward compatibility for M1 raw-state checkpoints. Existing
        # Evidence references must already be resolvable by the current store.
        graph_state = CheckpointGraphState.model_validate(payload)
        evidence_snapshot = []
        for evidence_id in graph_state.evidence_ids:
            evidence = self.evidence_store.get(evidence_id)
            if evidence is None:
                raise ValueError(
                    "Legacy checkpoint references Evidence missing from the store: "
                    f"{evidence_id}"
                )
            evidence_snapshot.append(evidence)
        return CheckpointEnvelope(
            graph_state=graph_state,
            evidence_snapshot=evidence_snapshot,
            checkpoint_metadata=CheckpointMetadata(case_id=graph_state.case_id),
        )

    def _log(self, msg: str) -> None:
        self.log.append(msg)
