"""
Event Handler
"""

from abc import ABC, abstractmethod

from core.events.event import Event


class EventHandler(ABC):
    """
    Base event handler.
    """

    @abstractmethod
    def handle(
        self,
        event: Event
    ) -> None:
        """
        Handle an event.
        """