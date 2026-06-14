from fastapi import APIRouter, Body, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from helpers.config import get_settings, settings
from controllers.InterviewController import InterviewController
from models.enums.InterviewStatusEnum import InterviewStatusEnum

class InterviewEmailPayload(BaseModel):
    subject: str
    body: str
    from_email: EmailStr
    candidate_email: EmailStr | None = None

class SubmitAnswersPayload(BaseModel):
    answers: list[str] = Field(..., min_items=1)


class ResumeInterviewPayload(BaseModel):
    force_resume: bool = False

    class Config:
        schema_extra = {
            "example": {
                "force_resume": True,
            }
        }


interview_router = APIRouter(
    prefix="/api/v1/interview",
    tags=["api_v1", "interview"],
)

@interview_router.post("/trigger")
async def trigger_interview(request: Request, payload: InterviewEmailPayload, app_settings: settings = Depends(get_settings)):
    controller = InterviewController(db_client=request.app.db_client, settings=app_settings)
    state = await controller.trigger_interview(
        subject=payload.subject,
        body=payload.body,
        from_email=str(payload.from_email),
        candidate_email=str(payload.candidate_email) if payload.candidate_email else None,
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"interview_id": state.interview_id, "status": state.status})

@interview_router.get("/{interview_id}")
async def get_interview_status(request: Request, interview_id: str, app_settings: settings = Depends(get_settings)):
    controller = InterviewController(db_client=request.app.db_client, settings=app_settings)
    interview = await controller.get_interview(interview_id=interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview workflow not found")
    return {
        "interview_id": interview.interview_id,
        "status": interview.status,
        "interview_datetime": interview.interview_datetime,
        "meeting_platform": interview.meeting_platform,
        "meeting_link": interview.meeting_link,
        "calendar_event_id": interview.calendar_event_id,
        "calendar_event_link": interview.calendar_event_link,
        "calendar_status": interview.calendar_status,
        "scheduled_start_time": interview.scheduled_start_time,
        "scheduled_end_time": interview.scheduled_end_time,
        "questions": interview.questions,
        "responses": interview.responses,
        "evaluation_scores": interview.evaluation_scores,
        "report": interview.report,
        "email_sent": interview.email_sent,
        "email_sent_at": interview.email_sent_at,
        "force_resume": interview.force_resume,
        "retry_count": interview.retry_count,
        "current_step": interview.current_step,
        "last_error": interview.last_error,
    }

@interview_router.post(
    "/{interview_id}/resume",
    summary="Resume an interview workflow",
    description="Resume a paused workflow. In development/testing, pass force_resume=true to bypass WAITING without editing MongoDB dates.",
)
async def resume_interview(
    request: Request,
    interview_id: str,
    payload: ResumeInterviewPayload | None = Body(
        default=None,
        examples={
            "normal_resume": {
                "summary": "Production resume",
                "description": "Keep normal waiting behavior.",
                "value": {"force_resume": False},
            },
            "force_resume": {
                "summary": "Development/testing bypass",
                "description": "Bypass WAITING and continue to the mock interview stages.",
                "value": {"force_resume": True},
            },
        },
    ),
    app_settings: settings = Depends(get_settings),
):
    controller = InterviewController(db_client=request.app.db_client, settings=app_settings)
    interview = await controller.get_interview(interview_id=interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview workflow not found")
    force_resume = payload.force_resume if payload else False
    state = await controller.resume_workflow(interview, force_resume=force_resume)
    return {
        "interview_id": state.interview_id,
        "status": state.status,
        "force_resume": state.force_resume,
        "current_step": state.current_step,
        "last_error": state.last_error,
    }

@interview_router.post("/{interview_id}/retry")
async def retry_interview(request: Request, interview_id: str, app_settings: settings = Depends(get_settings)):
    controller = InterviewController(db_client=request.app.db_client, settings=app_settings)
    interview = await controller.get_interview(interview_id=interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview workflow not found")
    if interview.status != InterviewStatusEnum.FAILED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only failed interviews can be retried")
    state = await controller.retry_workflow(interview)
    return {"interview_id": state.interview_id, "status": state.status, "retry_count": state.retry_count, "current_step": state.current_step, "last_error": state.last_error}

@interview_router.post("/{interview_id}/submit-answers")
async def submit_answers(
    request: Request,
    interview_id: str,
    payload: SubmitAnswersPayload,
    app_settings: settings = Depends(get_settings),
):
    """
    Submit candidate's answers to the generated questions and resume the workflow.
    """
    controller = InterviewController(db_client=request.app.db_client, settings=app_settings)
    interview = await controller.get_interview(interview_id=interview_id)
    if interview is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview workflow not found")

    state = await controller.submit_answers(interview, payload.answers)

    return {
        "interview_id": state.interview_id,
        "status": state.status,
        "current_step": state.current_step,
    }
