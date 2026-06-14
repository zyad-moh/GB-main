import logging
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState
from controllers.NLPController import NLPController

logger = logging.getLogger(__name__)


class EvaluateCandidateNode:
    """
    Evaluates the candidate's simulated interview performance using an LLM.
    """

    name = "evaluate_candidate"

    def __init__(self, nlp_controller: NLPController):
        self.nlp_controller = nlp_controller

    def execute(self, state: InterviewState) -> InterviewState:
        state.status = InterviewStatusEnum.EVALUATE_CANDIDATE.value
        logger.info(f"Evaluating candidate for interview_id: {state.interview_id}")

        if not state.questions or not state.responses:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = "Cannot evaluate: No questions or responses found in state."
            return state

        try:
            evaluation = self.nlp_controller.evaluate_interview(state.questions, state.responses)

            state.evaluation_scores = evaluation.get("scores", {})
            state.overall_score = evaluation.get("overall_score")
            state.decision = evaluation.get("decision")
            state.report = evaluation  # Store the full evaluation object in the report field for now

            state.status = InterviewStatusEnum.GENERATE_REPORT.value
        except Exception as e:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = f"Candidate evaluation failed: {e}"

        return state