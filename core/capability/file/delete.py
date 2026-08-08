"""Webster Alpha - Delete File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class DeleteFileCapability(FileSystemCapability):
    """Deletes a file through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="delete_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            path = self.get_path(request)
            self.ensure_file(path)
            require_confirmation = self.get_boolean(request, "require_confirmation", False)
            confirmed = self.get_boolean(request, "confirmed", False)
            if require_confirmation and not confirmed:
                return CapabilityResult.failure_result(
                    error="File deletion requires confirmation."
                )
            self._files.delete(path)
            return CapabilityResult.success_result(
                output=str(path), deleted=True, path=str(path)
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
