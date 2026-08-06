"""
Monitoring Manager
"""

from core.monitoring.telemetry import Telemetry
from core.monitoring.metrics import Metrics
from core.monitoring.profiler import Profiler


class MonitoringManager:
    """
    Controls Webster monitoring.
    """

    def __init__(
        self
    ) -> None:

        self._telemetry = Telemetry()

        self._metrics = Metrics()

        self._profiler = Profiler()

    @property
    def telemetry(
        self
    ) -> Telemetry:

        return self._telemetry

    @property
    def metrics(
        self
    ) -> Metrics:

        return self._metrics

    @property
    def profiler(
        self
    ) -> Profiler:

        return self._profiler

    def clear(
        self
    ) -> None:

        self._telemetry.clear()

        self._metrics.clear()