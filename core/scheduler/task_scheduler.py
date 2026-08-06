"""
Task Scheduler
"""

from threading import Lock

from core.scheduler.task import Task


class TaskScheduler:
    """
    Stores and manages scheduled tasks.
    """

    def __init__(self) -> None:

        self._tasks: dict[str, Task] = {}

        self._lock = Lock()

    @property
    def task_count(self) -> int:
        """
        Return total number of tasks.
        """

        return len(self._tasks)

    def add_task(
        self,
        task: Task
    ) -> None:
        """
        Register a task.
        """

        with self._lock:

            self._tasks[task.task_id] = task

    def remove_task(
        self,
        task_id: str
    ) -> None:
        """
        Remove a task.
        """

        with self._lock:

            self._tasks.pop(
                task_id,
                None
            )

    def get_task(
        self,
        task_id: str
    ) -> Task:

        return self._tasks[task_id]

    def all_tasks(self) -> list[Task]:
        """
        Return every registered task.
        """

        return list(
            self._tasks.values()
        )

    def clear(self) -> None:
        """
        Remove every task.
        """

        with self._lock:

            self._tasks.clear()