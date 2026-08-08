"""Models used by the Webster file service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileInfo:
    """Small immutable description of a filesystem entry."""

    path: Path
    is_file: bool
    is_directory: bool
    size: int = 0


@dataclass(frozen=True, slots=True)
class FileOperationResult:
    """Standard result for a file operation."""

    success: bool
    path: Path | None = None
    message: str = ""
