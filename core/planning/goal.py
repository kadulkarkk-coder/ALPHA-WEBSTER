"""core.planning.goal

Immutable Goal model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class Goal:
    objective: str

    priority: int

    id: str = field(default_factory=lambda: str(uuid4()))

    created: datetime = field(default_factory=datetime.utcnow)

    metadata: dict[str, Any] = field(default_factory=dict)

    status: str = "pending"

    tags: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.objective or not self.objective.strip():
            raise ValueError("Goal.objective cannot be empty")

        if not isinstance(self.priority, int):
            raise ValueError("Goal.priority must be an int")

    @property
    def summary(self) -> str:
        return self.objective if len(self.objective) < 120 else self.objective[:117] + "..."

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"Goal(id={self.id!r}, priority={self.priority}, objective={self.summary!r})"
