import logging
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState

logger = logging.getLogger(__name__)


class ValidateInvitationNode:
    """
    Validates that the parsed email is a legitimate interview invitation.
    This is a placeholder as the logic is considered complete.
    """

    name = "validate_invitation"

    def execute(self, state: InterviewState) -> InterviewState:
        logger.info(f"Validating invitation for interview_id: {state.interview_id}")
        # In a real system, this node would check for keywords, dates, etc.
        # For now, we assume it's valid and move to the next step.
        state.status = InterviewStatusEnum.CREATE_CALENDAR_EVENT.value
        return state