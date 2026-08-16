"""Webster Alpha system capabilities."""

from core.capability.system.close_application import CloseApplicationCapability
from core.capability.system.lock_screen import LockScreenCapability
from core.capability.system.open_application import OpenApplicationCapability
from core.capability.system.system_information import SystemInformationCapability

__all__ = [
    "CloseApplicationCapability",
    "LockScreenCapability",
    "OpenApplicationCapability",
    "SystemInformationCapability",
]
