"""
Webster Alpha

Decision Types
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class DecisionType(Enum):
    """
    The action Webster has decided to take.
    """

    NONE = auto()

    RESPOND = auto()

    EXECUTE = auto()

    PLAN = auto()

    SEARCH = auto()

    REMEMBER = auto()

    RECALL = auto()

    ASK = auto()

    AI = auto()

    REJECT = auto()


class DecisionPriority(Enum):
    """
    Execution priority.
    """

    LOW = auto()

    NORMAL = auto()

    HIGH = auto()

    CRITICAL = auto()


class DecisionSource(Enum):
    """
    Where the decision originated.
    """

    USER = auto()

    SYSTEM = auto()

    POLICY = auto()

    AUTOMATION = auto()

    AI = auto()


class DecisionStatus(Enum):
    """
    Current decision lifecycle.
    """

    CREATED = auto()

    EVALUATING = auto()

    APPROVED = auto()

    EXECUTING = auto()

    COMPLETED = auto()

    FAILED = auto()

    CANCELLED = auto()


class DecisionReason(Enum):
    """
    Why Webster chose this decision.
    """

    USER_REQUEST = auto()

    POLICY_RULE = auto()

    MEMORY_MATCH = auto()

    AUTOMATION_TRIGGER = auto()

    AI_RECOMMENDATION = auto()

    SYSTEM_EVENT = auto()

    UNKNOWN = auto()