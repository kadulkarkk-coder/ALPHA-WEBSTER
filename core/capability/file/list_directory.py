"""
Webster Alpha

List Directory Capability
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


class ListDirectoryCapability(FileSystemCapability):
    """
    Lists the contents of a directory.
    """

    def __init__(self) -> None:

        super().__init__(
            name="list_directory",
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

            directory = self.get_path(request)

            self.ensure_directory(directory)

            recursive = self.get_boolean(
                request,
                "recursive",
                False,
            )

            include_hidden = self.get_boolean(
                request,
                "include_hidden",
                False,
            )

            items = []

            iterator = (
                directory.rglob("*")
                if recursive
                else directory.iterdir()
            )

            for item in iterator:

                if (
                    not include_hidden
                    and item.name.startswith(".")
                ):
                    continue

                items.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "type": (
                            "directory"
                            if item.is_dir()
                            else "file"
                        ),
                        "size": (
                            item.stat().st_size
                            if item.is_file()
                            else None
                        ),
                    }
                )

            return CapabilityResult.success_result(
                output=items,
                path=str(directory),
                count=len(items),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )