from .BaseController import BaseController
from models.InterviewModel import InterviewModel
from models.db_schemes import Interview
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from agents.interview_graph import InterviewGraph
from agents.interview_state import InterviewState
from datetime import datetime
from typing import Optional, List


class InterviewController(BaseController):
    def __init__(self, db_client: object, settings):
        super().__init__()
        self.db_client = db_client
        self.settings = settings
        self.graph = InterviewGraph(settings=settings)

    async def create_interview_record(self, state: InterviewState) -> InterviewState:
        interview_model = await InterviewModel.create_instance(db_client=self.db_client)
        interview = await interview_model.create_interview(interview=state.to_interview())
        state.id = interview.id
        state.created_at = interview.created_at
        state.updated_at = interview.updated_at
        return state

    async def update_interview_record(self, state: InterviewState) -> InterviewState:
        interview_model = await InterviewModel.create_instance(db_client=self.db_client)
        state.touch()
        await interview_model.update_interview(interview=state.to_interview())
        return state

    async def persist_state(self, state: InterviewState) -> InterviewState:
        return await self.update_interview_record(state)

    async def trigger_interview(
        self,
        subject: str,
        body: str,
        from_email: str,
        candidate_email: Optional[str] = None,
    ) -> InterviewState:
        state = InterviewState.create_initial(
            interview_id=self.generate_random_string(16),
            subject=subject,
            body=body,
            from_email=from_email,
            candidate_email=candidate_email,
        )
        state = await self.create_interview_record(state)
        state = await self.graph.execute(state, persist_state=self.persist_state, resume=False)
        return state

    async def get_interview(self, interview_id: str) -> Optional[Interview]:
        interview_model = await InterviewModel.create_instance(db_client=self.db_client)
        return await interview_model.get_interview_by_id(interview_id=interview_id)

    async def resume_workflow(self, interview: Interview, force_resume: bool = False) -> InterviewState:
        state = InterviewState.from_interview(interview)
        state.last_error = None
        state.force_resume = force_resume
        return await self.graph.execute(state, persist_state=self.persist_state, resume=True)

    async def retry_workflow(self, interview: Interview) -> InterviewState:
        state = InterviewState.from_interview(interview)
        state.last_error = None
        state.retry_count += 1
        return await self.graph.execute(state, persist_state=self.persist_state, resume=True)

    async def submit_answers(self, interview: Interview, answers: List[str]) -> InterviewState:
        state = InterviewState.from_interview(interview)

        if state.status != InterviewStatusEnum.AWAITING_RESPONSES.value:
            raise Exception(f"Cannot submit answers when interview status is '{state.status}'")

        if len(answers) != len(state.questions):
            raise Exception(f"Number of answers ({len(answers)}) does not match number of questions ({len(state.questions)})")

        state.responses = answers
        # Set the status to the next logical step before resuming
        state.status = InterviewStatusEnum.EVALUATE_CANDIDATE.value
        state.last_error = None

        # Resume the graph execution, which will now start from the 'evaluate_candidate' node
        return await self.graph.execute(state, persist_state=self.persist_state, resume=True)
