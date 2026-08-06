"""
Webster Alpha

Capability Group System

Groups related capabilities together.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Iterator

from core.kernel.capability import Capability


@dataclass(slots=True)
class CapabilityGroup:
    """
    Collection of related capabilities.
    """

    name: str

    description: str = ""

    capabilities: dict[
        str,
        Capability
    ] = field(
        default_factory=dict
    )

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        capability: Capability
    ) -> None:

        self.capabilities[
            capability.name
        ] = capability

        capability.register()

    def unregister(
        self,
        name: str
    ) -> Capability | None:

        capability = self.capabilities.pop(
            name,
            None
        )

        if capability is not None:

            capability.unregister()

        return capability

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str
    ) -> Capability | None:

        return self.capabilities.get(
            name
        )

    def exists(
        self,
        name: str
    ) -> bool:

        return name in self.capabilities

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
            self.capabilities
        )

    def names(
        self
    ) -> list[str]:

        return sorted(
            self.capabilities.keys()
        )

    def values(
        self
    ) -> list[Capability]:

        return list(
            self.capabilities.values()
        )

    #
    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------
    #

    def enable_all(
        self
    ) -> None:

        for capability in self.capabilities.values():

            capability.enable()

    def disable_all(
        self
    ) -> None:

        for capability in self.capabilities.values():

            capability.disable()

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def clear(
        self
    ) -> None:

        for capability in self.capabilities.values():

            capability.unregister()

        self.capabilities.clear()

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
        Capability
    ]:

        return iter(
            self.capabilities.values()
        )

    def __repr__(
        self
    ) -> str:

        return (

            f"CapabilityGroup("

            f"name='{self.name}', "

            f"count={self.count}"

            f")"

        )