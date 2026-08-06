"""
Startup
"""

from typing import Callable


class Startup:
    """
    Manages Webster startup tasks.
    """

    def __init__(
        self
    ) -> None:

        self._tasks: list[
            Callable[[], None]
        ] = []

    @property
    def count(
        self
    ) -> int:

        return len(
            self._tasks
        )

    def register(
        self,
        task: Callable[[], None]
    ) -> None:

        self._tasks.append(
            task
        )

    def run(
        self
    ) -> None:

        for task in self._tasks:

            task()

    def clear(
        self
    ) -> None:

        self._tasks.clear()