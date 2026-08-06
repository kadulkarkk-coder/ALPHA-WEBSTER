"""
Webster Alpha

Power Capability
"""

from __future__ import annotations

import os
import subprocess

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class PowerCapability(SystemCapability):
    """
    Performs operating system power actions.

    Supported actions:

    - shutdown
    - restart
    - sleep
    - lock
    """

    def __init__(self) -> None:

        super().__init__(
            name="power",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.SYSTEM,
                CapabilityPermission.POWER,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        try:

            action = self.get_string(
                request,
                "action",
            ).lower()

            if self.is_windows:
                self._windows(action)

            elif self.is_linux:
                self._linux(action)

            elif self.is_macos:
                self._macos(action)

            else:
                raise RuntimeError(
                    "Unsupported operating system."
                )

            return CapabilityResult.success_result(
                output=f"Power action '{action}' executed.",
                action=action,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )

    # ---------------------------------------------------------

    def _windows(
        self,
        action: str,
    ) -> None:

        if action == "shutdown":

            os.system("shutdown /s /t 0")

        elif action == "restart":

            os.system("shutdown /r /t 0")

        elif action == "sleep":

            subprocess.run(
                [
                    "rundll32.exe",
                    "powrprof.dll,SetSuspendState",
                    "0,1,0",
                ],
                check=True,
            )

        elif action == "lock":

            subprocess.run(
                [
                    "rundll32.exe",
                    "user32.dll,LockWorkStation",
                ],
                check=True,
            )

        else:

            raise ValueError(
                f"Unknown action '{action}'."
            )

    # ---------------------------------------------------------

    def _linux(
        self,
        action: str,
    ) -> None:

        commands = {
            "shutdown": ["shutdown", "now"],
            "restart": ["reboot"],
            "sleep": ["systemctl", "suspend"],
            "lock": ["loginctl", "lock-session"],
        }

        if action not in commands:

            raise ValueError(
                f"Unknown action '{action}'."
            )

        subprocess.run(
            commands[action],
            check=True,
        )

    # ---------------------------------------------------------

    def _macos(
        self,
        action: str,
    ) -> None:

        commands = {
            "shutdown": ["shutdown", "-h", "now"],
            "restart": ["shutdown", "-r", "now"],
            "sleep": ["pmset", "sleepnow"],
            "lock": [
                "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession",
                "-suspend",
            ],
        }

        if action not in commands:

            raise ValueError(
                f"Unknown action '{action}'."
            )

        subprocess.run(
            commands[action],
            check=True,
        )