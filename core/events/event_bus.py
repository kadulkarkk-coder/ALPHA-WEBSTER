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

    @property
    def subscriber_count(self) -> int:

        return sum(
            len(handlers)
            for handlers in self._subscribers.values()
        )

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

        for handler in self._subscribers.get(
            event.name,
            []
        ):

            handler.handle(
                event
            )

    def clear(self) -> None:

        self._subscribers.clear()