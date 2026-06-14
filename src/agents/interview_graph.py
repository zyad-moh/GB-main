import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from models.enums.InterviewStatusEnum import InterviewStatusEnum
from controllers.NLPController import NLPController
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from .interview_state import InterviewState
from .nodes.parse_email_node import ParseEmailNode
from .nodes.validate_invitation_node import ValidateInvitationNode
from .nodes.create_calendar_event_node import CreateCalendarEventNode
from .nodes.wait_for_interview_node import WaitForInterviewNode
from .nodes.run_ai_interview_node import RunAiInterviewNode
from .nodes.evaluate_candidate_node import EvaluateCandidateNode
from .nodes.generate_report_node import GenerateReportNode
from .nodes.send_email_node import SendEmailNode

logger = logging.getLogger(__name__)


class GraphNode:
    name: str

    def execute(self, state: InterviewState) -> InterviewState:
        raise NotImplementedError


class InterviewGraph:
    def __init__(self, settings):
        self.settings = settings

        # Initialize dependencies for nodes
        llm_provider_factory = LLMProviderFactory(settings)
        generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
        generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
        template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)

        # The NLPController holds all our AI logic
        nlp_controller = NLPController(
            vectordb_client=None,  # Not needed for this workflow
            generation_client=generation_client,
            embedding_client=None, # Not needed for this workflow
            template_parser=template_parser,
        )

        self.nodes: List[GraphNode] = [
            ParseEmailNode(nlp_controller=nlp_controller),
            ValidateInvitationNode(),
            CreateCalendarEventNode(settings=self.settings),
            WaitForInterviewNode(),
            RunAiInterviewNode(nlp_controller=nlp_controller),
            EvaluateCandidateNode(nlp_controller=nlp_controller),
            GenerateReportNode(),
            SendEmailNode(settings=self.settings),
        ]
        self.step_index: Dict[str, int] = {node.name: index for index, node in enumerate(self.nodes)}
        self.status_to_step = {
            InterviewStatusEnum.START.value: 0,
            InterviewStatusEnum.PARSE_EMAIL.value: 0,
            InterviewStatusEnum.VALIDATE_INVITATION.value: 1,
            InterviewStatusEnum.CREATE_CALENDAR_EVENT.value: 2,
            InterviewStatusEnum.WAITING.value: 3,
            InterviewStatusEnum.AWAITING_RESPONSES.value: 5,  # When resuming, start at EvaluateCandidateNode
            InterviewStatusEnum.CREATE_JOIN_MEETING.value: 4, # Keeping for compatibility
            InterviewStatusEnum.RUN_INTERVIEW_SIMULATION.value: 4,
            InterviewStatusEnum.EVALUATE_CANDIDATE.value: 5,
            InterviewStatusEnum.GENERATE_REPORT.value: 6,
            InterviewStatusEnum.SEND_EMAIL_REPORT.value: 7,
            InterviewStatusEnum.COMPLETED.value: 7,
            InterviewStatusEnum.FAILED.value: 0,
        }

    def _resolve_start_index(self, state: InterviewState, resume: bool) -> int:
        status_index = self.status_to_step.get(state.status, 0)
        if resume and state.current_step in self.step_index:
            return max(self.step_index[state.current_step], status_index)
        return status_index

    def _set_current_step(self, state: InterviewState, new_step: Optional[str]) -> None:
        old_step = state.current_step
        if old_step != new_step:
            logger.info(f"Transition: {old_step} -> {new_step}")
        state.current_step = new_step

    def _next_step_for_status(self, state: InterviewState, current_index: int) -> Optional[str]:
        if state.status in {InterviewStatusEnum.FAILED.value, InterviewStatusEnum.COMPLETED.value}:
            return state.current_step

        next_index = self.status_to_step.get(state.status)
        if next_index is None:
            next_index = current_index + 1

        if next_index < len(self.nodes):
            return self.nodes[next_index].name

        return state.current_step

    async def execute(
        self,
        state: InterviewState,
        persist_state: Callable[[InterviewState], Any],
        resume: bool = False,
    ) -> InterviewState:
        start_index = self._resolve_start_index(state, resume)
        for index, node in enumerate(self.nodes[start_index:], start=start_index):
            self._set_current_step(state, node.name)
            state.touch()
            try:
                state = node.execute(state)
            except Exception as exc:
                state.status = InterviewStatusEnum.FAILED.value
                state.last_error = f"{node.name} failed: {exc}"
                state.touch()
                result = persist_state(state)
                if asyncio.iscoroutine(result):
                    await result
                return state

            self._set_current_step(state, self._next_step_for_status(state, index))
            state.touch()
            result = persist_state(state)
            if asyncio.iscoroutine(result):
                await result

            if state.status in {InterviewStatusEnum.FAILED.value, InterviewStatusEnum.WAITING.value, InterviewStatusEnum.AWAITING_RESPONSES.value, InterviewStatusEnum.COMPLETED.value}:
                return state

        return state
