"""High-level filesystem service for Webster."""

from __future__ import annotations

import shutil
from pathlib import Path

from core.file.errors import FileOperationError
from core.file.models import FileInfo


class FileManager:
    """Safe, small high-level API over the local filesystem."""

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False

    @property
    def initialized(self) -> bool:
        return self._initialized

    def _path(self, value: str | Path) -> Path:
        path = Path(value).expanduser()
        if not str(path).strip():
            raise FileOperationError("Path cannot be empty.")
        return path.resolve()

    def exists(self, path: str | Path) -> bool:
        return self._path(path).exists()

    def info(self, path: str | Path) -> FileInfo:
        target = self._path(path)
        if not target.exists():
            raise FileOperationError(f"Path does not exist: {target}")
        return FileInfo(
            path=target,
            is_file=target.is_file(),
            is_directory=target.is_dir(),
            size=target.stat().st_size if target.is_file() else 0,
        )

    def read(self, path: str | Path, encoding: str = "utf-8") -> str:
        target = self._path(path)
        try:
            return target.read_text(encoding=encoding)
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def write(self, path: str | Path, content: str, encoding: str = "utf-8") -> Path:
        target = self._path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding=encoding)
            return target
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def create(self, path: str | Path, content: str = "") -> Path:
        target = self._path(path)
        if target.exists():
            raise FileOperationError(f"Path already exists: {target}")
        return self.write(target, content)

    def create_folder(self, path: str | Path) -> Path:
        target = self._path(path)
        try:
            target.mkdir(parents=True, exist_ok=False)
            return target
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def rename(self, path: str | Path, new_name: str) -> Path:
        target = self._path(path)
        if not target.exists():
            raise FileOperationError(f"Path does not exist: {target}")
        if not new_name.strip() or Path(new_name).name != new_name:
            raise FileOperationError("New name must be a non-empty filename.")
        destination = target.parent / new_name
        try:
            return target.rename(destination)
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def copy(self, source: str | Path, destination: str | Path) -> Path:
        src = self._path(source)
        dst = self._path(destination)
        if not src.exists():
            raise FileOperationError(f"Source does not exist: {src}")
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                return Path(shutil.copytree(src, dst, dirs_exist_ok=True))
            return Path(shutil.copy2(src, dst))
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def move(self, source: str | Path, destination: str | Path) -> Path:
        src = self._path(source)
        dst = self._path(destination)
        if not src.exists():
            raise FileOperationError(f"Source does not exist: {src}")
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            return Path(shutil.move(str(src), str(dst)))
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def delete(self, path: str | Path) -> None:
        target = self._path(path)
        if not target.exists():
            raise FileOperationError(f"Path does not exist: {target}")
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        except OSError as error:
            raise FileOperationError(str(error)) from error

    def list(self, path: str | Path = ".") -> list[FileInfo]:
        target = self._path(path)
        if not target.is_dir():
            raise FileOperationError(f"Not a directory: {target}")
        return [self.info(item) for item in sorted(target.iterdir(), key=lambda p: p.name.lower())]

    def search(self, root: str | Path, pattern: str) -> list[Path]:
        target = self._path(root)
        if not target.is_dir():
            raise FileOperationError(f"Not a directory: {target}")
        if not pattern.strip():
            raise FileOperationError("Search pattern cannot be empty.")
        return sorted(target.rglob(pattern), key=lambda p: str(p).lower())

    def health(self) -> dict:
        return {"initialized": self._initialized, "healthy": self._initialized}

    def __repr__(self) -> str:
        return f"FileManager(initialized={self._initialized})"
