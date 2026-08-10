"""
Webster Alpha

Capability Pack Health Reporting
Sprint 30.9
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.capability.packs.manager import CapabilityPackManager


@dataclass(frozen=True, slots=True)
class CapabilityPackHealth:
    """Snapshot describing the current health of one capability pack."""

    name: str
    version: str
    enabled: bool
    registered: bool
    loaded: bool
    healthy: bool
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "registered": self.registered,
            "loaded": self.loaded,
            "healthy": self.healthy,
            "error": self.error,
        }


class CapabilityPackHealthReporter:
    """Produce health snapshots without changing pack lifecycle state."""

    def __init__(self, manager: CapabilityPackManager) -> None:
        self.manager = manager

    def check(self, name: str) -> CapabilityPackHealth:
        pack = self.manager.get(name)
        if pack is None:
            return CapabilityPackHealth(
                name=str(name),
                version="unknown",
                enabled=False,
                registered=False,
                loaded=False,
                healthy=False,
                error="Capability pack is not registered.",
            )

        manifest = self.manager.manifests.get(pack.name)
        enabled = bool(pack.enabled and (manifest is None or manifest.enabled))
        loaded = self.manager.is_loaded(pack.name)
        error: str | None = None

        try:
            result = self.manager.validate()
            if not result.valid:
                matching = [
                    message
                    for message in result.errors
                    if pack.name.lower() in message.lower()
                ]
                error = "; ".join(matching) if matching else "; ".join(result.errors)
        except Exception as exc:
            error = str(exc)

        healthy = error is None and (not enabled or loaded)

        return CapabilityPackHealth(
            name=pack.name,
            version=pack.version,
            enabled=enabled,
            registered=True,
            loaded=loaded,
            healthy=healthy,
            error=error,
        )

    def check_all(self) -> tuple[CapabilityPackHealth, ...]:
        return tuple(self.check(pack.name) for pack in self.manager.packs)

    def summary(self) -> dict[str, object]:
        health = self.check_all()
        return {
            "total": len(health),
            "healthy": sum(item.healthy for item in health),
            "loaded": sum(item.loaded for item in health),
            "enabled": sum(item.enabled for item in health),
            "errors": sum(item.error is not None for item in health),
        }
