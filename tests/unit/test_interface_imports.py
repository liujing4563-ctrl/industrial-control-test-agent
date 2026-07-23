from industrial_test_agent.agent_runtime import (
    AgentRuntime,
    CheckpointEnvelope,
    Checkpointer,
    GraphRunner,
    JsonCheckpointer,
)
from industrial_test_agent.domain import (
    ActionIntent,
    CaseState,
    Evidence,
    Finding,
    Hypothesis,
    Observation,
)
from industrial_test_agent.evidence import EvidenceStoreProtocol
from industrial_test_agent.policy import PolicyResult, PolicyValidatorProtocol
from industrial_test_agent.runner import Runner
from industrial_test_agent.skills import CapabilityPackManifest


def test_public_contracts_import() -> None:
    assert all(
        contract is not None
        for contract in (
            ActionIntent,
            AgentRuntime,
            CapabilityPackManifest,
            CaseState,
            CheckpointEnvelope,
            Checkpointer,
            Evidence,
            EvidenceStoreProtocol,
            Finding,
            GraphRunner,
            Hypothesis,
            JsonCheckpointer,
            Observation,
            PolicyResult,
            PolicyValidatorProtocol,
            Runner,
        )
    )
