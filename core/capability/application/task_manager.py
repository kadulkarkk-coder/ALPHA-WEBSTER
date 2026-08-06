from __future__ import annotations

import subprocess

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class TaskManagerCapability(Capability):

    def __init__(self):

        super().__init__(
            name="task_manager",
            capability_type=CapabilityType.APPLICATION,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.PROCESS_CONTROL,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        subprocess.Popen(["taskmgr"])

        return CapabilityResult.success_result(
            output="Task Manager opened."
        )