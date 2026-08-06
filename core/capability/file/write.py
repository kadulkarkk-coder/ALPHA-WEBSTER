"""
Webster Alpha

Write File Capability
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


class WriteFileCapability(FileSystemCapability):
    """
    Writes text to a file.
    """

    def __init__(self) -> None:

        super().__init__(
            name="write_file",
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
        """
        Write UTF-8 text to a file.
        """

        try:

            path = self.get_path(request)

            text = self.get_text(request)

            encoding = request.arguments.get(
                "encoding",
                "utf-8",
            )

            self.ensure_parent(path)

            path.write_text(
                text,
                encoding=encoding,
            )

            return CapabilityResult.success_result(
                output=str(path),
                path=str(path),
                bytes_written=path.stat().st_size,
                encoding=encoding,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )