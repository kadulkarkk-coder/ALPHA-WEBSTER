"""
Database Connection
"""

import sqlite3

from pathlib import Path


class DatabaseConnection:
    """
    SQLite connection wrapper.
    """

    def __init__(
        self,
        path: Path
    ) -> None:

        self._path = path

        self._connection: sqlite3.Connection | None = None

    @property
    def connected(
        self
    ) -> bool:

        return self._connection is not None

    def connect(
        self
    ) -> None:

        self._path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._connection = sqlite3.connect(
            self._path
        )

    def disconnect(
        self
    ) -> None:

        if self._connection is not None:

            self._connection.close()

            self._connection = None

    def execute(
        self,
        query: str,
        parameters: tuple = ()
    ) -> sqlite3.Cursor:

        if self._connection is None:

            raise RuntimeError(
                "Database is not connected."
            )

        cursor = self._connection.cursor()

        cursor.execute(
            query,
            parameters
        )

        self._connection.commit()

        return cursor