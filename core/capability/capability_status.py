"""WEBSTER capability status snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.capability.availability import Availability, availability_for
from core.capability.capability import Capability


@dataclass(frozen=True, slots=True)
class CapabilityStatusSnapshot:
    """Serializable runtime view of one registered capability."""

    name: str
    category: str
    capability_type: str
    status: str
    availability: Availability
    enabled: bool
    description: str
    version: str
    permissions: tuple[str, ...]
    last_execution: datetime | None = None
    last_error: str | None = None


def snapshot(
    capability: Capability,
    *,
    last_execution: datetime | None = None,
    last_error: str | None = None,
) -> CapabilityStatusSnapshot:
    """Build a status snapshot without exposing mutable capability internals."""
    availability = Availability(state=availability_for(capability.status))
    return CapabilityStatusSnapshot(
        name=capability.name,
        category=capability.category.name,
        capability_type=capability.capability_type.name,
        status=capability.status.name,
        availability=availability,
        enabled=capability.status.name != "DISABLED",
        description=capability.description,
        version=capability.version,
        permissions=tuple(permission.name for permission in capability.permissions),
        last_execution=last_execution,
        last_error=last_error,
    )
