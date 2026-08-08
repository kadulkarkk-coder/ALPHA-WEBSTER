"""High-level filesystem service for Webster."""

from __future__ import annotations

import shutil
from pathlib import Path

from core.file.errors import FileOperationError
from core.file.models import FileInfo
from core.file.safety import FileSafety


class FileManager:
    """High-level filesystem API with centralized safety validation."""

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def _require_initialized(self) -> None:
        if not self._initialized:
            raise FileOperationError(
                "FileManager has not been initialized. Call initialize() first."
            )

    def _path(self, value: str | Path) -> Path:
        self._require_initialized()
        return FileSafety.resolve_path(value)

    def exists(self, path: str | Path) -> bool:
        return self._path(path).exists()

    def info(self, path: str | Path) -> FileInfo:
        target = self._path(path)
        FileSafety.validate_existing(target)
        return FileInfo(
            path=target,
            is_file=target.is_file(),
            is_directory=target.is_dir(),
            size=target.stat().st_size if target.is_file() else 0,
        )

    def read(self, path: str | Path, encoding: str = "utf-8") -> str:
        target = self._path(path)
        FileSafety.validate_existing(target)
        if not target.is_file():
            raise FileOperationError(f"Not a file: {target}")
        try:
            return target.read_text(encoding=encoding)
        except (OSError, UnicodeError) as error:
            raise FileOperationError(str(error)) from error

    def write(self, path: str | Path, content: str, encoding: str = "utf-8") -> Path:
        target = self._path(path)
        if target.exists() and target.is_dir():
            raise FileOperationError(f"Cannot write to a directory: {target}")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding=encoding)
            return target
        except (OSError, UnicodeError) as error:
            raise FileOperationError(str(error)) from error

    def create(self, path: str | Path, content: str = "") -> Path:
        target = self._path(path)
        if target.exists():
            raise FileOperationError(f"Path already exists: {target}")
        return self.write(target, content)

    def create_folder(self, path: str | Path) -> Path:
        target = self._path(path)
        if target.exists():
            raise FileOperationError(f"Path already exists: {target}")
        try:
            target.mkdir(parents=True, exist_ok=False)
            return target
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def rename(self, path: str | Path, new_name: str) -> Path:
        target = self._path(path)
        FileSafety.validate_existing(target)
        safe_name = FileSafety.validate_name(new_name)
        destination = target.parent / safe_name
        if destination.exists():
            raise FileOperationError(f"Destination already exists: {destination}")
        try:
            return target.rename(destination)
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def copy(self, source: str | Path, destination: str | Path) -> Path:
        src = self._path(source)
        dst = self._path(destination)
        FileSafety.validate_existing(src)
        FileSafety.validate_destination(src, dst)
        if dst.exists():
            raise FileOperationError(f"Destination already exists: {dst}")
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                return Path(shutil.copytree(src, dst))
            return Path(shutil.copy2(src, dst))
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def move(self, source: str | Path, destination: str | Path) -> Path:
        src = self._path(source)
        dst = self._path(destination)
        FileSafety.validate_existing(src)
        FileSafety.validate_destination(src, dst)
        if dst.exists():
            raise FileOperationError(f"Destination already exists: {dst}")
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            return Path(shutil.move(str(src), str(dst)))
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def delete(self, path: str | Path) -> None:
        target = self._path(path)
        FileSafety.validate_existing(target)
        FileSafety.validate_delete(target)
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def list(self, path: str | Path = ".") -> list[FileInfo]:
        target = self._path(path)
        FileSafety.validate_directory(target)
        try:
            return [
                self.info(item)
                for item in sorted(target.iterdir(), key=lambda p: p.name.lower())
            ]
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def search(self, root: str | Path, pattern: str) -> list[Path]:
        target = self._path(root)
        FileSafety.validate_directory(target)
        if not str(pattern).strip():
            raise FileOperationError("Search pattern cannot be empty.")
        try:
            return sorted(
                target.rglob(str(pattern)),
                key=lambda p: str(p).lower(),
            )
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "healthy": self._initialized,
        }

    def __repr__(self) -> str:
        return f"FileManager(initialized={self._initialized})"
