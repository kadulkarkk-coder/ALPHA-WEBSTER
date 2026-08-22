"""WEBSTER capability availability states and snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from core.capability.types import CapabilityStatus


class AvailabilityState(Enum):
    """Operational availability of a capability."""

    AVAILABLE = auto()
    BUSY = auto()
    DISABLED = auto()
    UNAVAILABLE = auto()
    DEGRADED = auto()
    ERROR = auto()
    REQUIRES_PERMISSION = auto()
    REQUIRES_DEPENDENCY = auto()


def availability_for(status: CapabilityStatus) -> AvailabilityState:
    """Map the existing capability status to governance availability."""
    mapping = {
        CapabilityStatus.AVAILABLE: AvailabilityState.AVAILABLE,
        CapabilityStatus.BUSY: AvailabilityState.BUSY,
        CapabilityStatus.DISABLED: AvailabilityState.DISABLED,
        CapabilityStatus.UNAVAILABLE: AvailabilityState.UNAVAILABLE,
        CapabilityStatus.ERROR: AvailabilityState.ERROR,
    }
    return mapping[status]


@dataclass(frozen=True, slots=True)
class Availability:
    """Immutable availability snapshot used by governance and diagnostics."""

    state: AvailabilityState
    reason: str = ""
    dependency: str | None = None

    @property
    def usable(self) -> bool:
        return self.state in {
            AvailabilityState.AVAILABLE,
            AvailabilityState.DEGRADED,
        }
