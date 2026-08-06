"""
Service State
"""

from enum import Enum, auto


class ServiceState(Enum):
    """
    Service lifecycle states.
    """

    CREATED = auto()

    STARTING = auto()

    RUNNING = auto()

    STOPPING = auto()

    STOPPED = auto()

    FAILED = auto()