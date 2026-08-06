"""
Webster Alpha

Component State Machine

Defines every lifecycle state used by
Webster components.
"""

from __future__ import annotations

from enum import Enum
from enum import auto


class ComponentState(
    Enum
):
    """
    Lifecycle states of a component.
    """

    #
    # Creation
    #

    CREATED = auto()

    #
    # Initialization
    #

    INITIALIZING = auto()

    INITIALIZED = auto()

    #
    # Startup
    #

    STARTING = auto()

    RUNNING = auto()

    #
    # Runtime
    #

    PAUSED = auto()

    BUSY = auto()

    IDLE = auto()

    WAITING = auto()

    #
    # Shutdown
    #

    STOPPING = auto()

    STOPPED = auto()

    SHUTDOWN = auto()

    #
    # Error Handling
    #

    WARNING = auto()

    ERROR = auto()

    CRASHED = auto()

    RECOVERING = auto()

    #
    # Administrative
    #

    DISABLED = auto()

    UNKNOWN = auto()

    @property
    def active(
        self
    ) -> bool:
        """
        Component is active.
        """

        return self in {

            ComponentState.RUNNING,

            ComponentState.BUSY,

            ComponentState.IDLE,

            ComponentState.WAITING

        }

    @property
    def alive(
        self
    ) -> bool:
        """
        Component has been started and
        has not yet stopped.
        """

        return self not in {

            ComponentState.CREATED,

            ComponentState.STOPPED,

            ComponentState.SHUTDOWN

        }

    @property
    def failed(
        self
    ) -> bool:
        """
        Component is in a failure state.
        """

        return self in {

            ComponentState.ERROR,

            ComponentState.CRASHED

        }

    @property
    def recoverable(
        self
    ) -> bool:
        """
        Component can be restarted.
        """

        return self in {

            ComponentState.ERROR,

            ComponentState.CRASHED,

            ComponentState.WARNING

        }

    @property
    def terminal(
        self
    ) -> bool:
        """
        Final lifecycle state.
        """

        return self in {

            ComponentState.SHUTDOWN

        }

    @property
    def startup(
        self
    ) -> bool:
        """
        Startup sequence.
        """

        return self in {

            ComponentState.INITIALIZING,

            ComponentState.INITIALIZED,

            ComponentState.STARTING

        }

    @property
    def shutdown_phase(
        self
    ) -> bool:
        """
        Shutdown sequence.
        """

        return self in {

            ComponentState.STOPPING,

            ComponentState.STOPPED,

            ComponentState.SHUTDOWN

        }

    def __str__(
        self
    ) -> str:

        return self.name.lower()