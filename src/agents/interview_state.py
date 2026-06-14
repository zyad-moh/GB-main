from datetime import datetime
from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
from pydantic import BaseModel, EmailStr, Field
from models.db_schemes.interview import Interview
from models.enums.InterviewStatusEnum import InterviewStatusEnum


class InterviewState(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    interview_id: str
    subject: str
    body: str
    email_content: Optional[str] = None
    from_email: EmailStr
    candidate_email: Optional[EmailStr] = None
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    interview_datetime: Optional[datetime] = None
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    meeting_platform: Optional[str] = None
    meeting_link: Optional[str] = None
    calendar_event_id: Optional[str] = None
    calendar_event_link: Optional[str] = None
    calendar_status: Optional[str] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    status: str = InterviewStatusEnum.START.value
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

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    @classmethod
    def create_initial(
        cls,
        interview_id: str,
        subject: str,
        body: str,
        from_email: str,
        candidate_email: Optional[str] = None,
    ) -> "InterviewState":
        email_content = f"{subject}\n{body}".strip()
        return cls(
            interview_id=interview_id,
            subject=subject,
            body=body,
            email_content=email_content,
            from_email=from_email,
            candidate_email=candidate_email,
            status=InterviewStatusEnum.START.value,
        )

    @classmethod
    def from_interview(cls, interview: Interview) -> "InterviewState":
        data = interview.dict(by_alias=True, exclude_none=False)
        if interview.interview_datetime:
            data["interview_date"] = interview.interview_datetime.strftime("%Y-%m-%d")
            data["interview_time"] = interview.interview_datetime.strftime("%H:%M")
        data["email_content"] = f"{interview.subject}\n{interview.body}".strip()
        return cls(**data)

    def to_interview(self) -> Interview:
        fields = self.dict(by_alias=True, exclude_none=True, exclude={"email_content", "interview_date", "interview_time"})
        return Interview(**fields)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
