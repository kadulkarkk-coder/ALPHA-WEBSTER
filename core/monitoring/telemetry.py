"""
Telemetry
"""

from datetime import datetime


class Telemetry:
    """
    Collects runtime events.
    """

    def __init__(
        self
    ) -> None:

        self._events: list[
            dict
        ] = []

    @property
    def count(
        self
    ) -> int:

        return len(
            self._events
        )

    def record(
        self,
        name: str,
        value: object
    ) -> None:

        self._events.append(

            {

                "time": datetime.now(),

                "name": name,

                "value": value

            }

        )

    def all(
        self
    ) -> list[dict]:

        return self._events.copy()

    def clear(
        self
    ) -> None:

        self._events.clear()