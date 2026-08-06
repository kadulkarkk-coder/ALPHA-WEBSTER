"""
Webster Alpha

Open Folder Capability
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


class OpenFolderCapability(SystemCapability):
    """
    Opens a folder in the operating system's
    default file manager.
    """

    def __init__(self) -> None:

        super().__init__(
            name="open_folder",
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

            folder = self.get_existing_path(request)

            if not folder.is_dir():
                raise NotADirectoryError(
                    f"'{folder}' is not a directory."
                )

            if self.is_windows:

                os.startfile(str(folder))

            elif self.is_macos:

                subprocess.Popen(
                    ["open", str(folder)]
                )

            elif self.is_linux:

                subprocess.Popen(
                    ["xdg-open", str(folder)]
                )

            else:

                raise RuntimeError(
                    "Unsupported operating system."
                )

            return CapabilityResult.success_result(
                output=str(folder),
                path=str(folder),
                opened=True,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )