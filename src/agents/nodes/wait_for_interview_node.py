import logging
from datetime import datetime
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState

logger = logging.getLogger(__name__)


class WaitForInterviewNode:
    name = "wait_for_interview"

    def execute(self, state: InterviewState) -> InterviewState:
        state.status = InterviewStatusEnum.WAITING.value

        if state.force_resume:
            logger.info("Interview waiting stage bypassed via force_resume")
            state.status = InterviewStatusEnum.RUN_INTERVIEW_SIMULATION.value
            return state

        if state.interview_datetime is None:
            logger.warning(
                "interview_datetime is None for interview_id=%s; skipping wait and proceeding to interview.",
                state.interview_id,
            )
            state.status = InterviewStatusEnum.RUN_INTERVIEW_SIMULATION.value
            return state

        now = datetime.utcnow()
        delay_seconds = (state.interview_datetime - now).total_seconds()
        if delay_seconds > 0:
            return state

        state.status = InterviewStatusEnum.RUN_INTERVIEW_SIMULATION.value
        return state
