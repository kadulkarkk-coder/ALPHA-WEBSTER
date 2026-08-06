"""
Webster Alpha

Read File Capability
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


class ReadFileCapability(FileSystemCapability):
    """
    Reads the contents of a text file.
    """

    def __init__(self) -> None:

        super().__init__(
            name="read_file",
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
        Read a UTF-8 encoded text file.
        """

        try:

            path = self.get_path(request)

            self.ensure_file(path)

            encoding = request.arguments.get(
                "encoding",
                "utf-8",
            )

            text = path.read_text(
                encoding=encoding,
            )

            return CapabilityResult.success_result(
                output=text,
                path=str(path),
                encoding=encoding,
                size=path.stat().st_size,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )