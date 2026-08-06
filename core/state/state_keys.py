"""
State Keys
"""

from enum import Enum


class StateKey(str, Enum):
    """
    Built-in Webster state keys.
    """

    APPLICATION = "application"

    RUNTIME = "runtime"

    SERVICES = "services"

    TASKS = "tasks"

    MEMORY = "memory"

    AI = "ai"

    USER = "user"

    SESSION = "session"

    SETTINGS = "settings"

    SYSTEM = "system"