import logging
from datetime import datetime, timedelta
from typing import Optional
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from services.google_calendar_service import GoogleCalendarService
from ..interview_state import InterviewState

logger = logging.getLogger(__name__)


class CreateCalendarEventNode:
    name = "create_calendar_event"

    def __init__(self, settings):
        self.settings = settings
        self.calendar_service: Optional[GoogleCalendarService] = None
        if self.settings.GOOGLE_CALENDAR_CLIENT_SECRETS_FILE:
            try:
                self.calendar_service = GoogleCalendarService(
                    client_secrets_file=self.settings.GOOGLE_CALENDAR_CLIENT_SECRETS_FILE,
                    calendar_id=self.settings.GOOGLE_CALENDAR_ID,
                    token_storage_path=self.settings.GOOGLE_CALENDAR_TOKEN_STORAGE_PATH,
                )
            except Exception as exc:
                logger.error(f"Failed to initialize GoogleCalendarService: {exc}")
                self.calendar_service = None
        else:
            logger.warning(
                "Google Calendar client secret is not configured. Calendar node will use a fallback event id."
            )

    def execute(self, state: InterviewState) -> InterviewState:
        state.status = InterviewStatusEnum.CREATE_CALENDAR_EVENT.value
        try:
            # If no interview datetime was extracted, skip calendar creation entirely
            if state.interview_datetime is None:
                logger.warning(
                    "interview_datetime is None; skipping calendar event creation for interview_id=%s",
                    state.interview_id,
                )
                state.calendar_event_id = state.calendar_event_id or f"local-event-{state.interview_id}"
                state.calendar_event_link = None
                state.calendar_status = "skipped_no_datetime"
                state.status = InterviewStatusEnum.WAITING.value
                return state

            if self.calendar_service:
                start_time = state.interview_datetime
                end_time = start_time + timedelta(hours=1)
                attendees = [state.candidate_email] if state.candidate_email else None
                event_response = None

                if state.calendar_event_id:
                    logger.info(
                        "Updating existing Google Calendar event for interview_id=%s event_id=%s",
                        state.interview_id,
                        state.calendar_event_id,
                    )
                    event_response = self.calendar_service.update_event(
                        event_id=state.calendar_event_id,
                        title=state.subject,
                        description=state.email_content or state.body or "",
                        start_time=start_time,
                        end_time=end_time,
                        attendees=attendees,
                        location=state.meeting_platform or "",
                        meeting_link=state.meeting_link,
                    )
                else:
                    logger.info(
                        "Creating Google Calendar event for interview_id=%s",
                        state.interview_id,
                    )
                    event_response = self.calendar_service.create_event(
                        title=state.subject,
                        description=state.email_content or state.body or "",
                        start_time=start_time,
                        end_time=end_time,
                        attendees=attendees,
                        location=state.meeting_platform or "",
                        meeting_link=state.meeting_link,
                    )

                state.calendar_event_id = event_response.get("event_id")
                state.calendar_event_link = event_response.get("event_link")
                state.calendar_status = event_response.get("status")
                state.scheduled_start_time = self._parse_event_datetime(event_response.get("start_time"))
                state.scheduled_end_time = self._parse_event_datetime(event_response.get("end_time"))
            else:
                logger.warning(
                    "GoogleCalendarService unavailable; creating a fallback local calendar event id for interview_id=%s",
                    state.interview_id,
                )
                state.calendar_event_id = state.calendar_event_id or f"local-event-{state.interview_id}"
                state.calendar_event_link = None
                state.calendar_status = "pending"
                state.scheduled_start_time = state.interview_datetime
                state.scheduled_end_time = state.interview_datetime + timedelta(hours=1)

            state.status = InterviewStatusEnum.WAITING.value
        except Exception as exc:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = f"{self.name} failed: {exc}"
            logger.error(state.last_error)

        return state

    def _parse_event_datetime(self, event_time: Optional[str]) -> Optional[datetime]:
        if not event_time:
            return None
        try:
            dt = event_time
            if dt.endswith("Z"):
                dt = dt.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(dt)
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(tz=None).replace(tzinfo=None)
            return parsed
        except ValueError:
            logger.warning("Unable to parse calendar event datetime: %s", event_time)
            return None
