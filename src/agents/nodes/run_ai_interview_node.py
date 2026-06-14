import logging
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState
from controllers.NLPController import NLPController

logger = logging.getLogger(__name__)


class RunAiInterviewNode:
    """
    Generates dynamic interview questions using an LLM based on the job title
    and then pauses the workflow to await candidate responses.
    """

    name = "run_ai_interview"

    def __init__(self, nlp_controller: NLPController):
        self.nlp_controller = nlp_controller

    def execute(self, state: InterviewState) -> InterviewState:
        logger.info(f"Generating AI interview questions for interview_id: {state.interview_id}")

        try:
            # Determine the best context for question generation
            if state.job_title:
                context = state.job_title
                source = "job_title"
            elif state.subject:
                context = state.subject
                source = "email_subject"
            elif state.body:
                context = state.body
                source = "email_body"
            else:
                context = "General Interview"
                source = "fallback"

            # Generate questions using the LLM
            questions = self.nlp_controller.generate_interview_questions(context)
            state.questions = questions
            logger.info(f"Generated {len(questions)} questions using context from '{source}' for role/subject: '{context[:100]}...'")

            # Set status to pause and wait for candidate answers to be submitted
            state.status = InterviewStatusEnum.AWAITING_RESPONSES.value
            return state  # Explicitly return to pause the graph
        except Exception as e:
            state.status = InterviewStatusEnum.FAILED.value
            error_message = f"Failed to generate interview questions: {e}"
            state.last_error = error_message
            logger.error(f"Error in {self.name} for interview {state.interview_id}: {error_message}")

        return state