"""
Directory
"""

from pathlib import Path

from core.filesystem.file import File


class Directory:
    """
    Represents a filesystem directory.
    """

    def __init__(
        self,
        path: str
    ) -> None:

        self._path = Path(
            path
        )

    @property
    def path(
        self
    ) -> Path:

        return self._path

    def create(
        self
    ) -> None:

        self._path.mkdir(
            parents=True,
            exist_ok=True
        )

    def exists(
        self
    ) -> bool:

        return self._path.exists()

    def files(
        self
    ) -> list[File]:

        return [

            File(
                str(file)
            )

            for file in self._path.iterdir()

            if file.is_file()

        ]