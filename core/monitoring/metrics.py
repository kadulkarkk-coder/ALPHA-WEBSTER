"""
Metrics
"""


class Metrics:
    """
    Stores runtime metrics.
    """

    def __init__(
        self
    ) -> None:

        self._metrics: dict[
            str,
            float
        ] = {}

    def set(
        self,
        name: str,
        value: float
    ) -> None:

        self._metrics[
            name
        ] = value

    def get(
        self,
        name: str
    ) -> float:

        return self._metrics.get(
            name,
            0.0
        )

    def all(
        self
    ) -> dict[
        str,
        float
    ]:

        return self._metrics.copy()

    def clear(
        self
    ) -> None:

        self._metrics.clear()