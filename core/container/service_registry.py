"""
Webster Alpha

Service Registry

The central registry for every service
running inside Webster.

Owned by the Kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any


@dataclass(slots=True)
class ServiceRegistration:
    """
    Metadata for a registered service.
    """

    name: str

    instance: Any

    version: str = "1.0.0"

    description: str = ""

    created: datetime = field(
        default_factory=datetime.now
    )

    enabled: bool = True

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


class ServiceRegistry:
    """
    Webster Service Registry.

    Stores every service available
    to the Kernel.
    """

    def __init__(
        self
    ) -> None:

        self._services: dict[
            str,
            ServiceRegistration
        ] = {}

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        name: str,
        instance: Any,
        *,
        version: str = "1.0.0",
        description: str = ""
    ) -> None:

        if name in self._services:

            raise ValueError(

                f"Service '{name}' already exists."

            )

        self._services[
            name
        ] = ServiceRegistration(

            name=name,

            instance=instance,

            version=version,

            description=description

        )

    def unregister(
        self,
        name: str
    ) -> Any | None:

        registration = self._services.pop(
            name,
            None
        )

        if registration is None:

            return None

        return registration.instance

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str
    ) -> Any | None:

        registration = self._services.get(
            name
        )

        if registration is None:

            return None

        return registration.instance

    def registration(
        self,
        name: str
    ) -> ServiceRegistration | None:

        return self._services.get(
            name
        )

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self._services

    #
    # ---------------------------------------------------------
    # State
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
    # Metadata
    # ---------------------------------------------------------
    #

    def set_metadata(
        self,
        service: str,
        key: str,
        value: Any
    ) -> None:

        registration = self.registration(
            service
        )

        if registration is None:

            raise KeyError(

                service

            )

        registration.metadata[
            key
        ] = value

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
            self._services
        )

    def names(
        self
    ) -> list[str]:

        return sorted(
            self._services.keys()
        )

    def registrations(
        self
    ) -> list[
        ServiceRegistration
    ]:

        return list(
            self._services.values()
        )

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def clear(
        self
    ) -> None:

        self._services.clear()

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

    def __repr__(
        self
    ) -> str:

        return (

            "ServiceRegistry("

            f"services={self.count}"

            ")"

        )