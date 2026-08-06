"""
Log Formatter
"""

from datetime import datetime

from core.logging.log_level import LogLevel


class LogFormatter:
    """
    Formats Webster log messages.
    """

    def format(
        self,
        level: LogLevel,
        source: str,
        message: str
    ) -> str:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"[{timestamp}] "
            f"[{level.name}] "
            f"[{source}] "
            f"{message}"
        )