"""WEBSTER ALPHA - capability context prepared for planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.capability.engine import CapabilityEngine


@dataclass(slots=True)
class CapabilityContext:
    """A safe, serializable snapshot of capabilities available to an AI task."""

    requested: str | None = None
    available: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_engine(cls, engine: CapabilityEngine, requested: str | None = None) -> "CapabilityContext":
        names = sorted(engine.names())
        return cls(requested=requested, available=names, metadata={"count": len(names)})

    def supports(self, capability: str | None) -> bool:
        return bool(capability and capability in self.available)

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested": self.requested,
            "available": list(self.available),
            "metadata": dict(self.metadata),
        }
