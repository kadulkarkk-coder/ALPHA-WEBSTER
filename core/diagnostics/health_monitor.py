"""
Health Monitor
"""

from datetime import datetime

from core.diagnostics.diagnostic_report import (
    DiagnosticReport
)


class HealthMonitor:
    """
    Webster health monitoring system.
    """

    def __init__(self) -> None:

        self._checks: dict[str, bool] = {}

        self._last_check = datetime.now()

    @property
    def total_checks(self) -> int:

        return len(
            self._checks
        )

    @property
    def last_check(self) -> datetime:

        return self._last_check

    def update(
        self,
        component: str,
        status: bool
    ) -> None:

        self._checks[
            component
        ] = status

        self._last_check = datetime.now()

    def is_healthy(self) -> bool:

        return all(
            self._checks.values()
        ) if self._checks else True

    def get_checks(self) -> dict:

        return self._checks.copy()

    def create_report(self) -> DiagnosticReport:

        report = DiagnosticReport()

        report.health = self.get_checks()

        return report