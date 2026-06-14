from fastapi import APIRouter, HTTPException, Request, status


email_ingestion_router = APIRouter(
    prefix="/api/v1/email-ingestion",
    tags=["api_v1", "email_ingestion"],
)


@email_ingestion_router.get("/status")
async def get_email_ingestion_status(request: Request):
    service = getattr(request.app, "gmail_ingestion_service", None)
    task = getattr(request.app, "gmail_ingestion_task", None)

    if service is None:
        return {
            "enabled": False,
            "running": False,
            "message": "Gmail ingestion service is not configured or not started.",
        }

    status_payload = await service.status()
    status_payload["running"] = task is not None and not task.done()
    return status_payload


@email_ingestion_router.post("/poll-now")
async def poll_email_ingestion_now(request: Request):
    service = getattr(request.app, "gmail_ingestion_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gmail ingestion service is not configured or not started.",
        )

    return await service.poll_once()
