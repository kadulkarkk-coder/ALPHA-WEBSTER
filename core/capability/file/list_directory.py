"""Webster Alpha - List Directory Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class ListDirectoryCapability(FileSystemCapability):
    """Lists a directory through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="list_directory",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            directory = self.get_path(request)
            recursive = self.get_boolean(request, "recursive", False)
            include_hidden = self.get_boolean(request, "include_hidden", False)
            items = self._files.list(directory)
            if recursive:
                paths = self._files.search(directory, "*")
                items = [self._files.manager.info(p) for p in paths]
            output = []
            for info in items:
                if not include_hidden and info.path.name.startswith("."):
                    continue
                output.append({
                    "name": info.path.name,
                    "path": str(info.path),
                    "type": "directory" if info.is_directory else "file",
                    "size": info.size if info.is_file else None,
                })
            return CapabilityResult.success_result(
                output=output, path=str(directory), count=len(output)
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
