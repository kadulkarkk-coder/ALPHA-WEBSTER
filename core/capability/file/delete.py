"""
Webster Alpha

Delete File Capability
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


class DeleteFileCapability(FileSystemCapability):
    """
    Deletes a file.
    """

    def __init__(self) -> None:

        super().__init__(
            name="delete_file",
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

            self.ensure_file(path)

            require_confirmation = self.get_boolean(
                request,
                "require_confirmation",
                False,
            )

            confirmed = self.get_boolean(
                request,
                "confirmed",
                False,
            )

            if require_confirmation and not confirmed:

                return CapabilityResult.failure_result(
                    error=(
                        "File deletion requires confirmation."
                    ),
                )

            path.unlink()

            return CapabilityResult.success_result(
                output=str(path),
                deleted=True,
                path=str(path),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )