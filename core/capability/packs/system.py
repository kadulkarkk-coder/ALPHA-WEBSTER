"""
Webster Alpha

System Capability Pack
Sprint 30.6
"""

from __future__ import annotations

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry

from core.capability.system.close_application import CloseApplicationCapability
from core.capability.system.lock_screen import LockScreenCapability
from core.capability.system.open_application import OpenApplicationCapability
from core.capability.system.system_information import SystemInformationCapability


class SystemPack(CapabilityPack):
    """Registers safe core Windows/system capabilities."""

    @property
    def name(self) -> str:
        return "system"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(self, registry: CapabilityRegistry) -> None:
        registry.register(OpenApplicationCapability())
        registry.register(CloseApplicationCapability())
        registry.register(LockScreenCapability())
        registry.register(SystemInformationCapability())
