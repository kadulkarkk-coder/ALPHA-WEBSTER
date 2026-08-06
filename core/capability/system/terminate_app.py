"""
Webster Alpha

Terminate Application Capability
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


class TerminateApplicationCapability(SystemCapability):
    """
    Gracefully terminates an application by
    process name.
    """

    def __init__(self) -> None:

        super().__init__(
            name="terminate_application",
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

            process_name = self.get_process_name(request)

            terminated = []

            for process in psutil.process_iter(
                ["pid", "name"]
            ):

                try:

                    name = process.info["name"]

                    if (
                        name
                        and name.lower()
                        == process_name.lower()
                    ):

                        process.terminate()

                        terminated.append(
                            {
                                "pid": process.pid,
                                "name": name,
                            }
                        )

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                ):
                    continue

            if not terminated:

                return CapabilityResult.failure_result(
                    error=(
                        f"No running process named "
                        f"'{process_name}' found."
                    ),
                )

            return CapabilityResult.success_result(
                output=terminated,
                terminated=len(terminated),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )