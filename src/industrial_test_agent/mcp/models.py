from typing import Dict, List, Optional

from pydantic import BaseModel


class ToolCapability(BaseModel):
    tool_id: str
    name: str
    transport: str
    input_schema: Dict[str, object]
    output_schema: Dict[str, object]
    permissions: List[str] = []


class MCPRegistration(BaseModel):
    server_id: str
    version: str
    tools: List[ToolCapability]
    network_scope: Optional[str] = None
    timeout_seconds: Optional[int] = 30
    max_calls: Optional[int] = 10
    environment_type: Optional[str] = "test"
