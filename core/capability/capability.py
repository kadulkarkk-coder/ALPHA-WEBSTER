"""
Webster Alpha

Capability Base Class
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityStatus,
    CapabilityType,
)


class Capability(ABC):
    """
    Base class for every Webster capability.
    """

    def __init__(
        self,
        name: str,
        capability_type: CapabilityType,
        category: CapabilityCategory,
        permissions: tuple[
            CapabilityPermission,
            ...
        ] = (
            CapabilityPermission.NONE,
        ),
    ) -> None:

        self._name = name

        self._type = capability_type

        self._category = category

        self._permissions = permissions

        self._status = CapabilityStatus.AVAILABLE

        # Optional metadata
        self._description: str = ""
        self._version: str = "1.0.0"
        self._author: str = ""
        self._supported_platforms: tuple[str, ...] = ()
        self._arguments: dict[str, str] = {}
        self._returns: dict[str, str] = {}
        self._metadata: dict[str, object] = {}

    #
    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    #

    @property
    def name(self) -> str:

        return self._name

    @property
    def capability_type(
        self,
    ) -> CapabilityType:

        return self._type

    @property
    def category(
        self,
    ) -> CapabilityCategory:

        return self._category

    @property
    def permissions(
        self,
    ) -> tuple[
        CapabilityPermission,
        ...
    ]:

        return self._permissions

    @property
    def status(
        self,
    ) -> CapabilityStatus:

        return self._status

    #
    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------
    #

    def enable(self) -> None:

        self._status = (
            CapabilityStatus.AVAILABLE
        )

    def disable(self) -> None:

        self._status = (
            CapabilityStatus.DISABLED
        )

    def busy(self) -> None:

        self._status = (
            CapabilityStatus.BUSY
        )

    def available(self) -> None:

        self._status = (
            CapabilityStatus.AVAILABLE
        )

    #
    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    #

    def can_execute(
        self,
        request: CapabilityRequest,
    ) -> bool:
        """
        Determines whether this
        capability can execute
        the supplied request.
        """

        return (
            self.status
            == CapabilityStatus.AVAILABLE
        )

    #
    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    #

    @abstractmethod
    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """
        Execute the capability.
        """

        raise NotImplementedError

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self,
    ) -> str:

        return (

            "Capability("

            f"name='{self.name}', "

            f"type={self.capability_type.name}, "

            f"status={self.status.name}"

            ")"

        )

    # ---------------------------------------------------------
    # Metadata properties
    # ---------------------------------------------------------

    @property
    def description(self) -> str:
        return self._description

    @property
    def version(self) -> str:
        return self._version

    @property
    def author(self) -> str:
        return self._author

    @property
    def supported_platforms(self) -> tuple[str, ...]:
        return self._supported_platforms

    @property
    def arguments(self) -> dict[str, str]:
        return dict(self._arguments)

    @property
    def returns(self) -> dict[str, str]:
        return dict(self._returns)

    @property
    def metadata(self) -> dict[str, object]:
        return dict(self._metadata)