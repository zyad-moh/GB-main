from pydantic import BaseModel
from typing import Optional
from typing import List
class PushRequest(BaseModel):
    do_reset : Optional[int] = 0

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5
class SkillRequest(BaseModel):
    user_skill: List[str]

class Skill_gap_Request(BaseModel):
    user_gap_skill: List[str]

class RunAllRequest(BaseModel):
    skill_request: SkillRequest
    gap_request: Skill_gap_Request