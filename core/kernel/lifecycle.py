"""
Webster Alpha

Lifecycle Manager

The only component allowed to change
the lifecycle state of Webster Components.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from core.kernel.component import Component
from core.kernel.component_registry import ComponentRegistry
from core.kernel.component_state import ComponentState


@dataclass(slots=True)
class Transition:

    component: str

    previous: ComponentState

    current: ComponentState

    timestamp: datetime = field(
        default_factory=datetime.now
    )


class Lifecycle:
    """
    Webster Lifecycle Manager.
    """

    def __init__(
        self,
        registry: ComponentRegistry
    ) -> None:

        self._registry = registry

        self._history: list[
            Transition
        ] = []

    #
    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------
    #

    def _transition(
        self,
        component: Component,
        state: ComponentState
    ) -> None:

        previous = component.state

        component._set_state(
            state
        )

        self._history.append(

            Transition(

                component=component.name,

                previous=previous,

                current=state

            )

        )

        #
        # Future:
        #
        # Event Bus
        # Metrics
        # Logger
        # Health Monitor
        #

    #
    # ---------------------------------------------------------
    # Initialize
    # ---------------------------------------------------------
    #

    def initialize(
        self,
        component: Component
    ) -> None:

        if component.state != ComponentState.CREATED:

            return

        self._transition(

            component,

            ComponentState.INITIALIZING

        )

        try:

            component.on_initialize()

            self._transition(

                component,

                ComponentState.INITIALIZED

            )

        except Exception:

            self._transition(

                component,

                ComponentState.ERROR

            )

            raise

    #
    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------
    #

    def start(
        self,
        component: Component
    ) -> None:

        if component.state not in {

            ComponentState.INITIALIZED,

            ComponentState.STOPPED

        }:

            return

        self._transition(

            component,

            ComponentState.STARTING

        )

        try:

            component.on_start()

            component._started = datetime.now()

            self._transition(

                component,

                ComponentState.RUNNING

            )

        except Exception:

            self._transition(

                component,

                ComponentState.ERROR

            )

            raise

    #
    # ---------------------------------------------------------
    # Pause
    # ---------------------------------------------------------
    #

    def pause(
        self,
        component: Component
    ) -> None:

        if component.state != ComponentState.RUNNING:

            return

        component.on_pause()

        self._transition(

            component,

            ComponentState.PAUSED

        )

    #
    # ---------------------------------------------------------
    # Resume
    # ---------------------------------------------------------
    #

    def resume(
        self,
        component: Component
    ) -> None:

        if component.state != ComponentState.PAUSED:

            return

        component.on_resume()

        self._transition(

            component,

            ComponentState.RUNNING

        )

    #
    # ---------------------------------------------------------
    # Stop
    # ---------------------------------------------------------
    #

    def stop(
        self,
        component: Component
    ) -> None:

        if component.state not in {

            ComponentState.RUNNING,

            ComponentState.PAUSED

        }:

            return

        self._transition(

            component,

            ComponentState.STOPPING

        )

        component.on_stop()

        component._stopped = datetime.now()

        self._transition(

            component,

            ComponentState.STOPPED

        )

    #
    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------
    #

    def shutdown(
        self,
        component: Component
    ) -> None:

        component.on_shutdown()

        self._transition(

            component,

            ComponentState.SHUTDOWN

        )

    #
    # ---------------------------------------------------------
    # Recovery
    # ---------------------------------------------------------
    #

    def recover(
        self,
        component: Component
    ) -> None:

        self._transition(

            component,

            ComponentState.RECOVERING

        )

        component.on_initialize()

        component.on_start()

        self._transition(

            component,

            ComponentState.RUNNING

        )

    #
    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------
    #

    def history(
        self
    ) -> list[Transition]:

        return self._history.copy()

    def latest(
        self
    ) -> Transition | None:

        if not self._history:

            return None

        return self._history[-1]

    def clear_history(
        self
    ) -> None:

        self._history.clear()

    #
    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------
    #

    def component_state(
        self,
        name: str
    ) -> ComponentState | None:

        component = self._registry.get(
            name
        )

        if component is None:

            return None

        return component.state

    def healthy(
        self
    ) -> bool:

        return all(

            registration.healthy

            for registration

            in self._registry

        )

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def transition_count(
        self
    ) -> int:

        return len(
            self._history
        )

    def __repr__(
        self
    ) -> str:

        return (

            "Lifecycle("

            f"transitions={self.transition_count}"

            ")"

        )