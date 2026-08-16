"""Lock the current Windows session."""

from __future__ import annotations

import ctypes
import os

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class LockScreenCapability(Capability):
    """Lock the Windows workstation."""

    def __init__(self) -> None:
        super().__init__(
            name="lock_screen",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.SYSTEM_CONTROL,),
        )
        self._description = "Lock the current Windows session."
        self._supported_platforms = ("windows",)
        self._arguments = {}
        self._returns = {"output": "lock status"}

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        del request
        try:
            if os.name != "nt":
                return CapabilityResult.failure_result(
                    "lock_screen currently supports Windows only."
                )
            success = bool(ctypes.windll.user32.LockWorkStation())
            if not success:
                return CapabilityResult.failure_result("Windows could not lock the workstation.")
            return CapabilityResult.success_result(output="Screen locked.")
        except Exception as exc:
            return CapabilityResult.failure_result(str(exc))
