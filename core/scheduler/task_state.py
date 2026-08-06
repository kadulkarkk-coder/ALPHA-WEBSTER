"""
Task State
"""

from enum import Enum, auto


class TaskState(Enum):
    """
    Lifecycle state of a scheduled task.
    """

    CREATED = auto()

    WAITING = auto()

    RUNNING = auto()

    PAUSED = auto()

    COMPLETED = auto()

    CANCELLED = auto()

    FAILED = auto()