"""
Webster Alpha

Execution Plan
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from core.planning.step import PlanStep


@dataclass(slots=True)
class Plan:
    """
    Represents an executable plan.
    """

    goal: str

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    steps: list[PlanStep] = field(
        default_factory=list
    )

    status: str = "pending"

    metadata: dict = field(
        default_factory=dict
    )

    # -----------------------------------------

    def add_step(
        self,
        step: PlanStep,
    ) -> None:
        """
        Add a step to the plan.
        """

        self.steps.append(step)

    # -----------------------------------------

    def insert_step(
        self,
        index: int,
        step: PlanStep,
    ) -> None:

        self.steps.insert(
            index,
            step,
        )

    # -----------------------------------------

    def remove_step(
        self,
        index: int,
    ) -> PlanStep:

        return self.steps.pop(index)

    # -----------------------------------------

    def clear(
        self,
    ) -> None:

        self.steps.clear()

    # -----------------------------------------

    @property
    def total_steps(
        self,
    ) -> int:

        return len(self.steps)

    # -----------------------------------------

    @property
    def is_empty(
        self,
    ) -> bool:

        return len(self.steps) == 0

    # -----------------------------------------

    @property
    def completed_steps(
        self,
    ) -> int:

        return sum(
            step.status == "completed"
            for step in self.steps
        )

    # -----------------------------------------

    @property
    def progress(
        self,
    ) -> float:

        if not self.steps:
            return 0.0

        return (
            self.completed_steps
            / len(self.steps)
        ) * 100

    # -----------------------------------------

    def mark_running(
        self,
    ) -> None:

        self.status = "running"

    # -----------------------------------------

    def mark_completed(
        self,
    ) -> None:

        self.status = "completed"

    # -----------------------------------------

    def mark_failed(
        self,
    ) -> None:

        self.status = "failed"

    # -----------------------------------------

    def to_dict(
        self,
    ) -> dict:

        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "progress": self.progress,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "metadata": self.metadata,
        }