"""Webster Alpha - Rename File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class RenameFileCapability(FileSystemCapability):
    """Renames a filesystem entry through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="rename_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            source = self.get_path(request, "source")
            self.ensure_file(source)
            new_name = self.get_string(request, "new_name")
            destination = self._files.rename(source, new_name)
            return CapabilityResult.success_result(
                output=str(destination), source=str(source), destination=str(destination)
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
