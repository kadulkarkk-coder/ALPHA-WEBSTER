"""
Event Bus
"""

from collections import defaultdict

from core.events.event import Event
from core.events.event_handler import EventHandler


class EventBus:
    """
    Webster Event Bus.
    """

    def __init__(self) -> None:

        self._subscribers: dict[
            str,
            list[EventHandler]
        ] = defaultdict(list)

        self._initialized = False

        self._handlers = {}

    @property
    def subscriber_count(self) -> int:

        return sum(
            len(handlers)
            for handlers in self._subscribers.values()
        )

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the Webster event bus.

        The EventBus is an in-process subsystem, so no
        external connection is required.
        """

        if self._initialized:

            return

        #
        # Make sure the internal subscriber/handler
        # collection exists.
        #

        if self._handlers is None:

            self._handlers = {}

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the EventBus.

        Existing subscriptions are removed because they
        belong to the current runtime session.
        """

        if not self._initialized:

            return

        self._handlers.clear()

        self._initialized = False

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(
        self,
    ) -> bool:

        return self._initialized

    # -----------------------------------------------------

    @property
    def ready(
        self,
    ) -> bool:

        return self._initialized

    # =====================================================
    # Internal Validation
    # =====================================================

    def _ensure_initialized(
        self,
    ) -> None:
        """
        Ensure the EventBus is ready.
        """

        if not self._initialized:

            raise RuntimeError(

                "EventBus has not been initialized. "
                "Call initialize() first."

            )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return EventBus health information.
        """

        return {

            "initialized": self._initialized,

            "healthy": self._initialized,

            "ready": self._initialized,

            "handlers": len(
                self._handlers
            ),

        }

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler
    ) -> None:

        self._subscribers[event_name].append(
            handler
        )

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler
    ) -> None:

        if (
            event_name in self._subscribers
            and handler in self._subscribers[event_name]
        ):

            self._subscribers[event_name].remove(
                handler
            )

    def publish(
        self,
        event: Event
    ) -> None:

        self._ensure_initialized()

        for handler in self._subscribers.get(
            event.name,
            []
        ):

            handler.handle(
                event
            )

    def clear(self) -> None:

        self._subscribers.clear()