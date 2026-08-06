"""
File
"""

from pathlib import Path


class File:
    """
    Represents a filesystem file.
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

    @property
    def exists(
        self
    ) -> bool:

        return self._path.exists()

    @property
    def name(
        self
    ) -> str:

        return self._path.name

    @property
    def suffix(
        self
    ) -> str:

        return self._path.suffix

    def read(
        self,
        encoding: str = "utf-8"
    ) -> str:

        return self._path.read_text(
            encoding=encoding
        )

    def write(
        self,
        data: str,
        encoding: str = "utf-8"
    ) -> None:

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._path.write_text(
            data,
            encoding=encoding
        )

    def delete(
        self
    ) -> None:

        if self.exists:

            self._path.unlink()