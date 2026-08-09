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
    """Base class for every Webster capability."""

    def __init__(
        self,
        name: str,
        capability_type: CapabilityType,
        category: CapabilityCategory,
        permissions: tuple[CapabilityPermission, ...] = (
            CapabilityPermission.NONE,
        ),
    ) -> None:
        self._name = name
        self._type = capability_type
        self._category = category
        self._permissions = permissions
        self._status = CapabilityStatus.AVAILABLE

        self._description: str = ""
        self._version: str = "1.0.0"
        self._author: str = ""
        self._supported_platforms: tuple[str, ...] = ()
        self._arguments: dict[str, str] = {}
        self._returns: dict[str, str] = {}
        self._metadata: dict[str, object] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def capability_type(self) -> CapabilityType:
        return self._type

    @property
    def category(self) -> CapabilityCategory:
        return self._category

    @property
    def permissions(self) -> tuple[CapabilityPermission, ...]:
        return self._permissions

    @property
    def status(self) -> CapabilityStatus:
        return self._status

    def enable(self) -> None:
        self._status = CapabilityStatus.AVAILABLE

    def disable(self) -> None:
        self._status = CapabilityStatus.DISABLED

    def busy(self) -> None:
        self._status = CapabilityStatus.BUSY

    def available(self) -> None:
        self._status = CapabilityStatus.AVAILABLE

    def can_execute(self, request: CapabilityRequest) -> bool:
        return self.status == CapabilityStatus.AVAILABLE

    # ---------------------------------------------------------
    # Request argument helpers
    # ---------------------------------------------------------

    @staticmethod
    def _argument(request: CapabilityRequest, name: str) -> object:
        """Return a request argument with a clear missing-argument error."""
        if request is None:
            raise ValueError("Capability request cannot be None.")

        arguments = getattr(request, "arguments", None)
        if not isinstance(arguments, dict):
            raise ValueError("Capability request arguments must be a dictionary.")

        if name not in arguments:
            raise ValueError(f"Missing required argument '{name}'.")

        return arguments[name]

    @classmethod
    def get_string(cls, request: CapabilityRequest, name: str, default: str | None = None) -> str:
        """Read a string argument from a CapabilityRequest."""
        arguments = getattr(request, "arguments", None)
        if isinstance(arguments, dict) and name not in arguments and default is not None:
            return default

        value = cls._argument(request, name)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Argument '{name}' cannot be None.")

        text = str(value).strip()
        if not text and default is not None:
            return default
        return text

    @classmethod
    def get_bool(cls, request: CapabilityRequest, name: str, default: bool | None = None) -> bool:
        """Read a boolean argument from a CapabilityRequest."""
        arguments = getattr(request, "arguments", None)
        if isinstance(arguments, dict) and name not in arguments and default is not None:
            return default

        value = cls._argument(request, name)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y", "on"}:
                return True
            if normalized in {"false", "0", "no", "n", "off"}:
                return False
        raise ValueError(f"Argument '{name}' must be a boolean.")

    @classmethod
    def get_int(cls, request: CapabilityRequest, name: str, default: int | None = None) -> int:
        """Read an integer argument from a CapabilityRequest."""
        arguments = getattr(request, "arguments", None)
        if isinstance(arguments, dict) and name not in arguments and default is not None:
            return default

        value = cls._argument(request, name)
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Argument '{name}' must be an integer.") from exc

    @abstractmethod
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            "Capability("
            f"name='{self.name}', "
            f"type={self.capability_type.name}, "
            f"status={self.status.name}"
            ")"
        )

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
