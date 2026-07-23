"""Common configuration for executable Pydantic contracts."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticCustomError


class ContractModel(BaseModel):
    """Reject undeclared fields so runtime validation matches JSON Schema."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def validate_json_object(value: dict[str, Any]) -> dict[str, Any]:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise PydanticCustomError(
            "json_object",
            "Value must be a JSON-serializable object",
        ) from exc
    return value
