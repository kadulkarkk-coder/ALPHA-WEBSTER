"""
WEBSTER ALPHA

Capability Result
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from core.capability.types import CapabilityResultStatus


@dataclass(slots=True, frozen=True)
class CapabilityResult:
    """
    Represents the result returned after executing
    a capability.
    """

    # =====================================================
    # Required
    # =====================================================

    status: CapabilityResultStatus

    success: bool

    # =====================================================
    # Identity
    # =====================================================

    identifier: str = field(
        default_factory=lambda: str(uuid4())
    )

    created: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # Output
    # =====================================================

    output: object | None = None

    error: str | None = None

    # =====================================================
    # Execution
    # =====================================================

    duration: float = 0.0

    # =====================================================
    # Metadata
    # =====================================================

    metadata: dict[str, object] = field(
        default_factory=dict
    )

    # =====================================================
    # Validation
    # =====================================================

    def __post_init__(self) -> None:

        if self.duration < 0:
            raise ValueError(
                "Duration cannot be negative."
            )

        if self.success and self.error:
            raise ValueError(
                "Successful results cannot contain an error."
            )

        if (
            not self.success
            and self.status == CapabilityResultStatus.SUCCESS
        ):
            raise ValueError(
                "Status and success flag are inconsistent."
            )

    # =====================================================
    # Helpers
    # =====================================================

    @property
    def failed(self) -> bool:

        return not self.success

    @property
    def has_output(self) -> bool:

        return self.output is not None

    @property
    def has_error(self) -> bool:

        return self.error is not None

    @property
    def has_metadata(self) -> bool:

        return bool(self.metadata)

    # =====================================================
    # Factory Methods
    # =====================================================

    @classmethod
    def success_result(
        cls,
        output: object | None = None,
        duration: float = 0.0,
        **metadata,
    ) -> "CapabilityResult":

        return cls(
            status=CapabilityResultStatus.SUCCESS,
            success=True,
            output=output,
            duration=duration,
            metadata=metadata,
        )

    @classmethod
    def failure_result(
        cls,
        error: str,
        duration: float = 0.0,
        **metadata,
    ) -> "CapabilityResult":

        return cls(
            status=CapabilityResultStatus.FAILURE,
            success=False,
            error=error,
            duration=duration,
            metadata=metadata,
        )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:

        return (
            "CapabilityResult("
            f"status={self.status.name}, "
            f"success={self.success}, "
            f"duration={self.duration:.3f}s"
            ")"
        )