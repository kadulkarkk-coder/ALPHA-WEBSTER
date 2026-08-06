"""
Process Manager
"""

from datetime import datetime
from typing import Callable

from core.process.process import Process
from core.process.pool import WorkerPool
from core.process.worker import Worker


class ProcessManager:
    """
    Controls Webster processes.
    """

    def __init__(
        self
    ) -> None:

        self._processes: dict[
            str,
            Process
        ] = {}

        self._pool = WorkerPool()

    @property
    def count(
        self
    ) -> int:

        return len(
            self._processes
        )

    @property
    def workers(
        self
    ) -> WorkerPool:

        return self._pool

    def create(
        self,
        name: str,
        target: Callable,
        *args,
        **kwargs
    ) -> Process:

        process = Process(
            name=name
        )

        worker = Worker(
            target,
            *args,
            **kwargs
        )

        self._processes[
            process.process_id
        ] = process

        self._pool.add(
            worker
        )

        return process

    def start(
        self,
        process_id: str
    ) -> None:

        process = self._processes[
            process_id
        ]

        process.status = "running"

        process.started_at = datetime.now()

    def finish(
        self,
        process_id: str
    ) -> None:

        process = self._processes[
            process_id
        ]

        process.status = "finished"

        process.finished_at = datetime.now()

    def get(
        self,
        process_id: str
    ) -> Process:

        return self._processes[
            process_id
        ]

    def remove(
        self,
        process_id: str
    ) -> None:

        self._processes.pop(
            process_id,
            None
        )

    def all(
        self
    ) -> list[Process]:

        return list(
            self._processes.values()
        )

    def clear(
        self
    ) -> None:

        self._processes.clear()

        self._pool.clear()