"""
Webster Alpha

Move File Capability
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


class MoveFileCapability(FileSystemCapability):
    """
    Moves a file from one location
    to another.
    """

    def __init__(self) -> None:

        super().__init__(
            name="move_file",
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

            shutil.move(
                str(source),
                str(destination),
            )

            return CapabilityResult.success_result(
                output=str(destination),
                source=str(source),
                destination=str(destination),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )