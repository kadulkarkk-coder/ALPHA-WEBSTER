"""
Webster Alpha

Provider Manager
"""

from __future__ import annotations

from typing import Iterator

from core.provider.provider import Provider

from core.ai.request import AIRequest
from core.ai.response import AIResponse


class ProviderManager:
    """
    Manages all AI providers.

    Responsible for

    • registration

    • lookup

    • provider selection

    • fallback

    • health monitoring

    • AI generation
    """

    def __init__(self) -> None:

        self._providers: dict[str, Provider] = {}

        self._default: str | None = None

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        provider: Provider,
    ) -> None:
        """
        Register an AI provider.
        """

        self._providers[
            provider.name.lower()
        ] = provider

        if self._default is None:

            self._default = provider.name.lower()

    # ---------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:

        name = name.lower()

        self._providers.pop(
            name,
            None,
        )

        if self._default == name:

            self._default = None

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def has(
        self,
        name: str,
    ) -> bool:

        return name.lower() in self._providers

    # ---------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Provider:

        return self._providers[
            name.lower()
        ]

    # ---------------------------------------------------------

    @property
    def default_provider(
        self,
    ) -> Provider:

        if self._default is None:

            raise RuntimeError(

                "No default AI provider configured."

            )

        return self._providers[
            self._default
        ]

    # ---------------------------------------------------------

    def set_default(
        self,
        name: str,
    ) -> None:

        name = name.lower()

        if name not in self._providers:

            raise KeyError(

                f"Unknown provider '{name}'."

            )

        self._default = name

    # ---------------------------------------------------------
    # AI
    # ---------------------------------------------------------

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """
        Generate a response.

        Automatically falls back
        to another provider if the
        default provider is unavailable.
        """

        provider = self.default_provider

        if provider.available():

            return provider.generate(
                request
            )

        for candidate in self._providers.values():

            if candidate.available():

                self._default = (
                    candidate.name.lower()
                )

                return candidate.generate(
                    request
                )

        raise RuntimeError(

            "No AI providers are available."

        )

    # ---------------------------------------------------------

    def stream(
        self,
        request: AIRequest,
    ) -> Iterator[str]:

        provider = self.default_provider

        if provider.available():

            yield from provider.stream(
                request
            )

            return

        for candidate in self._providers.values():

            if candidate.available():

                self._default = (
                    candidate.name.lower()
                )

                yield from candidate.stream(
                    request
                )

                return

        raise RuntimeError(

            "No AI providers are available."

        )

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(
        self,
    ) -> None:

        for provider in self._providers.values():

            if provider.enabled:

                provider.initialize()

    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:

        for provider in self._providers.values():

            provider.shutdown()

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    @property
    def provider_count(
        self,
    ) -> int:

        return len(
            self._providers
        )

    @property
    def providers(
        self,
    ) -> list[str]:

        return list(
            self._providers.keys()
        )

    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:

        return {

            "healthy": any(

                provider.available()

                for provider in self._providers.values()

            ),

            "default": self._default,

            "providers": {

                name: provider.health()

                for name, provider in self._providers.items()

            },

            "count": len(

                self._providers

            ),

        }

    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            "ProviderManager("

            f"providers={len(self._providers)}, "

            f"default='{self._default}'"

            ")"

        )