"""
Webster Alpha

Rename File Capability
"""

from __future__ import annotations

from pathlib import Path

from core.capability.file.base import FileSystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class RenameFileCapability(FileSystemCapability):
    """
    Renames a file while keeping it
    in the same directory.
    """

    def __init__(self) -> None:

        super().__init__(
            name="rename_file",
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

            self.ensure_file(source)

            new_name = self.get_string(
                request,
                "new_name",
            )

            destination = source.with_name(
                new_name,
            )

            source.rename(
                destination,
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