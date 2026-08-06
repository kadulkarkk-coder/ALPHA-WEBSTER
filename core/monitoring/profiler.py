"""
Profiler
"""

from time import perf_counter


class Profiler:
    """
    Measures execution time.
    """

    def __init__(
        self
    ) -> None:

        self._starts: dict[
            str,
            float
        ] = {}

    def start(
        self,
        name: str
    ) -> None:

        self._starts[
            name
        ] = perf_counter()

    def stop(
        self,
        name: str
    ) -> float:

        elapsed = (

            perf_counter()

            -

            self._starts.pop(
                name
            )

        )

        return elapsed