from pathlib import Path

from industrial_test_agent.agent_runtime.checkpoint import CheckpointEnvelope
from industrial_test_agent.agent_runtime.checkpointer import JsonCheckpointer
from industrial_test_agent.agent_runtime.graph import GraphRunner
from industrial_test_agent.agent_runtime.interfaces import (
    AgentRuntime,
    Checkpointer,
)
from industrial_test_agent.domain import (
    ActionIntent,
    CaseState,
    CaseStage,
    RiskLevel,
)
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


def test_policy_uses_capability_risk_not_action_claim(
    action: ActionIntent,
) -> None:
    forged = action.model_copy(
        update={
            "capability_id": "plc.write_test_signal",
            "arguments": {"signal_name": "x", "value": True},
            "risk_level": RiskLevel.LOW,
        }
    )
    decision = PolicyValidator().validate(
        CaseState(
            case_id="case-policy",
            goal="test",
            stage=CaseStage.PLANNING,
            remaining_steps=20,
        ),
        forged,
    )
    assert decision.decision == "approval_required"


def test_evidence_snapshot_is_isolated_and_restorable(
    action: ActionIntent,
) -> None:
    observation = MockRunner().execute(
        action.model_copy(
            update={
                "capability_id": "plc.read_interlock",
                "arguments": {"group": "motor_start"},
            }
        )
    )
    source = EvidenceStore()
    evidence = source.append_from_observation(observation)
    snapshot = source.snapshot(action.case_id)
    snapshot[0].payload["tampered"] = True

    stored = source.get(evidence.evidence_id)
    assert stored is not None
    assert "tampered" not in stored.payload

    restored = EvidenceStore()
    restored.restore(source.snapshot(action.case_id))
    assert restored.get(evidence.evidence_id) == evidence


def test_json_checkpointer_uses_checkpoint_envelope(
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
    checkpointer.save("checkpoint-001", envelope)
    assert checkpointer.load("checkpoint-001") == envelope
