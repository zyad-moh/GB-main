from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
from datetime import datetime

from ..enums.InterviewStatusEnum import InterviewStatusEnum

class Interview(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    interview_id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    from_email: EmailStr
    candidate_email: Optional[EmailStr] = None
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    interview_datetime: Optional[datetime] = None
    meeting_platform: Optional[str] = None
    meeting_link: Optional[str] = None
    calendar_event_id: Optional[str] = None
    calendar_event_link: Optional[str] = None
    calendar_status: Optional[str] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    status: str = Field(default=InterviewStatusEnum.START.value)
    validation_score: Optional[float] = None
    questions: List[str] = Field(default_factory=list)
    responses: List[str] = Field(default_factory=list)
    evaluation_scores: Dict[str, float] = Field(default_factory=dict)
    overall_score: Optional[float] = None
    decision: Optional[str] = None
    report: Optional[Dict[str, Any]] = None
    email_sent: Optional[bool] = None
    email_sent_at: Optional[datetime] = None
    force_resume: bool = False
    retry_count: int = 0
    last_error: Optional[str] = None
    current_step: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("interview_id")
    def validate_interview_id(cls, value):
        if not value.isalnum():
            raise ValueError("interview_id must be alphanumeric")
        return value

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("interview_id", 1)],
                "name": "interview_id_index_1",
                "unique": True,
            }
        ]
