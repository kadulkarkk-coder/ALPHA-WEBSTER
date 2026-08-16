"""Close a desktop application on Windows."""

from __future__ import annotations

import os
import subprocess

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class CloseApplicationCapability(Capability):
    """Close processes by executable name."""

    def __init__(self) -> None:
        super().__init__(
            name="close_application",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.PROCESS_CONTROL,),
        )
        self._description = "Close a desktop application by process name."
        self._supported_platforms = ("windows",)
        self._arguments = {"application": "string"}
        self._returns = {"output": "termination information"}

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            application = self.get_string(request, "application")
            if os.name != "nt":
                return CapabilityResult.failure_result(
                    "close_application currently supports Windows only."
                )

            name = application if application.lower().endswith(".exe") else f"{application}.exe"
            completed = subprocess.run(
                ["taskkill", "/IM", name, "/T"],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                error = (completed.stderr or completed.stdout).strip()
                return CapabilityResult.failure_result(
                    error or f"Could not close {application}."
                )

            return CapabilityResult.success_result(
                output=f"Closed {application}.",
                application=application,
            )
        except Exception as exc:
            return CapabilityResult.failure_result(str(exc))
