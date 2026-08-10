"""
Webster Alpha

Capability Pack
Sprint 30.1
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.capability.registry import CapabilityRegistry


class CapabilityPack(ABC):
    """Base class for a cohesive group of Webster capabilities."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable, human-readable pack name."""
        raise NotImplementedError

    @property
    def version(self) -> str:
        """Return the pack version."""
        return "1.0.0"

    @property
    def enabled(self) -> bool:
        """Return whether this pack should be loaded."""
        return True

    @abstractmethod
    def register(self, registry: CapabilityRegistry) -> None:
        """Register all capabilities owned by this pack."""
        raise NotImplementedError

    def unregister(self, registry: CapabilityRegistry) -> None:
        """Optional cleanup hook for unloading the pack."""
        return None

    def metadata(self) -> dict[str, object]:
        """Return serializable metadata useful to the pack manager."""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
        }

    def __repr__(self) -> str:
        return (
            f"CapabilityPack(name='{self.name}', "
            f"version='{self.version}', enabled={self.enabled})"
        )
