from typing import Any, Optional

from pydantic import Field

from industrial_test_agent.contracts import ContractModel


class ToolCapability(ContractModel):
    tool_id: str = Field(min_length=1)
    name: str
    transport: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permissions: list[str] = Field(default_factory=list)


class MCPRegistration(ContractModel):
    server_id: str = Field(min_length=1)
    version: str
    tools: list[ToolCapability]
    network_scope: Optional[str] = None
    timeout_seconds: Optional[int] = 30
    max_calls: Optional[int] = 10
    environment_type: Optional[str] = "test"
