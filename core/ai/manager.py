"""
Webster Alpha

AI Manager
"""

from __future__ import annotations

from core.ai.request import AIRequest
from core.ai.response import AIResponse
from core.ai.router import AIRouter


class AIManager:
    """
    Coordinates Webster's AI subsystem.
    """

    def __init__(
        self,
        router: AIRouter
    ) -> None:

        self._router = router

    #
    # ---------------------------------------------------------
    # Request Pipeline
    # ---------------------------------------------------------
    #

    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:
        """
        Process an AI request.
        """

        request.validate()

        provider = self._router.route(
            request
        )

        if provider is None:

            raise RuntimeError(

                "No AI provider is available."

            )

        if not provider.ready:

            provider.initialize()

        if not provider.healthy():

            raise RuntimeError(

                f"{provider.provider.name} is unhealthy."

            )

        return provider.generate(
            request
        )

    #
    # ---------------------------------------------------------
    # Provider Access
    # ---------------------------------------------------------
    #

    @property
    def router(
        self
    ) -> AIRouter:

        return self._router

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def shutdown(
        self
    ) -> None:

        for provider in self._router.providers():

            provider.shutdown()

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "AIManager("

            f"providers={self._router.count}"

            ")"

        )