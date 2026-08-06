"""
Webster Alpha

Copy File Capability
"""

from __future__ import annotations

import shutil

from core.capability.file.base import FileSystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class CopyFileCapability(FileSystemCapability):
    """
    Copies a file.
    """

    def __init__(self) -> None:

        super().__init__(
            name="copy_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.FILE_SYSTEM,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        try:

            source = self.get_path(
                request,
                "source",
            )

            destination = self.get_path(
                request,
                "destination",
            )

            self.ensure_file(source)

            self.ensure_parent(destination)

            shutil.copy2(
                source,
                destination,
            )

            return CapabilityResult.success_result(
                output=str(destination),
                source=str(source),
                destination=str(destination),
                bytes_copied=destination.stat().st_size,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )