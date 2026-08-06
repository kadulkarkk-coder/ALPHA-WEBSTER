"""
Log Handler
"""

from pathlib import Path
from threading import Lock


class LogHandler:
    """
    Writes formatted logs.
    """

    def __init__(
        self,
        log_directory: str = "logs"
    ) -> None:

        self._lock = Lock()

        self._directory = Path(
            log_directory
        )

        self._directory.mkdir(
            parents=True,
            exist_ok=True
        )

        self._file = (
            self._directory
            / "webster.log"
        )

    def write(
        self,
        message: str
    ) -> None:

        with self._lock:

            with open(
                self._file,
                "a",
                encoding="utf-8"
            ) as file:

                file.write(
                    message + "\n"
                )