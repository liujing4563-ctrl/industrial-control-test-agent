from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest

from industrial_test_agent.domain import (
    ActionIntent,
    CaseStage,
    CaseState,
    Evidence,
    EvidenceType,
    Finding,
    FindingSeverity,
    FindingStatus,
    Hypothesis,
    HypothesisStatus,
    Observation,
    ObservationSourceType,
    ObservationStatus,
    RiskLevel,
    SideEffectType,
)
from industrial_test_agent.mcp.models import ToolCapability


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def action(now: datetime) -> ActionIntent:
    return ActionIntent(
        action_id="action-contract-001",
        case_id="case-contract-001",
        capability_id="demo.read_status",
        arguments={"channel": "status"},
        risk_level=RiskLevel.LOW,
        requested_by="contract-test",
        reason="validate canonical contract",
        created_at=now,
        idempotency_key="case-contract-001:action-contract-001",
        metadata={"suite": "contract"},
    )


@pytest.fixture
def observation(
    action: ActionIntent,
    now: datetime,
) -> Observation:
    return Observation(
        observation_id="observation-contract-001",
        case_id=action.case_id,
        action_id=action.action_id,
        tool_id=action.capability_id,
        status=ObservationStatus.SUCCEEDED,
        success=True,
        data={"ready": True},
        received_at=now,
        source_type=ObservationSourceType.MOCK,
        metadata={"source": "contract-test"},
    )


@pytest.fixture
def evidence(
    observation: Observation,
    now: datetime,
) -> Evidence:
    idempotency_key = (
        f"{observation.case_id}:{observation.observation_id}:"
        "tool-observation"
    )
    return Evidence(
        evidence_id=(
            "ev-"
            + hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
        ),
        case_id=observation.case_id,
        observation_id=observation.observation_id,
        action_id=observation.action_id,
        evidence_type=EvidenceType.TOOL_OBSERVATION,
        payload=observation.model_dump(mode="json"),
        source=observation.source,
        content_hash=hashlib.sha256(
            observation.model_dump_json().encode()
        ).hexdigest(),
        created_at=now,
        idempotency_key=idempotency_key,
        metadata={"suite": "contract"},
    )


@pytest.fixture
def case_state(
    action: ActionIntent,
    observation: Observation,
    evidence: Evidence,
    now: datetime,
) -> CaseState:
    return CaseState(
        case_id=action.case_id,
        goal="validate contracts",
        stage=CaseStage.COMPLETED,
        next_node=None,
        action_ids=[action.action_id],
        observation_ids=[observation.observation_id],
        evidence_ids=[evidence.evidence_id],
        hypotheses=["hypothesis-contract-001"],
        findings=["finding-contract-001"],
        remaining_steps=19,
        termination_reason="contract fixture completed",
        created_at=now,
        updated_at=now,
        metadata={"suite": "contract"},
        active_action=action,
        latest_observation=observation,
        last_execution_success=True,
        policy_decision="allowed",
    )


@pytest.fixture
def hypothesis(now: datetime) -> Hypothesis:
    return Hypothesis(
        hypothesis_id="hypothesis-contract-001",
        case_id="case-contract-001",
        statement="The platform contract is internally consistent",
        confidence=0.8,
        supporting_evidence_ids=["evidence-contract-001"],
        status=HypothesisStatus.SUPPORTED,
        created_at=now,
        updated_at=now,
        metadata={"suite": "contract"},
    )


@pytest.fixture
def finding(now: datetime) -> Finding:
    return Finding(
        finding_id="finding-contract-001",
        case_id="case-contract-001",
        title="Contract fixture",
        description="A generic platform finding",
        severity=FindingSeverity.LOW,
        status=FindingStatus.CONFIRMED,
        evidence_ids=["evidence-contract-001"],
        hypothesis_ids=["hypothesis-contract-001"],
        created_at=now,
        metadata={"suite": "contract"},
    )


@pytest.fixture
def capability() -> ToolCapability:
    return ToolCapability(
        capability_id="demo.read_status",
        display_name="读取演示状态",
        description="Generic contract-test capability",
        input_schema={
            "type": "object",
            "properties": {"channel": {"type": "string"}},
            "required": ["channel"],
            "additionalProperties": False,
        },
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        side_effect_type=SideEffectType.READ_ONLY,
        tags=["demo"],
        metadata={"suite": "contract"},
    )
