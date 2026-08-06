"""
Watcher
"""

from pathlib import Path
from datetime import datetime


class Watcher:
    """
    Watches filesystem changes.
    """

    def __init__(
        self
    ) -> None:

        self._paths: dict[
            str,
            datetime
        ] = {}

    def watch(
        self,
        path: str
    ) -> None:

        file = Path(
            path
        )

        if file.exists():

            self._paths[
                path
            ] = datetime.fromtimestamp(
                file.stat().st_mtime
            )

    def changed(
        self,
        path: str
    ) -> bool:

        file = Path(
            path
        )

        if (
            path not in self._paths
            or
            not file.exists()
        ):

            return False

        modified = datetime.fromtimestamp(
            file.stat().st_mtime
        )

        return modified > self._paths[
            path
        ]

    def refresh(
        self,
        path: str
    ) -> None:

        file = Path(
            path
        )

        if file.exists():

            self._paths[
                path
            ] = datetime.fromtimestamp(
                file.stat().st_mtime
            )