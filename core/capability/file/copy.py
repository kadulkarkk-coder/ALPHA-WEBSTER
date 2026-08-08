"""Webster Alpha - Copy File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class CopyFileCapability(FileSystemCapability):
    """Copies a file or directory through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="copy_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            source = self.get_path(request, "source")
            destination = self.get_path(request, "destination")
            self.ensure_file(source)
            target = self._files.copy(source, destination)
            return CapabilityResult.success_result(
                output=str(target), source=str(source), destination=str(target),
                bytes_copied=target.stat().st_size if target.is_file() else None,
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
