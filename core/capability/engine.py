"""
Webster Alpha

Capability Engine

Public API
"""

from __future__ import annotations

from core.capability.capability import Capability
from core.capability.manager import CapabilityManager
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.events.event import Event
from core.events.event_bus import EventBus
from core.events.event_types import EventType


class CapabilityEngine:
    """
    Public interface to Webster's
    Capability subsystem.
    """

    def __init__(
        self,

        manager: CapabilityManager,
        event_bus: EventBus | None = None,
    ) -> None:

        if manager is None:
            raise ValueError("CapabilityEngine requires a CapabilityManager to be injected")

        self._manager = manager
        self._event_bus = event_bus
        # execution statistics
        self._execution_count: int = 0
        self._success_count: int = 0
        self._failure_count: int = 0

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        capability: Capability,
    ) -> None:
        """
        Register a capability.
        """

        self._manager.register(capability)

    def discover_and_register(self, register_callable) -> None:
        """Register capabilities using a pack's register(registry) callable."""

        register_callable(self._manager.registry)

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a capability.
        """

        self._manager.unregister(
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
        """
        Execute a capability request.
        """

        # Ensure capability exists
        try:
            cap = self._manager.registry.require(request.capability)
        except KeyError as err:
            return CapabilityResult.failure_result(error=str(err))

        if not cap.can_execute(request):
            return CapabilityResult.failure_result(error=f"Capability '{request.capability}' cannot execute the request")

        import time

        start = time.time()

        try:
            result = self._manager.execute(request)

            duration = time.time() - start

            self._execution_count += 1

            if result.success:
                self._success_count += 1
            else:
                self._failure_count += 1

            if hasattr(result, "metadata") and isinstance(result.metadata, dict):
                result.metadata["duration"] = duration

            if self._event_bus is not None:
                self._event_bus.publish(
                    Event(
                        name=EventType.CAPABILITY_EXECUTED.name,
                        source="capability_engine",
                        data={
                            "capability": request.capability,
                            "action": request.action,
                            "success": result.success,
                            "duration": duration,
                        },
                    )
                )

            return result

        except Exception as error:
            duration = time.time() - start

            self._execution_count += 1

            self._failure_count += 1

            if self._event_bus is not None:
                self._event_bus.publish(
                    Event(
                        name=EventType.CAPABILITY_FAILED.name,
                        source="capability_engine",
                        data={
                            "capability": request.capability,
                            "action": request.action,
                            "error": str(error),
                            "duration": duration,
                        },
                    )
                )

            return CapabilityResult.failure_result(error=str(error), duration=duration)

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str,
    ) -> Capability | None:

        return self._manager.get(
            name
        )

    def exists(
        self,
        name: str,
    ) -> bool:

        return self._manager.exists(
            name
        )

    def capabilities(
        self,
    ) -> tuple[Capability, ...]:

        return self._manager.capabilities()

    def names(
        self,
    ) -> tuple[str, ...]:

        return self._manager.names()

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def manager(
        self,
    ) -> CapabilityManager:

        return self._manager

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def capability_count(
        self,
    ) -> int:

        return len(
            self._manager.registry
        )

    #
    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------
    #

    def health(self) -> dict:

        return {
            "registered": self.capability_count(),
            "categories": self._manager.registry.list_categories(),
            "executions": self._execution_count,
            "successes": self._success_count,
            "failures": self._failure_count,
        }

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self,
    ) -> str:

        return (

            "CapabilityEngine("

            f"capabilities={self.capability_count()}"

            ")"

        )