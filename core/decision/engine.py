"""
Webster Alpha

Decision Engine

Public API for Webster's
Decision subsystem.
"""

from __future__ import annotations

from core.ai.request import AIRequest

from core.decision.decision import Decision
from core.decision.manager import DecisionManager


class DecisionEngine:
    """
    Public interface to Webster's
    Decision subsystem.
    """

    def __init__(
        self,
        manager: DecisionManager | None = None
    ) -> None:

        self._manager = (
            manager
            or
            DecisionManager()
        )

    #
    # ---------------------------------------------------------
    # Decision
    # ---------------------------------------------------------
    #

    def decide(
        self,
        request: AIRequest
    ) -> Decision:

        return self._manager.decide(
            request
        )

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def manager(
        self
    ) -> DecisionManager:

        return self._manager

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def configure(
        self,
        **settings
    ) -> None:
        """
        Update policy configuration.
        """

        configuration = (
            self._manager
            .policy
            .configuration
        )

        for key, value in settings.items():

            if hasattr(
                configuration,
                key
            ):

                setattr(
                    configuration,
                    key,
                    value
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

            "DecisionEngine("

            f"manager={self.manager!r}"

            ")"

        )