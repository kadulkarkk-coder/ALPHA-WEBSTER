"""
Message Router
"""

from typing import Callable

from core.messaging.message import Message


class MessageRouter:
    """
    Routes messages to registered handlers.
    """

    def __init__(
        self
    ) -> None:

        self._routes: dict[
            str,
            Callable[[Message], None]
        ] = {}

    def register(
        self,
        name: str,
        handler: Callable[[Message], None]
    ) -> None:

        self._routes[
            name
        ] = handler

    def unregister(
        self,
        name: str
    ) -> None:

        self._routes.pop(
            name,
            None
        )

    def route(
        self,
        message: Message
    ) -> None:

        handler = self._routes.get(
            message.receiver
        )

        if handler is not None:

            handler(
                message
            )