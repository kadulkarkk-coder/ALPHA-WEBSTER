"""
Network
"""

from core.network.connection import Connection


class Network:
    """
    Webster network interface.
    """

    def __init__(
        self
    ) -> None:

        self._connection = Connection()

    @property
    def connection(
        self
    ) -> Connection:

        return self._connection

    @property
    def connected(
        self
    ) -> bool:

        return self._connection.connected

    def connect(
        self,
        host: str,
        port: int
    ) -> None:

        self._connection.connect(
            host,
            port
        )

    def disconnect(
        self
    ) -> None:

        self._connection.disconnect()