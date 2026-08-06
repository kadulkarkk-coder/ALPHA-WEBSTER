"""
Webster Alpha

AI Request
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.ai.types import AIProvider
from core.ai.types import ResponseMode

from core.conversation.context import ConversationContext


@dataclass(slots=True)
class AIRequest:
    """
    Represents a single AI request.
    """

    #
    # User Prompt
    #

    prompt: str

    #
    # AI Context
    #

    context: ConversationContext

    #
    # Provider
    #

    provider: AIProvider | None = None

    #
    # Response Mode
    #

    mode: ResponseMode = ResponseMode.CHAT

    #
    # Runtime
    #

    stream: bool = False

    temperature: float = 0.7

    max_tokens: int | None = None

    timeout: float = 60.0

    #
    # Metadata
    #

    metadata: dict = field(
        default_factory=dict
    )

    #
    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    #

    def validate(
        self
    ) -> None:

        if not self.prompt.strip():

            raise ValueError(

                "Prompt cannot be empty."

            )

        if not 0.0 <= self.temperature <= 2.0:

            raise ValueError(

                "Temperature must be between 0.0 and 2.0."

            )

        if self.max_tokens is not None:

            if self.max_tokens <= 0:

                raise ValueError(

                    "max_tokens must be greater than zero."

                )

        if self.timeout <= 0:

            raise ValueError(

                "timeout must be greater than zero."

            )

    #
    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    #

    @property
    def has_provider(
        self
    ) -> bool:

        return self.provider is not None

    @property
    def has_context(
        self
    ) -> bool:

        return (

            self.context.message_count > 0

            or

            self.context.memory_count > 0

        )

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "AIRequest("

            f"provider={self.provider}, "

            f"mode={self.mode.name}"

            ")"

        )