import logging
from typing import Dict, Any, List
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from ..interview_state import InterviewState

logger = logging.getLogger(__name__)


class GenerateReportNode:
    """Generate a structured interview report."""

    name = "generate_report"

    def execute(self, state: InterviewState) -> InterviewState:
        """
        Generate a comprehensive interview report.
        """
        state.status = InterviewStatusEnum.GENERATE_REPORT.value

        try:
            report = self._build_report(state)
            state.report = report

            logger.info(
                "Interview report generated: interview_id=%s, decision=%s",
                state.interview_id,
                state.decision,
            )

            state.status = InterviewStatusEnum.SEND_EMAIL_REPORT.value

        except Exception as exc:
            state.status = InterviewStatusEnum.FAILED.value
            state.last_error = f"{self.name} failed: {exc}"
            logger.error(state.last_error)

        return state

    def _build_report(self, state: InterviewState) -> Dict[str, Any]:
        """Build a comprehensive interview report."""
        # The full evaluation from the previous step is now in state.report
        evaluation_data = state.report
        if not evaluation_data or "overall_score" not in evaluation_data:
            raise ValueError("Evaluation data is missing or incomplete in the state.")

        # The LLM already provided these fields in the desired format.
        strengths = evaluation_data.get("strengths", [])
        weaknesses = evaluation_data.get("weaknesses", [])
        summary = evaluation_data.get("feedback", "No summary provided.")

        report = {
            "candidate_name": state.candidate_name or "N/A",
            "job_title": state.job_title or "N/A",
            "interview_date": state.interview_datetime.strftime("%Y-%m-%d") if state.interview_datetime else "N/A",
            "overall_score": round(evaluation_data.get("overall_score", 0.0), 2),
            "final_decision": evaluation_data.get("decision", "N/A"),
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "detailed_scores": evaluation_data.get("scores", {}),
            "questions_and_answers": list(zip(state.questions, state.responses))
        }

        return report
