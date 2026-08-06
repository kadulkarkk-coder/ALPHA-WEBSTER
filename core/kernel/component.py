"""
Webster Alpha

Component System

Every major Webster subsystem inherits
from this class.

The Kernel manages Components instead
of individual managers.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from datetime import datetime

from typing import Any

from core.kernel.component_state import ComponentState


class Component(
    ABC
):
    """
    Base component.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0"
    ) -> None:

        self._name = name

        self._version = version

        self._state = ComponentState.CREATED

        self._enabled = True

        self._created = datetime.now()

        self._started: datetime | None = None

        self._stopped: datetime | None = None

        self._last_error: Exception | None = None

    #
    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------
    #

    @property
    def name(
        self
    ) -> str:

        return self._name

    @property
    def version(
        self
    ) -> str:

        return self._version

    @property
    def state(
        self
    ) -> ComponentState:

        return self._state

    @property
    def enabled(
        self
    ) -> bool:

        return self._enabled

    @property
    def created(
        self
    ) -> datetime:

        return self._created

    @property
    def started(
        self
    ) -> datetime | None:

        return self._started

    @property
    def stopped(
        self
    ) -> datetime | None:

        return self._stopped

    @property
    def last_error(
        self
    ) -> Exception | None:

        return self._last_error

    #
    # ---------------------------------------------------------
    # State Management
    # ---------------------------------------------------------
    #

    def enable(
        self
    ) -> None:

        self._enabled = True

    def disable(
        self
    ) -> None:

        self._enabled = False

    def _set_state(
        self,
        state: ComponentState
    ) -> None:

        self._state = state

    #
    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------
    #

    def initialize(
        self
    ) -> None:

        self._set_state(
            ComponentState.INITIALIZING
        )

        try:

            self.on_initialize()

            self._set_state(
                ComponentState.INITIALIZED
            )

        except Exception as exc:

            self._last_error = exc

            self._set_state(
                ComponentState.ERROR
            )

            raise

    def start(
        self
    ) -> None:

        self._set_state(
            ComponentState.STARTING
        )

        try:

            self.on_start()

            self._started = datetime.now()

            self._set_state(
                ComponentState.RUNNING
            )

        except Exception as exc:

            self._last_error = exc

            self._set_state(
                ComponentState.ERROR
            )

            raise

    def pause(
        self
    ) -> None:

        self.on_pause()

        self._set_state(
            ComponentState.PAUSED
        )

    def resume(
        self
    ) -> None:

        self.on_resume()

        self._set_state(
            ComponentState.RUNNING
        )

    def stop(
        self
    ) -> None:

        self._set_state(
            ComponentState.STOPPING
        )

        self.on_stop()

        self._stopped = datetime.now()

        self._set_state(
            ComponentState.STOPPED
        )

    def shutdown(
        self
    ) -> None:

        self.on_shutdown()

        self._set_state(
            ComponentState.SHUTDOWN
        )

    #
    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------
    #

    def healthy(
        self
    ) -> bool:

        return (

            self._state

            !=

            ComponentState.ERROR

        )

    def info(
        self
    ) -> dict[
        str,
        Any
    ]:

        return {

            "name": self.name,

            "version": self.version,

            "state": self.state.name,

            "enabled": self.enabled,

            "healthy": self.healthy(),

            "created": self.created,

            "started": self.started,

            "stopped": self.stopped,

            "last_error": (
                str(self.last_error)
                if self.last_error
                else None
            )

        }

    #
    # ---------------------------------------------------------
    # Hooks
    # ---------------------------------------------------------
    #

    @abstractmethod
    def on_initialize(
        self
    ) -> None:

        pass

    @abstractmethod
    def on_start(
        self
    ) -> None:

        pass

    @abstractmethod
    def on_pause(
        self
    ) -> None:

        pass

    @abstractmethod
    def on_resume(
        self
    ) -> None:

        pass

    @abstractmethod
    def on_stop(
        self
    ) -> None:

        pass

    @abstractmethod
    def on_shutdown(
        self
    ) -> None:

        pass

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(name='{self.name}', "

            f"state='{self.state.name}')"

        )