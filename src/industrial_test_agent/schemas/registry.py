"""Stable mapping between contract models and repository Schema files."""

from pydantic import BaseModel

from industrial_test_agent.agent_runtime.checkpoint import CheckpointEnvelope
from industrial_test_agent.domain.action_intent import ActionIntent
from industrial_test_agent.domain.case_state import CaseState
from industrial_test_agent.domain.evidence import Evidence
from industrial_test_agent.domain.finding import Finding
from industrial_test_agent.domain.hypothesis import Hypothesis
from industrial_test_agent.domain.observation import Observation
from industrial_test_agent.mcp.models import ToolCapability
from industrial_test_agent.skills.models import CapabilityPackManifest


SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "action-intent.schema.json": ActionIntent,
    "observation.schema.json": Observation,
    "evidence.schema.json": Evidence,
    "case-state.schema.json": CaseState,
    "hypothesis.schema.json": Hypothesis,
    "finding.schema.json": Finding,
    "tool-capability.schema.json": ToolCapability,
    "capability-pack.schema.json": CapabilityPackManifest,
    "checkpoint-envelope.schema.json": CheckpointEnvelope,
}
