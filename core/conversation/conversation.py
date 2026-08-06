"""
Webster Alpha

Conversation

Public API for the Conversation Engine.
"""

from __future__ import annotations

from core.conversation.context import ConversationContext
from core.conversation.manager import ConversationManager
from core.conversation.session import ConversationSession
from core.memory.manager import MemoryManager
from core.messaging.message import Message


class Conversation:
    """
    Public interface for Webster's
    Conversation Engine.
    """

    def __init__(
        self,
        memory: MemoryManager
    ) -> None:

        self._manager = ConversationManager(
            memory
        )

    #
    # ---------------------------------------------------------
    # Session
    # ---------------------------------------------------------
    #

    def start(
        self
    ) -> ConversationSession:

        return self._manager.start()

    def finish(
        self
    ) -> None:

        self._manager.finish()

    #
    # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------
    #

    def receive(
        self,
        message: Message
    ) -> None:

        self._manager.receive(
            message
        )

    #
    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------
    #

    def context(
        self
    ) -> ConversationContext:

        return self._manager.build_context()

    #
    # ---------------------------------------------------------
    # Session Access
    # ---------------------------------------------------------
    #

    @property
    def session(
        self
    ) -> ConversationSession | None:

        return self._manager.session

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def clear(
        self
    ) -> None:

        self._manager.clear()

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "Conversation("

            f"session={self.session is not None}"

            ")"

        )