"""Errors raised by the Webster file service."""

from __future__ import annotations


class FileServiceError(RuntimeError):
    """Base error for file-service operations."""


class FileOperationError(FileServiceError):
    """Raised when a filesystem operation fails."""
