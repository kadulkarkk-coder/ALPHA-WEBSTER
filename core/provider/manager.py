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

    Responsibilities
    ----------------

    • Provider registration
    • Provider lookup
    • Default provider selection
    • Provider initialization
    • Provider shutdown
    • Provider fallback
    • AI generation
    • Streaming
    • Provider health monitoring
    """

    # =====================================================
    # Construction
    # =====================================================

    def __init__(
        self,
    ) -> None:
        """
        Create the provider manager.

        Providers are registered first and initialized
        later by initialize().
        """

        self._providers: dict[
            str,
            Provider,
        ] = {}

        self._default: str | None = None

        self._initialized = False

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize all enabled providers.

        Initialization is idempotent, meaning calling
        initialize() multiple times does not repeatedly
        initialize providers.
        """

        if self._initialized:

            return

        #
        # Initialize registered providers.
        #

        for provider in self._providers.values():

            if not provider.enabled:

                continue

            provider.initialize()

        #
        # Make sure a default provider exists.
        #

        if self._default is None:

            for provider in self._providers.values():

                if provider.enabled:

                    self._default = (
                        provider.name.lower()
                    )

                    break

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown all registered providers.
        """

        if not self._initialized:

            return

        #
        # Shutdown providers.
        #

        for provider in self._providers.values():

            try:

                provider.shutdown()

            except Exception:
                #
                # One provider failing to shut down should
                # not prevent the remaining providers from
                # being shut down.
                #

                continue

        self._initialized = False

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    @property
    def ready(
        self,
    ) -> bool:

        if not self._initialized:

            return False

        return any(

            provider.available()

            for provider
            in self._providers.values()

        )

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        provider: Provider,
    ) -> None:
        """
        Register an AI provider.

        If the manager has already been initialized,
        the provider is initialized immediately.
        """

        if provider is None:

            raise ValueError(
                "Provider cannot be None."
            )

        name = provider.name.strip().lower()

        if not name:

            raise ValueError(
                "Provider name cannot be empty."
            )

        #
        # Store provider.
        #

        self._providers[name] = provider

        #
        # Automatically select the first provider.
        #

        if self._default is None:

            self._default = name

        #
        # If the manager is already running, initialize
        # the newly registered provider immediately.
        #

        if self._initialized and provider.enabled:

            provider.initialize()

    # -----------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """

        key = name.strip().lower()

        provider = self._providers.pop(

            key,

            None,

        )

        if provider is not None:

            try:

                provider.shutdown()

            except Exception:

                pass

        #
        # Select another provider if the default was removed.
        #

        if self._default == key:

            self._default = None

            for candidate in self._providers.values():

                if candidate.enabled:

                    self._default = (
                        candidate.name.lower()
                    )

                    break

    # =====================================================
    # Lookup
    # =====================================================

    def has(
        self,
        name: str,
    ) -> bool:

        return (

            name.strip().lower()

            in self._providers

        )

    # -----------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Provider:

        key = name.strip().lower()

        try:

            return self._providers[key]

        except KeyError:

            raise KeyError(

                f"Unknown provider '{name}'."

            ) from None

    # -----------------------------------------------------

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

    # -----------------------------------------------------

    def set_default(
        self,
        name: str,
    ) -> None:

        key = name.strip().lower()

        if key not in self._providers:

            raise KeyError(

                f"Unknown provider '{name}'."

            )

        self._default = key

    # =====================================================
    # AI Generation
    # =====================================================

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """
        Generate an AI response.

        Uses the default provider first and automatically
        falls back to another available provider.
        """

        if not self._initialized:

            self.initialize()

        provider = self.default_provider

        #
        # Default provider.
        #

        if provider.available():

            return provider.generate(

                request

            )

        #
        # Fallback providers.
        #

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

    # -----------------------------------------------------

    def stream(
        self,
        request: AIRequest,
    ) -> Iterator[str]:
        """
        Stream an AI response.

        Uses the default provider first and falls back
        to another available provider if necessary.
        """

        if not self._initialized:

            self.initialize()

        provider = self.default_provider

        #
        # Default provider.
        #

        if provider.available():

            yield from provider.stream(

                request

            )

            return

        #
        # Fallback providers.
        #

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

    # =====================================================
    # Information
    # =====================================================

    @property
    def provider_count(
        self,
    ) -> int:

        return len(

            self._providers

        )

    # -----------------------------------------------------

    @property
    def providers(
        self,
    ) -> list[str]:

        return list(

            self._providers.keys()

        )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return provider subsystem health.
        """

        provider_health = {

            name: provider.health()

            for name, provider
            in self._providers.items()

        }

        available = any(

            provider.available()

            for provider
            in self._providers.values()

        )

        return {

            "initialized": self._initialized,

            "healthy": (

                self._initialized
                and available

            ),

            "ready": (

                self._initialized
                and available

            ),

            "default": self._default,

            "providers": provider_health,

            "count": len(
                self._providers
            ),

        }

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            "ProviderManager("

            f"initialized={self._initialized}, "

            f"providers={len(self._providers)}, "

            f"default='{self._default}'"

            ")"

        )