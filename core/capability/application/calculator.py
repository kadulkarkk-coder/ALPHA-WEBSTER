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


class CalculatorCapability(Capability):

    def __init__(self):

        super().__init__(
            name="calculator",
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

        subprocess.Popen(["calc"])

        return CapabilityResult.success_result(
            output="Calculator opened."
        )