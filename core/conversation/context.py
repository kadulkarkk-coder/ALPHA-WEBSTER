"""
Webster Alpha

Conversation Context
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.memory.record import MemoryRecord
from core.messaging.message import Message


@dataclass(slots=True)
class ConversationContext:
    """
    Context supplied to the AI.
    """

    #
    # Current conversation
    #

    messages: list[Message] = field(
        default_factory=list
    )

    #
    # Relevant memories
    #

    memories: list[MemoryRecord] = field(
        default_factory=list
    )

    #
    # Current project
    #

    project: str | None = None

    #
    # Active task
    #

    task: str | None = None

    #
    # User intent
    #

    intent: str | None = None

    #
    # Extra runtime information
    #

    metadata: dict = field(
        default_factory=dict
    )

    #
    # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------
    #

    def add_message(
        self,
        message: Message
    ) -> None:

        self.messages.append(
            message
        )

    #
    # ---------------------------------------------------------
    # Memory
    # ---------------------------------------------------------
    #

    def add_memory(
        self,
        memory: MemoryRecord
    ) -> None:

        self.memories.append(
            memory
        )

    #
    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------
    #

    def clear(
        self
    ) -> None:

        self.messages.clear()

        self.memories.clear()

        self.metadata.clear()

        self.project = None

        self.task = None

        self.intent = None

    #
    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    #

    @property
    def message_count(
        self
    ) -> int:

        return len(
            self.messages
        )

    @property
    def memory_count(
        self
    ) -> int:

        return len(
            self.memories
        )

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "ConversationContext("

            f"messages={self.message_count}, "

            f"memories={self.memory_count}"

            ")"

        )