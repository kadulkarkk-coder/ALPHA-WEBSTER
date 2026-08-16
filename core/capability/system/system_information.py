"""System information capability."""

from __future__ import annotations

import os
import platform
import socket
import sys

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class SystemInformationCapability(Capability):
    """Return basic runtime and operating-system information."""

    def __init__(self) -> None:
        super().__init__(
            name="system_information",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.NONE,),
        )
        self._description = "Get basic Webster host and runtime information."
        self._supported_platforms = ("windows", "linux", "darwin")
        self._arguments = {}
        self._returns = {"output": "system information dictionary"}

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        del request
        try:
            info = {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "python_version": platform.python_version(),
                "python_executable": sys.executable,
                "os_name": os.name,
            }
            return CapabilityResult.success_result(output=info)
        except Exception as exc:
            return CapabilityResult.failure_result(str(exc))
