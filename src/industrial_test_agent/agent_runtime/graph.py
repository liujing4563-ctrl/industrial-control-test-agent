"""Minimal LangGraph case execution graph."""

from __future__ import annotations

from typing import Any, Dict, Optional

from industrial_test_agent.agent_runtime.state import CaseGraphState
from industrial_test_agent.agent_runtime import nodes
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
    ) -> None:
        self.agent = agent or MockAgent()
        self.policy = policy or PolicyValidator()
        self.runner = runner or MockRunner()
        self.evidence_store = evidence_store or EvidenceStore()

        nodes.set_runtime_context(
            self.agent, self.policy, self.runner, self.evidence_store
        )

        # Execution log
        self.log: list[str] = []

    def run(self, case_id: str, goal: str) -> CaseGraphState:
        """Run the case graph until a terminal state is reached."""
        state: CaseGraphState = {
            "case_id": case_id,
            "goal": goal,
            "stage": "initialized",
            "proposed_action_id": None,
            "latest_observation_id": None,
            "evidence_ids": [],
            "hypothesis_ids": [],
            "remaining_steps": 20,
            "termination_reason": None,
            "policy_decision": None,
        }

        # Initialize
        self._apply(state, nodes.initialize_case(state))
        self._log("case initialized")

        # Main loop
        while state["stage"] not in ("completed", "escalated", "rejected"):
            # Propose
            state_updates = nodes.propose_action(state)
            self._apply(state, state_updates)
            self._log("action proposed")

            # Validate
            state_updates = nodes.validate_action(state)
            self._apply(state, state_updates)

            decision = state.get("policy_decision", "")
            if decision == "allowed":
                self._log("policy allowed")

                # Execute
                state_updates = nodes.execute_action(state)
                self._apply(state, state_updates)
                self._log("mock runner executed")

                # Record
                state_updates = nodes.record_observation(state)
                self._apply(state, state_updates)
                self._log("observation recorded")

                if state.get("evidence_ids"):
                    self._log(f"evidence appended: {state['evidence_ids'][-1]}")

            elif decision == "approval_required":
                self._log("policy: approval required (pausing)")
                state["stage"] = "escalated"
                state["termination_reason"] = "Human approval required"
                break

            else:  # rejected
                self._log("policy rejected")
                state["stage"] = "rejected"
                state["termination_reason"] = "Policy rejected action"
                break

            # Decide next
            state_updates = nodes.decide_next(state)
            self._apply(state, state_updates)

        # Finalize
        nodes.finalize_case(state)
        self._log("case " + state["stage"])

        return state

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply(state: CaseGraphState, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if key in state:
                state[key] = value  # type: ignore[literal-required]

    def _log(self, msg: str) -> None:
        self.log.append(msg)
