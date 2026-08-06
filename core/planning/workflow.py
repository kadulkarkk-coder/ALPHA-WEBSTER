"""
Webster Alpha

Workflow
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from core.planning.plan import Plan


@dataclass(slots=True)
class Workflow:
    """
    Represents a collection of plans executed
    as a single workflow.
    """

    name: str

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    plans: list[Plan] = field(
        default_factory=list
    )

    status: str = "pending"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # -------------------------------------------------

    def add_plan(
        self,
        plan: Plan,
    ) -> None:

        self.plans.append(plan)

    # -------------------------------------------------

    def remove_plan(
        self,
        index: int,
    ) -> Plan:

        return self.plans.pop(index)

    # -------------------------------------------------

    def clear(
        self,
    ) -> None:

        self.plans.clear()

    # -------------------------------------------------

    @property
    def total_plans(
        self,
    ) -> int:

        return len(self.plans)

    # -------------------------------------------------

    @property
    def completed_plans(
        self,
    ) -> int:

        return sum(
            plan.status == "completed"
            for plan in self.plans
        )

    # -------------------------------------------------

    @property
    def progress(
        self,
    ) -> float:

        if not self.plans:
            return 0.0

        return (
            self.completed_plans
            / len(self.plans)
        ) * 100

    # -------------------------------------------------

    def mark_running(
        self,
    ) -> None:

        self.status = "running"

    # -------------------------------------------------

    def mark_completed(
        self,
    ) -> None:

        self.status = "completed"

    # -------------------------------------------------

    def mark_failed(
        self,
    ) -> None:

        self.status = "failed"

    # -------------------------------------------------

    def to_dict(
        self,
    ) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "progress": self.progress,
            "plans": [
                plan.to_dict()
                for plan in self.plans
            ],
            "metadata": self.metadata,
        }