"""Webster Alpha - Write File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class WriteFileCapability(FileSystemCapability):
    """Writes text to a file through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="write_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            path = self.get_path(request)
            text = self.get_text(request)
            encoding = request.arguments.get("encoding", "utf-8")
            target = self._files.write(path, text, encoding=encoding)
            return CapabilityResult.success_result(
                output=str(target),
                path=str(target),
                bytes_written=target.stat().st_size,
                encoding=encoding,
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
