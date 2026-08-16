"""Open a desktop application on Windows."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class OpenApplicationCapability(Capability):
    """Launch an application using a command, executable, or path."""

    def __init__(self) -> None:
        super().__init__(
            name="open_application",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.PROCESS_CONTROL,),
        )
        self._description = "Open a desktop application."
        self._supported_platforms = ("windows",)
        self._arguments = {"application": "string"}
        self._returns = {"output": "launch information"}

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            application = self.get_string(request, "application")
            if os.name != "nt":
                return CapabilityResult.failure_result(
                    "open_application currently supports Windows only."
                )

            target = shutil.which(application)
            if target is None:
                candidate = Path(application).expanduser()
                if candidate.exists():
                    target = str(candidate)

            command = target or application
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return CapabilityResult.success_result(
                output=f"Opened {application}.",
                application=application,
            )
        except Exception as exc:
            return CapabilityResult.failure_result(str(exc))
