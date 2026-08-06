"""
Webster Alpha

Capability Result System

Defines the standardized result object returned by every
capability executed inside Webster.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from typing import Any


class CapabilityStatus(
    Enum
):
    """
    Execution status.
    """

    SUCCESS = "success"

    FAILED = "failed"

    CANCELLED = "cancelled"

    BLOCKED = "blocked"

    PERMISSION_DENIED = "permission_denied"

    NOT_FOUND = "not_found"

    INVALID_ARGUMENT = "invalid_argument"

    TIMEOUT = "timeout"


@dataclass(slots=True)
class CapabilityResult:
    """
    Result returned by every capability.
    """

    capability: str

    status: CapabilityStatus

    data: Any = None

    message: str = ""

    error: str | None = None

    execution_time: float = 0.0

    timestamp: datetime = field(
        default_factory=datetime.now
    )

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    @property
    def success(
        self
    ) -> bool:

        return (

            self.status

            ==

            CapabilityStatus.SUCCESS

        )

    @property
    def failed(
        self
    ) -> bool:

        return not self.success

    def add_metadata(
        self,
        key: str,
        value: Any
    ) -> None:

        self.metadata[
            key
        ] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None
    ) -> Any:

        return self.metadata.get(
            key,
            default
        )

    def to_dict(
        self
    ) -> dict[str, Any]:

        return {

            "capability": self.capability,

            "status": self.status.value,

            "success": self.success,

            "message": self.message,

            "error": self.error,

            "execution_time": self.execution_time,

            "timestamp": self.timestamp,

            "metadata": self.metadata,

            "data": self.data

        }

    @classmethod
    def ok(
        cls,
        capability: str,
        data: Any = None,
        message: str = ""
    ) -> "CapabilityResult":

        return cls(

            capability=capability,

            status=CapabilityStatus.SUCCESS,

            data=data,

            message=message

        )

    @classmethod
    def fail(
        cls,
        capability: str,
        message: str,
        error: str | None = None
    ) -> "CapabilityResult":

        return cls(

            capability=capability,

            status=CapabilityStatus.FAILED,

            message=message,

            error=error

        )

    @classmethod
    def blocked(
        cls,
        capability: str,
        reason: str
    ) -> "CapabilityResult":

        return cls(

            capability=capability,

            status=CapabilityStatus.BLOCKED,

            message=reason

        )

    @classmethod
    def permission_denied(
        cls,
        capability: str
    ) -> "CapabilityResult":

        return cls(

            capability=capability,

            status=CapabilityStatus.PERMISSION_DENIED,

            message="Permission denied."

        )

    @classmethod
    def timeout(
        cls,
        capability: str
    ) -> "CapabilityResult":

        return cls(

            capability=capability,

            status=CapabilityStatus.TIMEOUT,

            message="Execution timed out."

        )

    def __bool__(
        self
    ) -> bool:

        return self.success

    def __repr__(
        self
    ) -> str:

        return (

            f"CapabilityResult("

            f"capability='{self.capability}', "

            f"status='{self.status.value}')"

        )