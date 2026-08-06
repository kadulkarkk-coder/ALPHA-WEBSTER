"""
Webster Alpha

Component Registry

Central storage for every component
registered inside the Webster Kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Iterator

from core.kernel.component import Component
from core.kernel.component_state import ComponentState
from core.kernel.dependency import ComponentInfo


@dataclass(slots=True)
class ComponentRegistration:
    """
    Complete registration of a component.
    """

    component: Component

    info: ComponentInfo

    registered: datetime = field(
        default_factory=datetime.now
    )

    enabled: bool = True

    restart_count: int = 0

    metadata: dict = field(
        default_factory=dict
    )

    @property
    def name(
        self
    ) -> str:

        return self.component.name

    @property
    def state(
        self
    ) -> ComponentState:

        return self.component.state

    @property
    def healthy(
        self
    ) -> bool:

        return self.component.healthy()


class ComponentRegistry:
    """
    Webster Component Registry.
    """

    def __init__(
        self
    ) -> None:

        self._registry: dict[
            str,
            ComponentRegistration
        ] = {}

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        component: Component,
        info: ComponentInfo
    ) -> None:

        if component.name in self._registry:

            raise ValueError(

                f"Component '{component.name}' already exists."

            )

        self._registry[
            component.name
        ] = ComponentRegistration(

            component=component,

            info=info

        )

    def unregister(
        self,
        name: str
    ) -> ComponentRegistration | None:

        return self._registry.pop(

            name,

            None

        )

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def registration(
        self,
        name: str
    ) -> ComponentRegistration | None:

        return self._registry.get(
            name
        )

    def get(
        self,
        name: str
    ) -> Component | None:

        registration = self.registration(
            name
        )

        if registration is None:

            return None

        return registration.component

    def info(
        self,
        name: str
    ) -> ComponentInfo | None:

        registration = self.registration(
            name
        )

        if registration is None:

            return None

        return registration.info

    #
    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------
    #

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._registry

    def registrations(
        self
    ) -> list[
        ComponentRegistration
    ]:

        return list(
            self._registry.values()
        )

    def components(
        self
    ) -> list[
        Component
    ]:

        return [

            registration.component

            for registration

            in self._registry.values()

        ]

    def enabled(
        self
    ) -> list[
        ComponentRegistration
    ]:

        return [

            registration

            for registration

            in self._registry.values()

            if registration.enabled

        ]

    def healthy(
        self
    ) -> list[
        ComponentRegistration
    ]:

        return [

            registration

            for registration

            in self._registry.values()

            if registration.healthy

        ]

    #
    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------
    #

    def enable(
        self,
        name: str
    ) -> None:

        registration = self.registration(
            name
        )

        if registration:

            registration.enabled = True

    def disable(
        self,
        name: str
    ) -> None:

        registration = self.registration(
            name
        )

        if registration:

            registration.enabled = False

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def count(
        self
    ) -> int:

        return len(
            self._registry
        )

    def names(
        self
    ) -> list[str]:

        return sorted(
            self._registry.keys()
        )

    def clear(
        self
    ) -> None:

        self._registry.clear()

    #
    # ---------------------------------------------------------
    # Magic Methods
    # ---------------------------------------------------------
    #

    def __contains__(
        self,
        name: str
    ) -> bool:

        return self.exists(
            name
        )

    def __len__(
        self
    ) -> int:

        return self.count

    def __iter__(
        self
    ) -> Iterator[
        ComponentRegistration
    ]:

        return iter(
            self._registry.values()
        )

    def __repr__(
        self
    ) -> str:

        return (

            "ComponentRegistry("

            f"components={self.count}"

            ")"

        )