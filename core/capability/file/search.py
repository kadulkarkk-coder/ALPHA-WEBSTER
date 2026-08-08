"""Webster Alpha - Search Files Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class SearchFilesCapability(FileSystemCapability):
    """Searches files through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="search_files",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            root = self.get_path(request)
            pattern = self.get_string(request, "pattern")
            recursive = self.get_boolean(request, "recursive", True)
            files_only = self.get_boolean(request, "files_only", False)
            directories_only = self.get_boolean(request, "directories_only", False)
            matches = self._files.search(root, pattern) if recursive else self._files.manager.list(root)
            if not recursive:
                paths = [info.path for info in matches]
            else:
                paths = matches
            output = []
            for path in paths:
                if files_only and not path.is_file():
                    continue
                if directories_only and not path.is_dir():
                    continue
                output.append({
                    "name": path.name,
                    "path": str(path),
                    "type": "directory" if path.is_dir() else "file",
                    "size": path.stat().st_size if path.is_file() else None,
                })
            return CapabilityResult.success_result(
                output=output, root=str(root), pattern=pattern, count=len(output)
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
