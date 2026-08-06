"""
System Monitor
"""

from datetime import datetime

import platform
import sys


class SystemMonitor:
    """
    Collects basic information about the
    running Webster environment.
    """

    def __init__(self) -> None:

        self._started_at = datetime.now()

    @property
    def started_at(self) -> datetime:

        return self._started_at

    def get_system_information(self) -> dict:

        return {

            "platform": platform.system(),

            "platform_release": platform.release(),

            "platform_version": platform.version(),

            "machine": platform.machine(),

            "processor": platform.processor(),

            "python_version": sys.version.split()[0]
        }

    def uptime(self) -> float:

        return (

            datetime.now()

            - self._started_at

        ).total_seconds()