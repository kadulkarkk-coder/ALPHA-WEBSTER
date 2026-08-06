"""
Webster Alpha

File Capability Pack
"""

from __future__ import annotations

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry

from core.capability.file.read import ReadFileCapability
from core.capability.file.write import WriteFileCapability
from core.capability.file.copy import CopyFileCapability
from core.capability.file.move import MoveFileCapability
from core.capability.file.rename import RenameFileCapability
from core.capability.file.delete import DeleteFileCapability
from core.capability.file.create_folder import (
    CreateFolderCapability,
)
from core.capability.file.list_directory import (
    ListDirectoryCapability,
)
from core.capability.file.search import SearchFilesCapability


class FilePack(CapabilityPack):

    @property
    def name(self) -> str:
        return "files"

    def register(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        registry.register(ReadFileCapability())
        registry.register(WriteFileCapability())
        registry.register(CopyFileCapability())
        registry.register(MoveFileCapability())
        registry.register(RenameFileCapability())
        registry.register(DeleteFileCapability())
        registry.register(CreateFolderCapability())
        registry.register(ListDirectoryCapability())
        registry.register(SearchFilesCapability())