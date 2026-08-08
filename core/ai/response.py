"""
Webster Alpha

AI Response
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.ai.types import AIProvider


@dataclass(slots=True)
class AIResponse:
    """Represents a response returned by an AI provider."""

    content: str

    provider: AIProvider = AIProvider.WEBSTER

    model: str = "unknown"

    success: bool = True

    latency: float = 0.0

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    finish_reason: str | None = None

    reasoning: str | None = None

    metadata: dict = field(
        default_factory=dict
    )

    @property
    def text(
        self,
    ) -> str:
        """Compatibility alias used by the application layer."""

        return self.content

    @classmethod
    def error(
        cls,
        message: str,
    ) -> "AIResponse":
        """Create a failed response without requiring provider details."""

        return cls(
            content=message,
            provider=AIProvider.WEBSTER,
            model="system",
            success=False,
        )

    def validate(
        self,
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

    @property
    def token_usage(
        self,
    ) -> int:

        if self.total_tokens:

            return self.total_tokens

        return (
            self.prompt_tokens
            + self.completion_tokens
        )

    @property
    def has_reasoning(
        self,
    ) -> bool:

        return self.reasoning is not None

    def __repr__(
        self,
    ) -> str:

        return (
            "AIResponse("
            f"provider={self.provider.name}, "
            f"model='{self.model}', "
            f"success={self.success}"
            ")"
        )
