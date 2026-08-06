"""
Webster Alpha

Memory Types

Defines every category of memory
stored by the Webster Memory Engine.
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class MemoryType(Enum):
    """
    Categories of memory managed by Webster.
    """

    #
    # ---------------------------------------------------------
    # User
    # ---------------------------------------------------------
    #

    PERSONAL = auto()

    PREFERENCE = auto()

    PROFILE = auto()

    CONTACT = auto()

    #
    # ---------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------
    #

    CONVERSATION = auto()

    MESSAGE = auto()

    QUESTION = auto()

    RESPONSE = auto()

    #
    # ---------------------------------------------------------
    # Knowledge
    # ---------------------------------------------------------
    #

    KNOWLEDGE = auto()

    FACT = auto()

    CONCEPT = auto()

    REFERENCE = auto()

    #
    # ---------------------------------------------------------
    # Projects
    # ---------------------------------------------------------
    #

    PROJECT = auto()

    TASK = auto()

    GOAL = auto()

    NOTE = auto()

    DOCUMENT = auto()

    #
    # ---------------------------------------------------------
    # System
    # ---------------------------------------------------------
    #

    CONFIGURATION = auto()

    SYSTEM = auto()

    SESSION = auto()

    LOG = auto()

    #
    # ---------------------------------------------------------
    # AI
    # ---------------------------------------------------------
    #

    AI_CONTEXT = auto()

    AI_RESPONSE = auto()

    AI_PLAN = auto()

    #
    # ---------------------------------------------------------
    # Learning
    # ---------------------------------------------------------
    #

    EXPERIENCE = auto()

    OBSERVATION = auto()

    FEEDBACK = auto()

    CORRECTION = auto()

    #
    # ---------------------------------------------------------
    # Scheduling
    # ---------------------------------------------------------
    #

    CALENDAR = auto()

    REMINDER = auto()

    EVENT = auto()

    #
    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------
    #

    TEMPORARY = auto()

    CACHE = auto()

    LONG_TERM = auto()

    ARCHIVE = auto()

    UNKNOWN = auto()

    @property
    def persistent(self) -> bool:
        """
        Should this memory be stored permanently?
        """

        return self not in {
            MemoryType.TEMPORARY,
            MemoryType.CACHE,
        }

    @property
    def searchable(self) -> bool:
        """
        Can this memory be searched?
        """

        return self not in {
            MemoryType.CACHE,
        }

    @property
    def ai_visible(self) -> bool:
        """
        Can the AI use this memory?
        """

        return self != MemoryType.LOG

    @property
    def user_visible(self) -> bool:
        """
        Should this memory appear in
        user-facing history?
        """

        return self not in {
            MemoryType.LOG,
            MemoryType.SYSTEM,
            MemoryType.CACHE,
        }