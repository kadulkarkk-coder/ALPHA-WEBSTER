"""
Worker Pool
"""

from core.process.worker import Worker


class WorkerPool:
    """
    Manages Webster workers.
    """

    def __init__(
        self
    ) -> None:

        self._workers: list[
            Worker
        ] = []

    @property
    def count(
        self
    ) -> int:

        return len(
            self._workers
        )

    def add(
        self,
        worker: Worker
    ) -> None:

        self._workers.append(
            worker
        )

    def start_all(
        self
    ) -> None:

        for worker in self._workers:

            worker.start()

    def join_all(
        self
    ) -> None:

        for worker in self._workers:

            worker.join()

    def clear(
        self
    ) -> None:

        self._workers.clear()