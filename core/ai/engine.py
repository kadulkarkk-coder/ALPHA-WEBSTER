"""Webster Alpha - Artificial Intelligence Engine."""

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
        self._pending_confirmation: str | None = None

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    def shutdown(self) -> None:
        self._pending_confirmation = None
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def chat(self, message: str) -> str:
        return self.process(message).text

    def ask(self, prompt: str) -> str:
        return self.chat(prompt)

    def execute(self, command: str) -> AIResponse:
        return self.process(command)

    def _chat_with_provider(self, message: str) -> AIResponse:
        request = AIRequest(
            prompt=message,
            context=self.conversation_manager.context,
        )
        return self.provider_manager.generate(request)

    def process(self, message: str) -> AIResponse:
        """Process conversational requests and validated executable goals."""
        if not self._initialized:
            self.initialize()

        message = str(message).strip()
        if not message:
            return AIResponse.error("Message cannot be empty.")

        self.conversation_manager.add_user_message(message)

        # Resolve a pending destructive-operation confirmation before routing
        # the answer as ordinary chat.
        if self._pending_confirmation is not None:
            normalized = message.lower().strip()
            if normalized in {"yes", "y", "confirm", "confirmed", "do it", "yes, delete"}:
                original = self._pending_confirmation
                self._pending_confirmation = None
                message = original + " confirmed"
            elif normalized in {"no", "n", "cancel", "stop", "don't", "do not"}:
                self._pending_confirmation = None
                response = AIResponse(content="Okay. I cancelled the pending file operation.", success=True)
                self.conversation_manager.add_assistant_message(response.text)
                return response

        intent = self.router.route(message)

        if intent.is_chat or intent.is_question:
            response = self._chat_with_provider(message)
        elif intent.is_action and intent.action is None:
            # A generic action without a known executable capability is not a
            # valid plan. Keep it conversational instead of creating an empty
            # plan that will fail strict validation.
            response = self._chat_with_provider(message)
        else:
            # Destructive filesystem operations require an explicit second
            # user turn. This prevents a natural-language misclassification
            # from deleting files immediately.
            if intent.action == "delete_file" and "confirmed" not in message.lower():
                self._pending_confirmation = message
                response = AIResponse(
                    content="I found a file operation that would delete data. "
                    "Please confirm by replying 'yes' or cancel with 'no'.",
                    success=True,
                )
            else:
                goal = self.goal_builder.build(message, intent)
                result = self.planning_engine.execute_goal(goal)
                response_text = self.response_builder.build(result)
                response = AIResponse(
                    content=response_text,
                    success=getattr(result, "success", True),
                )

        self.conversation_manager.add_assistant_message(response.text)
        return response

    def stream(self, message: str):
        """Stream a conversational response from the active provider."""
        message = str(message).strip()
        if not message:
            raise ValueError("Message cannot be empty.")
        if not self._initialized:
            self.initialize()

        self.conversation_manager.add_user_message(message)
        request = AIRequest(
            prompt=message,
            context=self.conversation_manager.context,
            stream=True,
        )
        chunks = []
        for chunk in self.provider_manager.stream(request):
            chunks.append(chunk)
            yield chunk
        if chunks:
            self.conversation_manager.add_assistant_message("".join(chunks))

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "healthy": self._initialized and self.provider_manager.ready,
            "pending_confirmation": self._pending_confirmation is not None,
            "provider_manager": self.provider_manager.health(),
            "planning_engine": self.planning_engine.health(),
            "capability_engine": self.capability_engine.health(),
            "conversation_manager": self.conversation_manager.health(),
            "memory_manager": self.memory_manager.health(),
        }

    def __repr__(self) -> str:
        return f"AIEngine(initialized={self._initialized})"
