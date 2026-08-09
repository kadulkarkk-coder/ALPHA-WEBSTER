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
    """Webster's intelligence layer.

    Deterministic computer commands are handled by CommandEngine first.
    The LLM is used for conversation and questions, not for basic tool routing.
    """

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
        command_engine=None,
    ) -> None:
        self.provider_manager = provider_manager
        self.planning_engine = planning_engine
        self.capability_engine = capability_engine
        self.memory_manager = memory_manager
        self.conversation_manager = conversation_manager
        self.router = router
        self.goal_builder = goal_builder
        self.response_builder = response_builder
        self.command_engine = command_engine
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
        request = AIRequest(prompt=message, context=self.conversation_manager.context)
        return self.provider_manager.generate(request)

    def process(self, message: str) -> AIResponse:
        if not self._initialized:
            self.initialize()

        message = str(message).strip()
        if not message:
            return AIResponse.error("Message cannot be empty.")

        self.conversation_manager.add_user_message(message)

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

        # Part 1: execute every recognized, registered single command directly.
        # This completely removes the empty-plan failure from ordinary commands.
        if self.command_engine is not None and self.command_engine.can_handle(message):
            if intent.action == "delete_file" and "confirmed" not in message.lower():
                self._pending_confirmation = message
                response = AIResponse(
                    content="I found a file operation that would delete data. Please confirm by replying 'yes' or cancel with 'no'.",
                    success=True,
                )
            else:
                try:
                    text = self.command_engine.execute(message)
                    response = AIResponse(content=text, success=True)
                except Exception as error:
                    response = AIResponse.error(str(error))
        elif intent.is_chat or intent.is_question:
            response = self._chat_with_provider(message)
        elif intent.is_action:
            # Don't manufacture an empty plan. Explain that no executable
            # capability is currently registered for this command.
            action = intent.action or "unknown"
            available = ", ".join(self.capability_engine.names())
            response = AIResponse.error(
                f"No registered capability can execute this command (requested: {action}). "
                f"Available capabilities: {available or 'none'}."
            )
        else:
            response = self._chat_with_provider(message)

        self.conversation_manager.add_assistant_message(response.text)
        return response

    def stream(self, message: str):
        message = str(message).strip()
        if not message:
            raise ValueError("Message cannot be empty.")
        if not self._initialized:
            self.initialize()

        self.conversation_manager.add_user_message(message)
        request = AIRequest(prompt=message, context=self.conversation_manager.context, stream=True)
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
            "command_engine": self.command_engine.health() if self.command_engine else {"healthy": False},
            "provider_manager": self.provider_manager.health(),
            "planning_engine": self.planning_engine.health(),
            "capability_engine": self.capability_engine.health(),
            "conversation_manager": self.conversation_manager.health(),
            "memory_manager": self.memory_manager.health(),
        }

    def __repr__(self) -> str:
        return f"AIEngine(initialized={self._initialized})"
