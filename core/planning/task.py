"""core.planning.task

Immutable Task model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class Task:
    description: str

    capability: str

    id: str = field(default_factory=lambda: str(uuid4()))

    status: str = "pending"

    arguments: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("Task.description cannot be empty")

        if not self.capability or not self.capability.strip():
            raise ValueError("Task.capability cannot be empty")

    @property
    def is_complete(self) -> bool:
        return self.status.lower() in ("completed", "done")

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"Task(id={self.id!r}, capability={self.capability!r})"
