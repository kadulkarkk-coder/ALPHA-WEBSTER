"""Webster Alpha - Create File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class CreateFileCapability(FileSystemCapability):
    """Creates a new file through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="create_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            path = self.get_path(request)
            content = request.arguments.get("content", "")
            if not isinstance(content, str):
                content = str(content)
            target = self._files.create(path, content=content)
            return CapabilityResult.success_result(
                output=str(target), path=str(target), created=True,
                bytes_written=target.stat().st_size,
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
