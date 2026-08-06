"""
Webster Alpha

Conversation Session
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from core.conversation.types import ConversationState
from core.messaging.message import Message


@dataclass(slots=True)
class ConversationSession:
    """
    Represents a single conversation.
    """

    identifier: str = field(
        default_factory=lambda: str(uuid4())
    )

    created: datetime = field(
        default_factory=datetime.now
    )

    updated: datetime = field(
        default_factory=datetime.now
    )

    state: ConversationState = ConversationState.CREATED

    messages: list[Message] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    #
    # ---------------------------------------------------------
    # Message Operations
    # ---------------------------------------------------------
    #

    def add_message(
        self,
        message: Message
    ) -> None:

        self.messages.append(message)

        self.updated = datetime.now()

    def last_message(
        self
    ) -> Message | None:

        if not self.messages:

            return None

        return self.messages[-1]

    def clear(
        self
    ) -> None:

        self.messages.clear()

        self.updated = datetime.now()

    #
    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------
    #

    def activate(
        self
    ) -> None:

        self.state = ConversationState.ACTIVE

    def pause(
        self
    ) -> None:

        self.state = ConversationState.PAUSED

    def finish(
        self
    ) -> None:

        self.state = ConversationState.FINISHED

    def cancel(
        self
    ) -> None:

        self.state = ConversationState.CANCELLED

    #
    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    #

    @property
    def message_count(
        self
    ) -> int:

        return len(self.messages)

    @property
    def active(
        self
    ) -> bool:

        return self.state == ConversationState.ACTIVE

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "ConversationSession("

            f"id={self.identifier}, "

            f"messages={self.message_count}, "

            f"state={self.state.name}"

            ")"

        )