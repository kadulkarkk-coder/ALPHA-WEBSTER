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

        self._messages = []

        self._initialized = False

        self._handlers = {}
        
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

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the messaging subsystem.

        Messaging currently operates in-process, so there
        are no external connections to establish. This
        method prepares the internal messaging structures
        and marks the subsystem as ready.
        """

        if self._initialized:

            return

        #
        # Ensure internal collections exist.
        #

        if self._messages is None:

            self._messages = []

        if self._handlers is None:

            self._handlers = {}

        #
        # Messaging subsystem is ready.
        #

        self._initialized = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown the messaging subsystem.

        Existing message history is preserved.
        """

        if not self._initialized:

            return

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
        Ensure that messaging is ready before performing
        an operation.
        """

        if not self._initialized:

            raise RuntimeError(

                "MessagingManager has not been "
                "initialized. Call initialize() first."

            )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return messaging subsystem health information.
        """

        return {

            "initialized": self._initialized,

            "healthy": self._initialized,

            "ready": self._initialized,

            "messages": len(
                self._messages
            ),

            "handlers": len(
                self._handlers
            ),

        }

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