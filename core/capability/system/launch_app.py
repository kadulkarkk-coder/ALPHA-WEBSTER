"""
Webster Alpha

Launch Application Capability
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class LaunchApplicationCapability(SystemCapability):
    """
    Launches an application or opens
    a file using the operating system.
    """

    def __init__(self) -> None:

        super().__init__(
            name="launch_application",
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

            target = self.get_existing_path(request)

            if self.is_windows:

                subprocess.Popen(
                    [str(target)],
                    shell=True,
                )

            else:

                subprocess.Popen(
                    [str(target)],
                )

            return CapabilityResult.success_result(
                output=str(target),
                path=str(target),
                launched=True,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )