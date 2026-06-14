import logging
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState
from controllers.NLPController import NLPController
from datetime import datetime

logger = logging.getLogger(__name__)


class ParseEmailNode:
    """
    Parses the initial email to extract key information like the job title.
    This node uses an LLM for robust extraction.
    """

    name = "parse_email"

    def __init__(self, nlp_controller: NLPController):
        self.nlp_controller = nlp_controller

    def execute(self, state: InterviewState) -> InterviewState:
        state.status = InterviewStatusEnum.PARSE_EMAIL.value
        logger.info(f"Parsing email for interview_id: {state.interview_id}")

        try:
            # Use LLM for robust extraction of all key details
            extracted_data = self.nlp_controller.parse_interview_email(
                email_body=state.body,
                email_subject=state.subject
            )

            if not extracted_data:
                logger.warning(f"LLM returned no data for interview_id: {state.interview_id}. Continuing with available info.")
            else:
                if extracted_data.get("job_title"):
                    state.job_title = extracted_data["job_title"]
                    logger.info(f"Extracted job title: {state.job_title}")

                if extracted_data.get("candidate_name"):
                    state.candidate_name = extracted_data["candidate_name"]

                if extracted_data.get("meeting_platform"):
                    state.meeting_platform = extracted_data["meeting_platform"]

                if extracted_data.get("meeting_link"):
                    state.meeting_link = extracted_data["meeting_link"]
                    logger.info(f"Extracted meeting link: {state.meeting_link}")

                if extracted_data.get("interview_datetime"):
                    try:
                        state.interview_datetime = datetime.fromisoformat(extracted_data["interview_datetime"])
                        logger.info(f"Extracted interview datetime: {state.interview_datetime}")
                    except (ValueError, TypeError) as dt_err:
                        logger.warning(f"Could not parse interview_datetime '{extracted_data['interview_datetime']}': {dt_err}")

            # Log warnings for missing optional fields, but do NOT fail
            if not state.job_title:
                logger.warning(f"job_title not found for interview_id: {state.interview_id}. Will use fallback context for question generation.")
            if not state.interview_datetime:
                logger.warning(f"interview_datetime not found for interview_id: {state.interview_id}. Calendar event will be skipped.")

            state.status = InterviewStatusEnum.VALIDATE_INVITATION.value
        except Exception as e:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = f"Failed during email parsing: {e}"

        return state