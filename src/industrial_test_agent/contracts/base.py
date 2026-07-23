"""Common configuration for executable Pydantic contracts."""

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    """Reject undeclared fields so runtime validation matches JSON Schema."""

    model_config = ConfigDict(extra="forbid")
