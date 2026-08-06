"""
Webster Alpha

Conversation Manager
"""

from __future__ import annotations

from core.conversation.context import ConversationContext
from core.conversation.history import ConversationHistory
from core.conversation.session import ConversationSession
from core.events.event_bus import EventBus
from core.events.event import Event
from core.events.event_types import EventType
from core.memory.manager import MemoryManager
from core.messaging.message import Message


class ConversationManager:
    """
    Coordinates conversation sessions.
    """

    def __init__(
        self,
        memory: MemoryManager,
        event_bus: EventBus | None = None,
    ) -> None:

        self._memory = memory

        self._event_bus = event_bus

        self._session: ConversationSession | None = None

    #
    # ---------------------------------------------------------
    # Session
    # ---------------------------------------------------------
    #

    def start(self) -> ConversationSession:

        self._session = ConversationSession()

        self._session.activate()

        return self._session

    @property
    def session(
        self
    ) -> ConversationSession | None:

        return self._session

    #
    # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------
    #

    def receive(
        self,
        message: Message
    ) -> None:

        if self._session is None:

            self.start()

        self._session.history.append(
            message
        )

        if self._event_bus is not None:
            self._event_bus.publish(
                Event(
                    name=EventType.CONVERSATION_UPDATED.name,
                    source="conversation_manager",
                    data={
                        "sender": message.sender,
                        "receiver": message.receiver,
                        "payload": message.payload,
                    },
                )
            )

    #
    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------
    #

    def build_context(
        self
    ) -> ConversationContext:

        context = ConversationContext()

        if self._session is None:

            return context

        #
        # Recent messages
        #

        for message in self._session.history.last(10):

            context.add_message(
                message
            )

        if self._event_bus is not None:
            self._event_bus.publish(
                Event(
                    name=EventType.CONVERSATION_UPDATED.name,
                    source="conversation_manager",
                    data={
                        "message_count": self._session.history.count,
                    },
                )
            )

        #
        # Memory retrieval
        # (implemented later)
        #

        return context

    #
    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------
    #

    def finish(
        self
    ) -> None:

        if self._session:

            self._session.finish()

    def clear(
        self
    ) -> None:

        self._session = None

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        state = "active" if self._session else "idle"

        return (

            "ConversationManager("

            f"{state}"

            ")"

        )