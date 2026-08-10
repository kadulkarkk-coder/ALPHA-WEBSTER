"""
Webster Alpha

Capability Pack Diagnostics
Sprint 30.10
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.capability.packs.manager import CapabilityPackManager


@dataclass(frozen=True, slots=True)
class CapabilityPackDiagnostic:
    """Detailed, read-only diagnostic snapshot for one capability pack."""

    name: str
    version: str
    enabled: bool
    registered: bool
    loaded: bool
    healthy: bool
    error: str | None
    dependencies: tuple[str, ...]
    priority: int | None
    module: str | None
    class_name: str | None
    checked_at: str

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "registered": self.registered,
            "loaded": self.loaded,
            "healthy": self.healthy,
            "error": self.error,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "module": self.module,
            "class_name": self.class_name,
            "checked_at": self.checked_at,
        }


class CapabilityPackDiagnostics:
    """Collect diagnostics without changing pack or registry state."""

    def __init__(self, manager: CapabilityPackManager) -> None:
        self.manager = manager

    def inspect(self, name: str) -> CapabilityPackDiagnostic:
        checked_at = datetime.now(timezone.utc).isoformat()
        pack = self.manager.get(name)

        if pack is None:
            return CapabilityPackDiagnostic(
                name=str(name),
                version="unknown",
                enabled=False,
                registered=False,
                loaded=False,
                healthy=False,
                error="Capability pack is not registered.",
                dependencies=(),
                priority=None,
                module=None,
                class_name=None,
                checked_at=checked_at,
            )

        manifest = self.manager.manifests.get(pack.name)
        error: str | None = None
        try:
            result = self.manager.validate()
            if not result.valid:
                related = [
                    message for message in result.errors
                    if pack.name.lower() in message.lower()
                ]
                error = "; ".join(related) if related else "; ".join(result.errors)
        except Exception as exc:
            error = str(exc)

        enabled = bool(pack.enabled and (manifest is None or manifest.enabled))
        loaded = self.manager.is_loaded(pack.name)
        healthy = error is None and (not enabled or loaded)

        return CapabilityPackDiagnostic(
            name=pack.name,
            version=pack.version,
            enabled=enabled,
            registered=True,
            loaded=loaded,
            healthy=healthy,
            error=error,
            dependencies=manifest.dependencies if manifest else (),
            priority=manifest.priority if manifest else None,
            module=manifest.module if manifest else pack.__class__.__module__,
            class_name=manifest.class_name if manifest else pack.__class__.__qualname__,
            checked_at=checked_at,
        )

    def inspect_all(self) -> tuple[CapabilityPackDiagnostic, ...]:
        return tuple(self.inspect(pack.name) for pack in self.manager.packs)

    def report(self) -> dict[str, object]:
        diagnostics = self.inspect_all()
        return {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "total": len(diagnostics),
            "healthy": sum(item.healthy for item in diagnostics),
            "unhealthy": sum(not item.healthy for item in diagnostics),
            "loaded": sum(item.loaded for item in diagnostics),
            "enabled": sum(item.enabled for item in diagnostics),
            "errors": sum(item.error is not None for item in diagnostics),
            "packs": tuple(item.as_dict() for item in diagnostics),
        }

    def format_report(self) -> str:
        """Return a compact human-readable diagnostic report."""
        report = self.report()
        lines = [
            "Capability Pack Diagnostics",
            "----------------------------",
            f"Total: {report['total']}",
            f"Healthy: {report['healthy']}",
            f"Unhealthy: {report['unhealthy']}",
            f"Loaded: {report['loaded']}",
            f"Enabled: {report['enabled']}",
            f"Errors: {report['errors']}",
        ]

        for item in report["packs"]:
            status = "OK" if item["healthy"] else "ERROR"
            lines.append(
                f"- {item['name']} [{status}] "
                f"loaded={item['loaded']} enabled={item['enabled']}"
            )
            if item["error"]:
                lines.append(f"  error: {item['error']}")

        return "\n".join(lines)
