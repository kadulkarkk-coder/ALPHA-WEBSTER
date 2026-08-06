"""
Connection
"""

import socket


class Connection:
    """
    TCP connection wrapper.
    """

    def __init__(
        self
    ) -> None:

        self._socket: socket.socket | None = None

        self._host = ""

        self._port = 0

    @property
    def connected(
        self
    ) -> bool:

        return self._socket is not None

    def connect(
        self,
        host: str,
        port: int
    ) -> None:

        self._host = host

        self._port = port

        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def disconnect(
        self
    ) -> None:

        if self._socket is not None:

            self._socket.close()

            self._socket = None

    def send(
        self,
        data: bytes
    ) -> None:

        if self._socket is None:

            raise RuntimeError(
                "Not connected."
            )

        self._socket.sendall(
            data
        )

    def receive(
        self,
        size: int = 4096
    ) -> bytes:

        if self._socket is None:

            raise RuntimeError(
                "Not connected."
            )

        return self._socket.recv(
            size
        )