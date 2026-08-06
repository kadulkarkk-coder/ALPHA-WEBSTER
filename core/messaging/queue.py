"""
Message Queue
"""

from collections import deque

from core.messaging.message import Message


class MessageQueue:
    """
    FIFO queue for Webster messages.
    """

    def __init__(
        self
    ) -> None:

        self._queue: deque[
            Message
        ] = deque()

    @property
    def count(
        self
    ) -> int:

        return len(
            self._queue
        )

    def push(
        self,
        message: Message
    ) -> None:

        self._queue.append(
            message
        )

    def pop(
        self
    ) -> Message:

        return self._queue.popleft()

    def empty(
        self
    ) -> bool:

        return len(
            self._queue
        ) == 0

    def clear(
        self
    ) -> None:

        self._queue.clear()