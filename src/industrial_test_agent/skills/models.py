from typing import List, Optional

from pydantic import BaseModel


class SkillManifest(BaseModel):
    skill_id: str
    name: str
    version: str
    description: str
    inputs: List[str]
    outputs: List[str]
    allowed_tools: List[str]
    owner: Optional[str] = None
