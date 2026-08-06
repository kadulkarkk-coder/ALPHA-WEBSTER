"""
Task Runner
"""

from threading import Thread
from time import sleep

from core.scheduler.task import Task


class TaskRunner(Thread):
    """
    Executes scheduled tasks.
    """

    def __init__(
        self,
        task: Task
    ) -> None:

        super().__init__(
            daemon=True
        )

        self._task = task

        self._running = False

    def run(self) -> None:

        self._running = True

        while self._running:

            sleep(
                self._task.interval
            )

            if not self._task.enabled:

                continue

            self._task.callback()

            if not self._task.repeat:

                break

    def stop(self) -> None:

        self._running = False