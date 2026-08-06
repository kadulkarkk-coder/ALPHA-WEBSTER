"""
Webster Alpha

AI

Public API for Webster's
AI subsystem.
"""

from __future__ import annotations

from core.ai.manager import AIManager
from core.ai.request import AIRequest
from core.ai.response import AIResponse
from core.ai.router import AIRouter
from core.ai.provider import BaseAIProvider


class AI:
    """
    Public interface to Webster's
    AI subsystem.
    """

    def __init__(
        self,
        router: AIRouter | None = None
    ) -> None:

        self._router = router or AIRouter()

        self._manager = AIManager(
            self._router
        )

    #
    # ---------------------------------------------------------
    # Requests
    # ---------------------------------------------------------
    #

    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:

        return self._manager.generate(
            request
        )

    #
    # ---------------------------------------------------------
    # Providers
    # ---------------------------------------------------------
    #

    def register(
        self,
        provider: BaseAIProvider
    ) -> None:

        self._router.register(
            provider
        )

    def unregister(
        self,
        provider
    ) -> None:

        self._router.unregister(
            provider
        )

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def manager(
        self
    ) -> AIManager:

        return self._manager

    @property
    def router(
        self
    ) -> AIRouter:

        return self._router

    #
    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------
    #

    def shutdown(
        self
    ) -> None:

        self._manager.shutdown()

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "AI("

            f"providers={self.router.count}"

            ")"

        )