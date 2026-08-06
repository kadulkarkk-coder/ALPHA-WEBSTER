"""
Webster Alpha

Capability Registry

Central registry responsible for managing all
capabilities inside Webster.
"""

from __future__ import annotations

from typing import Any
from typing import Iterator

from core.kernel.capability import Capability
from core.kernel.capability_group import CapabilityGroup
from core.kernel.capability_result import CapabilityResult


class CapabilityRegistry:
    """
    Central capability registry.
    """

    def __init__(
        self
    ) -> None:

        self._groups: dict[
            str,
            CapabilityGroup
        ] = {}

        self._aliases: dict[
            str,
            str
        ] = {}

    #
    # ---------------------------------------------------------
    # Groups
    # ---------------------------------------------------------
    #

    def create_group(
        self,
        name: str,
        description: str = ""
    ) -> CapabilityGroup:

        if name in self._groups:

            raise ValueError(

                f"Group '{name}' already exists."

            )

        group = CapabilityGroup(

            name=name,

            description=description

        )

        self._groups[
            name
        ] = group

        return group

    def remove_group(
        self,
        name: str
    ) -> None:

        self._groups.pop(
            name,
            None
        )

    def group(
        self,
        name: str
    ) -> CapabilityGroup:

        return self._groups[
            name
        ]

    def has_group(
        self,
        name: str
    ) -> bool:

        return name in self._groups

    #
    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------
    #

    def register(
        self,
        capability: Capability
    ) -> None:

        group_name = capability.category

        if group_name not in self._groups:

            self.create_group(
                group_name
            )

        self._groups[
            group_name
        ].register(
            capability
        )

    def unregister(
        self,
        name: str
    ) -> Capability | None:

        for group in self._groups.values():

            capability = group.unregister(
                name
            )

            if capability is not None:

                return capability

        return None

    #
    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------
    #

    def get(
        self,
        name: str
    ) -> Capability | None:

        real_name = self._aliases.get(
            name,
            name
        )

        for group in self._groups.values():

            capability = group.get(
                real_name
            )

            if capability is not None:

                return capability

        return None

    def exists(
        self,
        name: str
    ) -> bool:

        return self.get(
            name
        ) is not None

    #
    # ---------------------------------------------------------
    # Aliases
    # ---------------------------------------------------------
    #

    def add_alias(
        self,
        alias: str,
        capability: str
    ) -> None:

        self._aliases[
            alias
        ] = capability

    def remove_alias(
        self,
        alias: str
    ) -> None:

        self._aliases.pop(
            alias,
            None
        )

    #
    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    #

    def execute(
        self,
        name: str,
        *args: Any,
        **kwargs: Any
    ) -> CapabilityResult:

        capability = self.get(
            name
        )

        if capability is None:

            return CapabilityResult.not_found(
                name
            )

        try:

            result = capability.execute(
                *args,
                **kwargs
            )

            if isinstance(
                result,
                CapabilityResult
            ):

                return result

            return CapabilityResult.ok(

                capability=name,

                data=result

            )

        except Exception as exc:

            return CapabilityResult.fail(

                capability=name,

                message="Capability execution failed.",

                error=str(
                    exc
                )

            )

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def groups(
        self
    ) -> list[str]:

        return sorted(
            self._groups.keys()
        )

    @property
    def group_count(
        self
    ) -> int:

        return len(
            self._groups
        )

    @property
    def capability_count(
        self
    ) -> int:

        total = 0

        for group in self._groups.values():

            total += group.count

        return total

    def all(
        self
    ) -> list[Capability]:

        capabilities: list[
            Capability
        ] = []

        for group in self._groups.values():

            capabilities.extend(
                group.values()
            )

        return capabilities

    def clear(
        self
    ) -> None:

        for group in self._groups.values():

            group.clear()

        self._groups.clear()

        self._aliases.clear()

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

        return self.capability_count

    def __iter__(
        self
    ) -> Iterator[
        Capability
    ]:

        return iter(
            self.all()
        )

    def __repr__(
        self
    ) -> str:

        return (

            f"CapabilityRegistry("

            f"groups={self.group_count}, "

            f"capabilities={self.capability_count}"

            f")"

        )