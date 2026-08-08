"""
Webster Alpha

Capability Engine

Public API
"""

from __future__ import annotations

import time

from core.capability.capability import Capability
from core.capability.manager import CapabilityManager
from core.capability.registry import CapabilityRegistry
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.events.event import Event
from core.events.event_bus import EventBus
from core.events.event_types import EventType


class CapabilityEngine:
    """Public interface to Webster's Capability subsystem."""

    def __init__(
        self,
        manager: CapabilityManager,
        event_bus: EventBus | None = None,
        registry: CapabilityRegistry | None = None,
    ) -> None:

        if manager is None:

            raise ValueError(
                "CapabilityEngine requires a CapabilityManager."
            )

        self._initialized = False
        self._manager = manager
        self._event_bus = event_bus
        self._registry = registry or manager.registry
        self._execution_count = 0
        self._success_count = 0
        self._failure_count = 0

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

        return (
            self._initialized
            and self._registry is not None
        )

    @property
    def registry(
        self,
    ) -> CapabilityRegistry:

        return self._registry

    @property
    def manager(
        self,
    ) -> CapabilityManager:

        return self._manager

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:

        if self._initialized:
            return

        if self._registry is None:

            raise RuntimeError(
                "CapabilityEngine requires a CapabilityRegistry."
            )

        self._initialized = True

    def shutdown(
        self,
    ) -> None:

        if not self._initialized:
            return

        self._initialized = False

    def _ensure_initialized(
        self,
    ) -> None:

        if not self._initialized:

            raise RuntimeError(
                "CapabilityEngine has not been initialized. "
                "Call initialize() first."
            )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:

        return {
            "initialized": self._initialized,
            "healthy": self.ready,
            "ready": self.ready,
            "capabilities": self.capability_count(),
            "executions": self._execution_count,
            "successes": self._success_count,
            "failures": self._failure_count,
        }

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        capability: Capability,
    ) -> None:

        self._manager.register(capability)

    def discover_and_register(
        self,
        register_callable,
    ) -> None:

        register_callable(
            self._manager.registry
        )

    def unregister(
        self,
        name: str,
    ) -> None:

        self._manager.unregister(name)

    # =====================================================
    # Execution
    # =====================================================

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        self._ensure_initialized()

        try:

            cap = self._manager.registry.require(
                request.capability
            )

        except KeyError as error:

            self._failure_count += 1

            return CapabilityResult.failure_result(
                error=str(error)
            )

        if not cap.can_execute(request):

            self._failure_count += 1

            return CapabilityResult.failure_result(
                error=(
                    f"Capability '{request.capability}' "
                    "cannot execute the request"
                )
            )

        started = time.time()

        try:

            result = self._manager.execute(request)

            duration = time.time() - started

            self._execution_count += 1

            if result.success:
                self._success_count += 1
            else:
                self._failure_count += 1

            if isinstance(
                getattr(result, "metadata", None),
                dict,
            ):

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

            duration = time.time() - started

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

            return CapabilityResult.failure_result(
                error=str(error),
                duration=duration,
            )

    # =====================================================
    # Lookup
    # =====================================================

    def get(
        self,
        name: str,
    ) -> Capability | None:

        return self._manager.get(name)

    def exists(
        self,
        name: str,
    ) -> bool:

        return self._manager.exists(name)

    def capabilities(
        self,
    ) -> tuple[Capability, ...]:

        return self._manager.capabilities()

    def names(
        self,
    ) -> tuple[str, ...]:

        return self._manager.names()

    def capability_count(
        self,
    ) -> int:

        return len(self._manager.registry)

    def __repr__(
        self,
    ) -> str:

        return (
            "CapabilityEngine("
            f"capabilities={self.capability_count()}"
            ")"
        )
