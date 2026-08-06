"""
Hooks
"""

from typing import Callable


class Hooks:
    """
    System hook manager.
    """

    def __init__(
        self
    ) -> None:

        self._hooks: dict[
            str,
            list[Callable]
        ] = {}

    def register(
        self,
        event: str,
        callback: Callable
    ) -> None:

        self._hooks.setdefault(
            event,
            []
        ).append(
            callback
        )

    def execute(
        self,
        event: str,
        *args,
        **kwargs
    ) -> None:

        for callback in self._hooks.get(
            event,
            []
        ):

            callback(
                *args,
                **kwargs
            )

    def remove(
        self,
        event: str
    ) -> None:

        self._hooks.pop(
            event,
            None
        )