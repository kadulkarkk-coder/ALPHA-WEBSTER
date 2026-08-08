"""Webster Alpha - Read File Capability."""

from __future__ import annotations

from core.capability.file.base import FileSystemCapability
from core.capability.file.manager_adapter import FileManagerAdapter
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.file.manager import FileManager


class ReadFileCapability(FileSystemCapability):
    """Reads a text file through the shared FileManager."""

    def __init__(self, file_manager: FileManager | None = None) -> None:
        super().__init__(
            name="read_file",
            capability_type=CapabilityType.FILE,
            category=CapabilityCategory.SYSTEM,
            permissions=(CapabilityPermission.FILE_SYSTEM,),
        )
        self._files = FileManagerAdapter(file_manager or FileManager())

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            path = self.get_path(request)
            self.ensure_file(path)
            encoding = request.arguments.get("encoding", "utf-8")
            text = self._files.read(path, encoding=encoding)
            return CapabilityResult.success_result(
                output=text,
                path=str(path),
                encoding=encoding,
                size=path.stat().st_size,
            )
        except Exception as error:
            return CapabilityResult.failure_result(error=str(error))
