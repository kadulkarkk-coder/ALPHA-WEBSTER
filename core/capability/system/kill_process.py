"""
Webster Alpha

List Processes Capability
"""

from __future__ import annotations

import psutil

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class ListProcessesCapability(SystemCapability):
    """
    Lists all running system processes.
    """

    def __init__(self) -> None:

        super().__init__(
            name="list_processes",
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

            processes = []

            for process in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "status",
                    "memory_info",
                    "exe",
                ]
            ):

                try:

                    memory = process.info["memory_info"]

                    processes.append(
                        {
                            "pid": process.info["pid"],
                            "name": process.info["name"],
                            "status": process.info["status"],
                            "memory": (
                                memory.rss
                                if memory
                                else 0
                            ),
                            "path": process.info["exe"],
                        }
                    )

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            processes.sort(
                key=lambda p: (
                    p["name"] or ""
                ).lower()
            )

            return CapabilityResult.success_result(
                output=processes,
                count=len(processes),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )