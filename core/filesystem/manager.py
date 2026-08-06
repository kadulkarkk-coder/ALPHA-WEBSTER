"""
Filesystem Manager
"""

from core.filesystem.file import File
from core.filesystem.directory import Directory
from core.filesystem.watcher import Watcher


class FilesystemManager:
    """
    Controls Webster filesystem operations.
    """

    def __init__(
        self
    ) -> None:

        self._watcher = Watcher()

    @property
    def watcher(
        self
    ) -> Watcher:

        return self._watcher

    def file(
        self,
        path: str
    ) -> File:

        return File(
            path
        )

    def directory(
        self,
        path: str
    ) -> Directory:

        return Directory(
            path
        )

    def watch(
        self,
        path: str
    ) -> None:

        self._watcher.watch(
            path
        )

    def changed(
        self,
        path: str
    ) -> bool:

        return self._watcher.changed(
            path
        )