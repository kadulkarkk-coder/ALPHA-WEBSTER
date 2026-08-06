"""
WEBSTER ALPHA

Capability Request
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from core.planning.step import PlanStep

from core.capability.types import (
    CapabilityPriority,
    CapabilityType,
)


@dataclass(slots=True, frozen=True)
class CapabilityRequest:
    """
    Represents a request to execute
    a capability.
    """

    # =====================================================
    # Required
    # =====================================================

    capability: str

    action: str

    step: PlanStep

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
    # Configuration
    # =====================================================

    capability_type: CapabilityType = (
        CapabilityType.SYSTEM
    )

    priority: CapabilityPriority = (
        CapabilityPriority.NORMAL
    )

    # =====================================================
    # Arguments
    # =====================================================

    arguments: dict[str, object] = field(
        default_factory=dict
    )

    # =====================================================
    # Execution
    # =====================================================

    timeout: float | None = None

    retry_count: int = 0

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

        if not self.capability.strip():

            raise ValueError(
                "Capability name cannot be empty."
            )

        if not self.action.strip():

            raise ValueError(
                "Action cannot be empty."
            )

        if self.retry_count < 0:

            raise ValueError(
                "Retry count cannot be negative."
            )

        if (
            self.timeout is not None
            and self.timeout <= 0
        ):

            raise ValueError(
                "Timeout must be greater than zero."
            )

    # =====================================================
    # Helpers
    # =====================================================

    @property
    def has_timeout(self) -> bool:

        return self.timeout is not None

    @property
    def has_arguments(self) -> bool:

        return bool(self.arguments)

    @property
    def has_metadata(self) -> bool:

        return bool(self.metadata)

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:

        return (
            "CapabilityRequest("
            f"id='{self.identifier}', "
            f"capability='{self.capability}', "
            f"action='{self.action}', "
            f"type={self.capability_type.name}, "
            f"priority={self.priority.name}"
            ")"
        )
