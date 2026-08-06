"""
Webster Alpha

Conversation Types
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class Speaker(Enum):
    """
    Who created the message.
    """

    USER = auto()

    ASSISTANT = auto()

    SYSTEM = auto()

    PLUGIN = auto()

    SERVICE = auto()


class ConversationState(Enum):
    """
    Current state of a conversation.
    """

    CREATED = auto()

    ACTIVE = auto()

    WAITING = auto()

    PROCESSING = auto()

    PAUSED = auto()

    FINISHED = auto()

    CANCELLED = auto()


class IntentType(Enum):
    """
    High-level intent category.

    These are NOT the final AI intents.
    They are broad classifications.
    """

    UNKNOWN = auto()

    CHAT = auto()

    QUESTION = auto()

    COMMAND = auto()

    SEARCH = auto()

    TASK = auto()

    AUTOMATION = auto()

    FILESYSTEM = auto()

    SYSTEM = auto()

    CONFIGURATION = auto()


class ResponseType(Enum):
    """
    How Webster should respond.
    """

    TEXT = auto()

    ACTION = auto()

    QUESTION = auto()

    ERROR = auto()

    CONFIRMATION = auto()

    NOTIFICATION = auto()