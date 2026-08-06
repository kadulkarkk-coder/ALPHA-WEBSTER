"""
Webster Alpha

Capability Registry
"""

from __future__ import annotations

from typing import Iterable

from core.capability.capability import Capability


class CapabilityRegistry:
    """
    Stores and manages all registered
    capabilities.
    """

    def __init__(self) -> None:

        self._capabilities: dict[
            str,
            Capability
        ] = {}

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        capability: Capability
    ) -> None:
        """
        Register a capability.
        """

        name = capability.name.lower()

        if name in self._capabilities:

            raise ValueError(

                f"Capability '{name}' is already registered."

            )

        self._capabilities[name] = capability

    def unregister(
        self,
        name: str
    ) -> None:
        """
        Remove a capability.
        """

        self._capabilities.pop(
            name.lower(),
            None
        )

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str
    ) -> Capability | None:
        """
        Retrieve a capability.
        """

        return self._capabilities.get(
            name.lower()
        )

    def require(
        self,
        name: str
    ) -> Capability:
        """
        Retrieve a capability or
        raise an exception.
        """

        capability = self.get(name)

        if capability is None:

            raise KeyError(

                f"Capability '{name}' was not found."

            )

        return capability

    def exists(
        self,
        name: str
    ) -> bool:

        return (

            name.lower()

            in

            self._capabilities

        )

    #
    # ---------------------------------------------------------
    # Listing
    # ---------------------------------------------------------
    #

    def all(
        self
    ) -> tuple[
        Capability,
        ...
    ]:

        return tuple(

            self._capabilities.values()

        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def find_by_category(self, category) -> list[Capability]:
        return [c for c in self._capabilities.values() if getattr(c, "category", None) == category]

    def find_by_name(self, name: str) -> list[Capability]:
        key = name.lower()
        return [c for n, c in self._capabilities.items() if key in n]

    def list_capabilities(self) -> list[str]:
        return list(self._capabilities.keys())

    def list_categories(self) -> list[str]:
        cats = set()
        for c in self._capabilities.values():
            cats.add(str(getattr(c, "category", "unknown")))
        return sorted(cats)

    def names(
        self
    ) -> tuple[
        str,
        ...
    ]:

        return tuple(

            sorted(

                self._capabilities.keys()

            )

        )

    #
    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    #

    def clear(
        self
    ) -> None:

        self._capabilities.clear()

    def __len__(
        self
    ) -> int:

        return len(

            self._capabilities

        )

    def __contains__(
        self,
        name: str
    ) -> bool:

        return self.exists(name)

    def __iter__(
        self
    ) -> Iterable[
        Capability
    ]:

        return iter(

            self._capabilities.values()

        )

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self
    ) -> str:

        return (

            "CapabilityRegistry("

            f"count={len(self)}"

            ")"

        )