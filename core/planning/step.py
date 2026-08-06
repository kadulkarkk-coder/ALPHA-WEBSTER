"""
Webster Alpha

Plan Step
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class PlanStep:
    """
    Represents a single executable step within a plan.
    """

    capability: str

    arguments: dict[str, Any] = field(
        default_factory=dict
    )

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: str = "pending"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    started_at: datetime | None = None

    completed_at: datetime | None = None

    result: Any | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # -----------------------------------------------------

    def mark_running(self) -> None:
        self.status = "running"
        self.started_at = datetime.utcnow()

    # -----------------------------------------------------

    def mark_completed(
        self,
        result: Any = None,
    ) -> None:

        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.result = result

    # -----------------------------------------------------

    def mark_failed(
        self,
        error: str,
    ) -> None:

        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error = error

    # -----------------------------------------------------

    @property
    def duration(self) -> float | None:
        """
        Returns execution duration in seconds.
        """

        if (
            self.started_at is None
            or self.completed_at is None
        ):
            return None

        return (
            self.completed_at
            - self.started_at
        ).total_seconds()

    # -----------------------------------------------------

    @property
    def is_finished(self) -> bool:

        return self.status in (
            "completed",
            "failed",
        )

    # -----------------------------------------------------

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "capability": self.capability,
            "arguments": self.arguments,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "duration": self.duration,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }