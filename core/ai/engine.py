"""
Webster Alpha

AI Engine

Central orchestration layer for all AI interactions.
"""

from __future__ import annotations

from core.ai.request import AIRequest
from core.ai.response import AIResponse

from core.ai.router import IntentRouter
from core.ai.goal_builder import GoalBuilder
from core.ai.response_builder import ResponseBuilder

from core.provider.manager import ProviderManager

from core.planning.engine import PlanningEngine

from core.conversation.manager import ConversationManager

from core.memory.manager import MemoryManager


class AIEngine:
    """
    Coordinates every AI interaction inside Webster.

    This class never talks directly to the operating system.

    It decides whether a request should

    • generate a conversational response

    • execute a plan

    • invoke capabilities

    and returns a natural language reply.
    """

    def __init__(
        self,
        provider_manager: ProviderManager,
        planning_engine: PlanningEngine,
        conversation_manager: ConversationManager,
        memory_manager: MemoryManager,
        router: IntentRouter,
        goal_builder: GoalBuilder,
        response_builder: ResponseBuilder,
    ) -> None:

        self._providers = provider_manager

        self._planning = planning_engine

        self._conversation = conversation_manager

        self._memory = memory_manager

        self._router = router

        self._goal_builder = goal_builder

        self._response_builder = response_builder

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def chat(
        self,
        message: str,
    ) -> str:
        """
        Primary entry point for Webster.

        Returns a natural language response.
        """

        request = AIRequest(

            prompt=message,

            context=self._conversation.context,

        )

        response = self.process(request)

        return response.text

    # ---------------------------------------------------------

    def process(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """
        Process an AI request.
        """

        request.validate()

        self._conversation.add_user_message(
            request.prompt
        )

        intent = self._router.route(
            request.prompt
        )

        if intent.is_action:

            return self._execute_action(
                request,
                intent,
            )

        return self._generate_chat(
            request
        )

    # ---------------------------------------------------------

    def _generate_chat(
        self,
        request: AIRequest,
    ) -> AIResponse:

        provider = self._providers.default_provider

        response = provider.generate(
            request
        )

        self._conversation.add_assistant_message(
            response.text
        )

        return response

    # ---------------------------------------------------------

    def _execute_action(
        self,
        request: AIRequest,
        intent,
    ) -> AIResponse:

        goal = self._goal_builder.build(
            request.prompt,
            intent,
        )

        result = self._planning.execute_goal(
            goal
        )

        text = self._response_builder.build(
            result
        )

        response = AIResponse(
            text=text
        )

        self._conversation.add_assistant_message(
            response.text
        )

        return response

    # ---------------------------------------------------------

    @property
    def planning_engine(
        self,
    ) -> PlanningEngine:

        return self._planning

    @property
    def provider_manager(
        self,
    ) -> ProviderManager:

        return self._providers

    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {

            "healthy": True,

            "providers": self._providers.health(),

            "planning": self._planning.health(),

            "conversation": True,

            "memory": True,

        }