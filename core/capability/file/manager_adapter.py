"""Bridge between FileManager and filesystem capabilities."""

from __future__ import annotations

from pathlib import Path

from core.file.manager import FileManager
from core.file.errors import FileOperationError


class FileManagerAdapter:
    """Shared filesystem implementation used by capability code."""

    def __init__(self, manager: FileManager) -> None:
        if manager is None:
            raise ValueError("FileManager is required.")
        self.manager = manager

    def _ready(self) -> FileManager:
        if not self.manager.initialized:
            raise FileOperationError(
                "FileManager has not been initialized. Call initialize() first."
            )
        return self.manager

    def read(self, path: str | Path, encoding: str = "utf-8") -> str:
        return self._ready().read(path, encoding=encoding)

    def write(self, path: str | Path, content: str, encoding: str = "utf-8") -> Path:
        return self._ready().write(path, content, encoding=encoding)

    def create(self, path: str | Path, content: str = "") -> Path:
        return self._ready().create(path, content=content)

    def create_folder(self, path: str | Path) -> Path:
        return self._ready().create_folder(path)

    def rename(self, path: str | Path, new_name: str) -> Path:
        return self._ready().rename(path, new_name)

    def copy(self, source: str | Path, destination: str | Path) -> Path:
        return self._ready().copy(source, destination)

    def move(self, source: str | Path, destination: str | Path) -> Path:
        return self._ready().move(source, destination)

    def delete(self, path: str | Path) -> None:
        self._ready().delete(path)

    def list(self, path: str | Path = "."):
        return self._ready().list(path)

    def search(self, root: str | Path, pattern: str):
        return self._ready().search(root, pattern)
