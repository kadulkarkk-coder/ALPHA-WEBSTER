"""
Webster Alpha

Create Folder Capability
"""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class CreateFolderCapability(FileSystemCapability):
    """
    Creates a directory.
    """

    def __init__(self) -> None:

        super().__init__(
            name="create_folder",
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

            path = self.get_path(request)

            parents = self.get_boolean(
                request,
                "parents",
                True,
            )

            exist_ok = self.get_boolean(
                request,
                "exist_ok",
                True,
            )

            path.mkdir(
                parents=parents,
                exist_ok=exist_ok,
            )

            return CapabilityResult.success_result(
                output=str(path),
                path=str(path),
                created=True,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )