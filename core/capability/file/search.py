"""
Webster Alpha

Search Files Capability
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


class SearchFilesCapability(FileSystemCapability):
    """
    Searches for files and directories.
    """

    def __init__(self) -> None:

        super().__init__(
            name="search_files",
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

            root = self.get_path(request)

            self.ensure_directory(root)

            pattern = self.get_string(
                request,
                "pattern",
            )

            recursive = self.get_boolean(
                request,
                "recursive",
                True,
            )

            files_only = self.get_boolean(
                request,
                "files_only",
                False,
            )

            directories_only = self.get_boolean(
                request,
                "directories_only",
                False,
            )

            case_sensitive = self.get_boolean(
                request,
                "case_sensitive",
                False,
            )

            iterator = (
                root.rglob("*")
                if recursive
                else root.iterdir()
            )

            matches = []

            pattern_cmp = (
                pattern
                if case_sensitive
                else pattern.lower()
            )

            for item in iterator:

                if files_only and not item.is_file():
                    continue

                if directories_only and not item.is_dir():
                    continue

                name = (
                    item.name
                    if case_sensitive
                    else item.name.lower()
                )

                if Path(name).match(pattern_cmp):

                    matches.append(
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
                output=matches,
                root=str(root),
                pattern=pattern,
                count=len(matches),
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )