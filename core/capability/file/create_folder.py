"""Webster Alpha - Create Folder Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class CreateFolderCapability(FileSystemCapability):
    """Creates a directory through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="create_folder",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            path = self.get_path(request)
            exist_ok = self.get_boolean(request, "exist_ok", True)
            if path.exists():
                if path.is_dir() and exist_ok:
                    return CapabilityResult.success_result(
                        output=str(path), path=str(path), created=False, existing=True
                    )
                raise FileExistsError(f"Path already exists: {path}")
            created = self._files.create_folder(path)
            return CapabilityResult.success_result(
                output=str(created), path=str(created), created=True
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
