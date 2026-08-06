"""
Resource Monitor
"""

from datetime import datetime

from core.resources.resource import Resource


class ResourceMonitor:
    """
    Tracks resource usage.
    """

    def __init__(
        self
    ) -> None:

        self._usage: dict[
            str,
            int
        ] = {}

    def touch(
        self,
        resource: Resource
    ) -> None:

        resource.last_used = datetime.now()

        self._usage[
            resource.name
        ] = self._usage.get(
            resource.name,
            0
        ) + 1

    def usage(
        self,
        name: str
    ) -> int:

        return self._usage.get(
            name,
            0
        )

    def reset(
        self
    ) -> None:

        self._usage.clear()