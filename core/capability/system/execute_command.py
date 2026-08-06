"""
Webster Alpha

Execute Command Capability
"""

from __future__ import annotations

import subprocess

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class ExecuteCommandCapability(SystemCapability):
    """
    Executes a shell command.
    """

    DEFAULT_TIMEOUT = 30

    def __init__(self) -> None:

        super().__init__(
            name="execute_command",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.SYSTEM,
                CapabilityPermission.EXECUTE,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        try:

            command = self.get_command(request)

            timeout = request.arguments.get(
                "timeout",
                self.DEFAULT_TIMEOUT,
            )

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return CapabilityResult.success_result(
                output=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
            )

        except subprocess.TimeoutExpired:

            return CapabilityResult.failure_result(
                error="Command execution timed out.",
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )