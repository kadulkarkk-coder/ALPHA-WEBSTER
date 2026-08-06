"""
Performance Monitor
"""

from time import perf_counter


class PerformanceMonitor:
    """
    Measures execution performance.
    """

    def __init__(self) -> None:

        self._timers: dict[str, float] = {}

    def start(
        self,
        name: str
    ) -> None:

        self._timers[name] = perf_counter()

    def stop(
        self,
        name: str
    ) -> float:

        if name not in self._timers:

            raise KeyError(
                f"Timer '{name}' does not exist."
            )

        elapsed = (

            perf_counter()

            - self._timers[name]

        )

        del self._timers[name]

        return elapsed

    @property
    def active_timers(self) -> int:

        return len(
            self._timers
        )