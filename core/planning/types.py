"""
Webster Alpha

Planning Types
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class PlanStatus(Enum):
    """
    Current lifecycle of a plan.
    """

    CREATED = auto()

    READY = auto()

    RUNNING = auto()

    PAUSED = auto()

    COMPLETED = auto()

    FAILED = auto()

    CANCELLED = auto()


class StepStatus(Enum):
    """
    Current state of a plan step.
    """

    PENDING = auto()

    READY = auto()

    RUNNING = auto()

    COMPLETED = auto()

    FAILED = auto()

    SKIPPED = auto()


class StepType(Enum):
    """
    Type of work performed by a step.
    """

    AI = auto()

    CAPABILITY = auto()

    MEMORY = auto()

    SEARCH = auto()

    USER = auto()

    DECISION = auto()

    PLANNING = auto()

    VALIDATION = auto()

    SYSTEM = auto()


class PlanPriority(Enum):
    """
    Execution priority.
    """

    LOW = auto()

    NORMAL = auto()

    HIGH = auto()

    CRITICAL = auto()


class ExecutionMode(Enum):
    """
    How a plan should execute.
    """

    SEQUENTIAL = auto()

    PARALLEL = auto()

    CONDITIONAL = auto()

    MANUAL = auto()