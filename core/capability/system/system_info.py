"""
Webster Alpha

System Information Capability
"""

from __future__ import annotations

import platform
from datetime import datetime

import psutil

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class SystemInfoCapability(SystemCapability):
    """
    Returns information about the current system.
    """

    def __init__(self) -> None:

        super().__init__(
            name="system_info",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.SYSTEM,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        try:

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            cpu_percent = psutil.cpu_percent(interval=0.5)

            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "platform": platform.platform(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),

                "cpu": {
                    "physical_cores": psutil.cpu_count(
                        logical=False,
                    ),
                    "logical_cores": psutil.cpu_count(),
                    "usage_percent": cpu_percent,
                },

                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent,
                },

                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },

                "boot_time": datetime.fromtimestamp(
                    psutil.boot_time()
                ).isoformat(),
            }

            return CapabilityResult.success_result(
                output=info,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )