"""
Logger
"""

from core.logging.log_formatter import LogFormatter
from core.logging.log_handler import LogHandler
from core.logging.log_level import LogLevel


class Logger:
    """
    Webster logging interface.
    """

    def __init__(self) -> None:

        self._formatter = LogFormatter()

        self._handler = LogHandler()

        self._level = LogLevel.INFO

    @property
    def level(self) -> LogLevel:

        return self._level

    def set_level(
        self,
        level: LogLevel
    ) -> None:

        self._level = level

    def log(
        self,
        level: LogLevel,
        source: str,
        message: str
    ) -> None:

        if level < self._level:

            return

        formatted = self._formatter.format(
            level,
            source,
            message
        )

        self._handler.write(
            formatted
        )

    def debug(
        self,
        source: str,
        message: str
    ) -> None:

        self.log(
            LogLevel.DEBUG,
            source,
            message
        )

    def info(
        self,
        source: str,
        message: str
    ) -> None:

        self.log(
            LogLevel.INFO,
            source,
            message
        )

    def warning(
        self,
        source: str,
        message: str
    ) -> None:

        self.log(
            LogLevel.WARNING,
            source,
            message
        )

    def error(
        self,
        source: str,
        message: str
    ) -> None:

        self.log(
            LogLevel.ERROR,
            source,
            message
        )

    def critical(
        self,
        source: str,
        message: str
    ) -> None:

        self.log(
            LogLevel.CRITICAL,
            source,
            message
        )