"""
Webster Alpha

AI Response
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.ai.types import AIProvider


@dataclass(slots=True)
class AIResponse:
    """
    Represents a response returned
    by an AI provider.
    """

    #
    # Response
    #

    content: str

    #
    # Provider
    #

    provider: AIProvider

    model: str

    #
    # Status
    #

    success: bool = True

    #
    # Performance
    #

    latency: float = 0.0

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    #
    # Optional Information
    #

    finish_reason: str | None = None

    reasoning: str | None = None

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

        if self.latency < 0:

            raise ValueError(

                "Latency cannot be negative."

            )

        if self.prompt_tokens < 0:

            raise ValueError(

                "prompt_tokens cannot be negative."

            )

        if self.completion_tokens < 0:

            raise ValueError(

                "completion_tokens cannot be negative."

            )

        if self.total_tokens < 0:

            raise ValueError(

                "total_tokens cannot be negative."

            )

    #
    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    #

    @property
    def token_usage(
        self
    ) -> int:

        if self.total_tokens:

            return self.total_tokens

        return (

            self.prompt_tokens

            +

            self.completion_tokens

        )

    @property
    def has_reasoning(
        self
    ) -> bool:

        return self.reasoning is not None

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "AIResponse("

            f"provider={self.provider.name}, "

            f"model='{self.model}', "

            f"success={self.success}"

            ")"

        )