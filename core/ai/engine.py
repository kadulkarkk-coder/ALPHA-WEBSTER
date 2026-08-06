"""
Webster Alpha

Artificial Intelligence Engine
"""

from __future__ import annotations

from core.ai.request import AIRequest
from core.ai.response import AIResponse

from core.ai.router import IntentRouter

from core.ai.goal_builder import GoalBuilder

from core.ai.response_builder import ResponseBuilder

from core.provider.manager import ProviderManager

from core.planning.engine import PlanningEngine

from core.capability.engine import CapabilityEngine

from core.memory.manager import MemoryManager

from core.conversation.manager import ConversationManager


class AIEngine:
    """
    Webster's central intelligence engine.

    Responsibilities
    ----------------

    • Receive user requests

    • Detect intent

    • Decide AI vs Capability execution

    • Invoke planning

    • Execute capabilities

    • Talk to AI providers

    • Store conversation

    • Build responses
    """

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        provider_manager: ProviderManager,
        planning_engine: PlanningEngine,
        capability_engine: CapabilityEngine,
        memory_manager: MemoryManager,
        conversation_manager: ConversationManager,
        router: IntentRouter,
        goal_builder: GoalBuilder,
        response_builder: ResponseBuilder,
    ) -> None:

        self.provider_manager = provider_manager

        self.planning_engine = planning_engine

        self.capability_engine = capability_engine

        self.memory_manager = memory_manager

        self.conversation_manager = conversation_manager

        self.router = router

        self.goal_builder = goal_builder

        self.response_builder = response_builder

        self.initialized = False

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(
        self,
    ) -> None:
        """
        Initialize the AI engine.
        """

        if self.initialized:

            return

        self.initialized = True

    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the AI engine.
        """

        self.initialized = False

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def chat(
        self,
        message: str,
    ) -> str:
        """
        Main AI entry point.
        """

        response = self.process(

            message

        )

        return response.text

    # ---------------------------------------------------------

    def process(
        self,
        message: str,
    ) -> AIResponse:
        """
        Process a user message.

        Full implementation follows in Part 2.
        """

        raise NotImplementedError

    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {

            "healthy": self.initialized,

            "provider_manager": self.provider_manager.health(),

            "planning_engine": self.planning_engine.health(),

            "capability_engine": self.capability_engine.health(),

            "conversation_manager": self.conversation_manager.health(),

            "memory_manager": self.memory_manager.health(),

        }

    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            "AIEngine("

            f"initialized={self.initialized}"

            ")"

        )

    # ---------------------------------------------------------
    # Processing
    # ---------------------------------------------------------

    def process(
        self,
        message: str,
    ) -> AIResponse:
        """
        Process a user request.
        """

        #
        # Validation
        #

        message = message.strip()

        if not message:

            return AIResponse.error(

                "Message cannot be empty."

            )

        #
        # Store User Message
        #

        self.conversation_manager.add_user_message(

            message

        )

        #
        # Determine Intent
        #

        intent = self.router.route(

            message

        )

        #
        # Conversation Request
        #

        if intent.is_conversation:

            request = AIRequest(

                prompt=message,

                context=self.conversation_manager.context,

            )

            response = self.provider_manager.generate(

                request

            )

        #
        # Capability Request
        #

        else:

            goal = self.goal_builder.build(

                message,

                intent,

            )

            plan = self.planning_engine.create_plan(

                goal

            )

            capability_result = (

                self.capability_engine.execute(

                    plan

                )

            )

            response = self.response_builder.build(

                capability_result

            )

        #
        # Save Conversation
        #

        self.conversation_manager.add_assistant_message(

            response.text

        )

        #
        # Store Memory
        #

        self.memory_manager.store(

            message=message,

            response=response.text,

        )

        return response

    # ---------------------------------------------------------
    # Streaming
    # ---------------------------------------------------------

    def stream(
        self,
        message: str,
    ):
        """
        Stream an AI response.
        """

        request = AIRequest(

            prompt=message,

            context=self.conversation_manager.context,

            stream=True,

        )

        yield from self.provider_manager.stream(

            request

        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def ask(
        self,
        prompt: str,
    ) -> str:

        return self.chat(

            prompt

        )

    # ---------------------------------------------------------

    def execute(
        self,
        command: str,
    ) -> AIResponse:

        return self.process(

            command

        )
