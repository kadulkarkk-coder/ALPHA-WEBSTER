"""
Webster Alpha

Capability Types
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class CapabilityType(Enum):
    """
    Type of capability.
    """

    SYSTEM = auto()

    APPLICATION = auto()

    FILE = auto()

    MEMORY = auto()

    AI = auto()

    SEARCH = auto()

    WEB = auto()

    VOICE = auto()

    VISION = auto()

    AUTOMATION = auto()

    PLUGIN = auto()


class CapabilityCategory(Enum):
    """
    Logical grouping for capabilities.
    """

    CORE = auto()

    PRODUCTIVITY = auto()

    MULTIMEDIA = auto()

    DEVELOPMENT = auto()

    COMMUNICATION = auto()

    INTERNET = auto()

    SYSTEM = auto()

    CUSTOM = auto()


class CapabilityStatus(Enum):
    """
    Current capability state.
    """

    AVAILABLE = auto()

    BUSY = auto()

    DISABLED = auto()

    UNAVAILABLE = auto()

    ERROR = auto()


class CapabilityPriority(Enum):
    """
    Execution priority.
    """

    LOW = auto()

    NORMAL = auto()

    HIGH = auto()

    CRITICAL = auto()


class CapabilityPermission(Enum):
    """
    Permissions required to execute
    a capability.
    """

    NONE = auto()

    FILE_SYSTEM = auto()

    NETWORK = auto()

    MICROPHONE = auto()

    CAMERA = auto()

    CLIPBOARD = auto()

    NOTIFICATIONS = auto()

    SYSTEM_CONTROL = auto()

    PROCESS_CONTROL = auto()


class CapabilityResultStatus(Enum):
    """
    Execution result.
    """

    SUCCESS = auto()

    FAILURE = auto()

    PARTIAL = auto()

    CANCELLED = auto()

    TIMEOUT = auto()