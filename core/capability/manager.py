"""
Webster Alpha

Capability Manager
"""

from __future__ import annotations

from core.capability.capability import Capability
from core.capability.executor import CapabilityExecutor
from core.capability.registry import CapabilityRegistry
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult


class CapabilityManager:
    """
    Coordinates Webster's
    Capability subsystem.
    """

    def __init__(
        self,
        registry: CapabilityRegistry | None = None,
        executor: CapabilityExecutor | None = None,
    ) -> None:

        self._registry = (
            registry
            or
            CapabilityRegistry()
        )

        self._executor = (
            executor
            or
            CapabilityExecutor(
                self._registry
            )
        )

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        capability: Capability,
    ) -> None:

        self._registry.register(
            capability
        )

    def unregister(
        self,
        name: str,
    ) -> None:

        self._registry.unregister(
            name
        )

    #
    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    #

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        return self._executor.execute(
            request
        )

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str,
    ) -> Capability | None:

        return self._registry.get(
            name
        )

    def exists(
        self,
        name: str,
    ) -> bool:

        return self._registry.exists(
            name
        )

    def capabilities(
        self,
    ) -> tuple[Capability, ...]:

        return self._registry.all()

    def names(
        self,
    ) -> tuple[str, ...]:

        return self._registry.names()

    #
    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------
    #

    @property
    def registry(
        self,
    ) -> CapabilityRegistry:

        return self._registry

    @property
    def executor(
        self,
    ) -> CapabilityExecutor:

        return self._executor

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self,
    ) -> str:

        return (

            "CapabilityManager("

            f"capabilities={len(self.registry)}"

            ")"

        )