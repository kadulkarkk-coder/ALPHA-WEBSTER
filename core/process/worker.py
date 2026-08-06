"""
Worker
"""

from threading import Thread
from typing import Callable


class Worker(Thread):
    """
    Executes a single background task.
    """

    def __init__(
        self,
        target: Callable,
        *args,
        **kwargs
    ) -> None:

        super().__init__(
            daemon=True
        )

        self._target = target

        self._args = args

        self._kwargs = kwargs

    def run(
        self
    ) -> None:

        self._target(
            *self._args,
            **self._kwargs
        )