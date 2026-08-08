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
    """Webster's central intelligence engine."""

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
        self._initialized = False

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:

        if self._initialized:

            return

        self._initialized = True

    def shutdown(
        self,
    ) -> None:

        self._initialized = False

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    # =====================================================
    # Public API
    # =====================================================

    def chat(
        self,
        message: str,
    ) -> str:

        response = self.process(message)

        return response.text

    def ask(
        self,
        prompt: str,
    ) -> str:

        return self.chat(prompt)

    def execute(
        self,
        command: str,
    ) -> AIResponse:

        return self.process(command)

    # =====================================================
    # Processing
    # =====================================================

    def process(
        self,
        message: str,
    ) -> AIResponse:
        """Process a user request through chat or planning."""

        if not self._initialized:

            self.initialize()

        message = str(message).strip()

        if not message:

            return AIResponse.error(
                "Message cannot be empty."
            )

        self.conversation_manager.add_user_message(
            message
        )

        intent = self.router.route(
            message
        )

        # -------------------------------------------------
        # Conversational / question request
        # -------------------------------------------------

        if intent.is_chat or intent.is_question:

            request = AIRequest(
                prompt=message,
                context=self.conversation_manager.context,
            )

            response = self.provider_manager.generate(
                request
            )

        # -------------------------------------------------
        # Capability / workflow request
        # -------------------------------------------------

        else:

            goal = self.goal_builder.build(
                message,
                intent,
            )

            result = self.planning_engine.execute_goal(
                goal
            )

            response_text = self.response_builder.build(
                result
            )

            response = AIResponse(
                content=response_text,
                success=getattr(
                    result,
                    "success",
                    True,
                ),
            )

        self.conversation_manager.add_assistant_message(
            response.text
        )

        return response

    # =====================================================
    # Streaming
    # =====================================================

    def stream(
        self,
        message: str,
    ):
        """Stream a response from the active provider."""

        message = str(message).strip()

        if not message:

            raise ValueError(
                "Message cannot be empty."
            )

        if not self._initialized:

            self.initialize()

        self.conversation_manager.add_user_message(
            message
        )

        request = AIRequest(
            prompt=message,
            context=self.conversation_manager.context,
            stream=True,
        )

        chunks = []

        for chunk in self.provider_manager.stream(
            request
        ):

            chunks.append(chunk)
            yield chunk

        if chunks:

            self.conversation_manager.add_assistant_message(
                "".join(chunks)
            )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:

        return {
            "initialized": self._initialized,
            "healthy": (
                self._initialized
                and self.provider_manager.ready
            ),
            "provider_manager": self.provider_manager.health(),
            "planning_engine": self.planning_engine.health(),
            "capability_engine": self.capability_engine.health(),
            "conversation_manager": self.conversation_manager.health(),
            "memory_manager": self.memory_manager.health(),
        }

    def __repr__(
        self,
    ) -> str:

        return (
            "AIEngine("
            f"initialized={self._initialized}"
            ")"
        )
