"""
Database
"""

from pathlib import Path

from core.database.connection import DatabaseConnection


class Database:
    """
    Webster database.
    """

    def __init__(
        self,
        path: str = "data/webster.db"
    ) -> None:

        self._path = Path(path)

        self._connection = DatabaseConnection(
            self._path
        )

    @property
    def connection(
        self
    ) -> DatabaseConnection:

        return self._connection

    @property
    def path(
        self
    ) -> Path:

        return self._path

    def connect(
        self
    ) -> None:

        self._connection.connect()

    def disconnect(
        self
    ) -> None:

        self._connection.disconnect()