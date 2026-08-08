"""Safety policy for Webster filesystem operations."""

from __future__ import annotations

import os
from pathlib import Path

from core.file.errors import FileOperationError


class FileSafety:
    """Centralized validation for filesystem paths and destructive actions."""

    @staticmethod
    def resolve_path(value: str | Path) -> Path:
        if value is None:
            raise FileOperationError("Path cannot be None.")
        raw = str(value).strip()
        if not raw:
            raise FileOperationError("Path cannot be empty.")
        try:
            return Path(raw).expanduser().resolve()
        except (OSError, RuntimeError, ValueError) as error:
            raise FileOperationError(f"Invalid path: {raw}") from error

    @staticmethod
    def validate_name(name: str) -> str:
        value = str(name).strip()
        if not value:
            raise FileOperationError("Filename cannot be empty.")
        if value in {".", ".."} or Path(value).name != value:
            raise FileOperationError("Filename must not contain path separators.")
        if any(char in value for char in '<>:"|?*'):
            raise FileOperationError(f"Invalid filename: {value}")
        if os.name == "nt" and value.rstrip(" .") != value:
            raise FileOperationError("Windows filenames cannot end with spaces or periods.")
        return value

    @staticmethod
    def validate_destination(source: Path, destination: Path) -> None:
        if source == destination:
            raise FileOperationError("Source and destination cannot be the same.")
        if source.is_dir():
            try:
                destination.relative_to(source)
            except ValueError:
                return
            raise FileOperationError("A directory cannot be copied or moved into itself.")

    @staticmethod
    def validate_delete(target: Path) -> None:
        """Reject filesystem roots and the current working directory."""
        resolved = target.resolve()
        if resolved.parent == resolved:
            raise FileOperationError("Deleting a filesystem root is not allowed.")
        cwd = Path.cwd().resolve()
        if resolved == cwd:
            raise FileOperationError("Deleting the Webster working directory is not allowed.")

    @staticmethod
    def validate_existing(target: Path) -> None:
        if not target.exists():
            raise FileOperationError(f"Path does not exist: {target}")

    @staticmethod
    def validate_directory(target: Path) -> None:
        if not target.is_dir():
            raise FileOperationError(f"Not a directory: {target}")
