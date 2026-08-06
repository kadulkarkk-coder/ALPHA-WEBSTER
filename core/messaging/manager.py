"""
Messaging Manager
"""

from core.messaging.message import Message
from core.messaging.queue import MessageQueue
from core.messaging.router import MessageRouter


class MessagingManager:
    """
    Controls Webster messaging.
    """

    def __init__(
        self
    ) -> None:

        self._queue = MessageQueue()

        self._router = MessageRouter()

    @property
    def queue(
        self
    ) -> MessageQueue:

        return self._queue

    @property
    def router(
        self
    ) -> MessageRouter:

        return self._router

    def send(
        self,
        message: Message
    ) -> None:

        self._queue.push(
            message
        )

    def process(
        self
    ) -> None:

        while not self._queue.empty():

            message = self._queue.pop()

            self._router.route(
                message
            )

    def clear(
        self
    ) -> None:

        self._queue.clear()