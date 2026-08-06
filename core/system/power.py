"""
Power
"""

from enum import Enum


class PowerState(
    Enum
):
    """
    System power states.
    """

    RUNNING = "running"

    SLEEP = "sleep"

    HIBERNATE = "hibernate"

    SHUTDOWN = "shutdown"

    RESTART = "restart"


class Power:
    """
    Stores Webster power state.
    """

    def __init__(
        self
    ) -> None:

        self._state = PowerState.RUNNING

    @property
    def state(
        self
    ) -> PowerState:

        return self._state

    def set_state(
        self,
        state: PowerState
    ) -> None:

        self._state = state