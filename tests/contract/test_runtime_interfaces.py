from pathlib import Path

from industrial_test_agent.agent_runtime.checkpoint import CheckpointEnvelope
from industrial_test_agent.agent_runtime.checkpointer import JsonCheckpointer
from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.agent_runtime.interfaces import (
    AgentRuntime,
    Checkpointer,
)
from industrial_test_agent.agents.mock_agent import MockAgent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.evidence.in_memory_store import EvidenceStore
from industrial_test_agent.evidence.interfaces import EvidenceStoreProtocol
from industrial_test_agent.policy.interfaces import PolicyValidatorProtocol
from industrial_test_agent.policy.validator import PolicyValidator
from industrial_test_agent.runner.interfaces import Runner
from industrial_test_agent.runner.mock_runner import MockRunner


def test_runtime_implementations_satisfy_public_protocols() -> None:
    assert isinstance(GraphRunner(), AgentRuntime)
    assert isinstance(PolicyValidator(), PolicyValidatorProtocol)
    assert isinstance(MockRunner(), Runner)
    assert isinstance(EvidenceStore(), EvidenceStoreProtocol)


def test_runner_policy_and_evidence_share_canonical_models() -> None:
    case = CaseState(case_id="case-contract", current_phase="planning")
    intent = MockAgent().propose(case)

    decision = PolicyValidator().validate(case, intent)
    observation = MockRunner().execute(intent)
    evidence = EvidenceStore().append_from_observation(observation)

    assert decision.decision == "allowed"
    assert observation.related_action_intent_id == intent.intent_id
    assert evidence.observation_id == observation.observation_id


def test_json_checkpointer_roundtrips_checkpoint_envelope(
    tmp_path: Path,
) -> None:
    runtime = GraphRunner()
    state = runtime.run(
        "case-checkpointer",
        "validate Checkpointer contract",
        max_node_executions=5,
    )
    envelope = CheckpointEnvelope.model_validate_json(runtime.checkpoint(state))
    checkpointer = JsonCheckpointer(tmp_path)

    assert isinstance(checkpointer, Checkpointer)
    path = checkpointer.save("checkpoint-001", envelope)

    assert path == tmp_path / "checkpoint-001.json"
    assert checkpointer.load("checkpoint-001") == envelope
