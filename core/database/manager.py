"""
Database Manager
"""

from core.database.database import Database
from core.database.models import Table


class DatabaseManager:
    """
    Manages Webster database.
    """

    def __init__(self) -> None:

        self._database = Database()

        self._tables: dict[
            str,
            Table
        ] = {}

    @property
    def database(
        self
    ) -> Database:

        return self._database

    @property
    def table_count(
        self
    ) -> int:

        return len(
            self._tables
        )

    def register(
        self,
        table: Table
    ) -> None:

        self._tables[
            table.name
        ] = table

    def get(
        self,
        name: str
    ) -> Table:

        return self._tables[
            name
        ]

    def create_tables(
        self
    ) -> None:

        self._database.connect()

        for table in self._tables.values():

            self._database.connection.execute(
                table.schema
            )

    def close(
        self
    ) -> None:

        self._database.disconnect()