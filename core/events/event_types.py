"""
Webster Alpha

Event Types

Defines every event category used
throughout the Webster Kernel.
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class EventCategory(
    Enum
):
    """
    High-level event categories.
    """

    SYSTEM = auto()

    KERNEL = auto()

    COMPONENT = auto()

    SERVICE = auto()

    CAPABILITY = auto()

    MEMORY = auto()

    DATABASE = auto()

    FILESYSTEM = auto()

    NETWORK = auto()

    AI = auto()

    VOICE = auto()

    VISION = auto()

    PLUGIN = auto()

    AUTOMATION = auto()

    SCHEDULER = auto()

    SECURITY = auto()

    USER = auto()

    UI = auto()

    METRIC = auto()

    LOG = auto()


class EventType(
    Enum
):
    """
    Webster system events.
    """

    #
    # ---------------------------------------------------------
    # SYSTEM
    # ---------------------------------------------------------
    #

    SYSTEM_STARTING = auto()

    SYSTEM_STARTED = auto()

    SYSTEM_STOPPING = auto()

    SYSTEM_STOPPED = auto()

    SYSTEM_RESTARTING = auto()

    SYSTEM_READY = auto()

    #
    # ---------------------------------------------------------
    # KERNEL
    # ---------------------------------------------------------
    #

    KERNEL_INITIALIZING = auto()

    KERNEL_READY = auto()

    KERNEL_SHUTDOWN = auto()

    #
    # ---------------------------------------------------------
    # COMPONENT
    # ---------------------------------------------------------
    #

    COMPONENT_REGISTERED = auto()

    COMPONENT_INITIALIZED = auto()

    COMPONENT_STARTED = auto()

    COMPONENT_PAUSED = auto()

    COMPONENT_RESUMED = auto()

    COMPONENT_STOPPED = auto()

    COMPONENT_SHUTDOWN = auto()

    COMPONENT_ENABLED = auto()

    COMPONENT_DISABLED = auto()

    COMPONENT_FAILED = auto()

    COMPONENT_RECOVERED = auto()

    #
    # ---------------------------------------------------------
    # SERVICE
    # ---------------------------------------------------------
    #

    SERVICE_REGISTERED = auto()

    SERVICE_STARTED = auto()

    SERVICE_STOPPED = auto()

    SERVICE_REMOVED = auto()

    #
    # ---------------------------------------------------------
    # CAPABILITY
    # ---------------------------------------------------------
    #

    CAPABILITY_REGISTERED = auto()

    CAPABILITY_EXECUTED = auto()

    CAPABILITY_FAILED = auto()

    #
    # ---------------------------------------------------------
    # MEMORY
    # ---------------------------------------------------------
    #

    MEMORY_CREATED = auto()

    MEMORY_UPDATED = auto()

    MEMORY_DELETED = auto()

    MEMORY_SEARCHED = auto()

    #
    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------
    #

    DATABASE_CONNECTED = auto()

    DATABASE_DISCONNECTED = auto()

    DATABASE_ERROR = auto()

    #
    # ---------------------------------------------------------
    # FILESYSTEM
    # ---------------------------------------------------------
    #

    FILE_CREATED = auto()

    FILE_MODIFIED = auto()

    FILE_DELETED = auto()

    DIRECTORY_CREATED = auto()

    #
    # ---------------------------------------------------------
    # NETWORK
    # ---------------------------------------------------------
    #

    NETWORK_CONNECTED = auto()

    NETWORK_DISCONNECTED = auto()

    NETWORK_TIMEOUT = auto()

    NETWORK_ERROR = auto()

    #
    # ---------------------------------------------------------
    # AI
    # ---------------------------------------------------------
    #

    AI_REQUEST = auto()

    AI_RESPONSE = auto()

    AI_STREAM_STARTED = auto()

    AI_STREAM_FINISHED = auto()

    AI_MODEL_CHANGED = auto()

    PLANNING_STARTED = auto()

    PLANNING_COMPLETED = auto()

    WORKFLOW_STARTED = auto()

    WORKFLOW_COMPLETED = auto()

    #
    # ---------------------------------------------------------
    # VOICE
    # ---------------------------------------------------------
    #

    VOICE_LISTENING = auto()

    VOICE_RECOGNIZED = auto()

    VOICE_SYNTHESIS = auto()

    #
    # ---------------------------------------------------------
    # VISION
    # ---------------------------------------------------------
    #

    CAMERA_STARTED = auto()

    CAMERA_STOPPED = auto()

    OBJECT_DETECTED = auto()

    FACE_DETECTED = auto()

    GESTURE_DETECTED = auto()

    #
    # ---------------------------------------------------------
    # PLUGINS
    # ---------------------------------------------------------
    #

    PLUGIN_LOADED = auto()

    PLUGIN_UNLOADED = auto()

    PLUGIN_FAILED = auto()

    #
    # ---------------------------------------------------------
    # AUTOMATION
    # ---------------------------------------------------------
    #

    AUTOMATION_STARTED = auto()

    AUTOMATION_FINISHED = auto()

    AUTOMATION_FAILED = auto()

    #
    # ---------------------------------------------------------
    # SECURITY
    # ---------------------------------------------------------
    #

    LOGIN = auto()

    LOGOUT = auto()

    AUTH_FAILED = auto()

    PERMISSION_DENIED = auto()

    #
    # ---------------------------------------------------------
    # USER
    # ---------------------------------------------------------
    #

    USER_COMMAND = auto()

    USER_MESSAGE = auto()

    USER_NOTIFICATION = auto()

    #
    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    #

    UI_OPENED = auto()

    UI_CLOSED = auto()

    UI_UPDATED = auto()

    #
    # ---------------------------------------------------------
    # LOGGING
    # ---------------------------------------------------------
    #

    DEBUG = auto()

    INFO = auto()

    WARNING = auto()

    ERROR = auto()

    CRITICAL = auto()


class EventPriority(
    Enum
):
    """
    Event processing priority.
    """

    LOW = auto()

    NORMAL = auto()

    HIGH = auto()

    CRITICAL = auto()


class EventScope(
    Enum
):
    """
    Event visibility.
    """

    LOCAL = auto()

    GLOBAL = auto()

    BROADCAST = auto()