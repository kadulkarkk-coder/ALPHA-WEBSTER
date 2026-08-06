"""
PlanningContext model for Planning Intelligence Layer
"""core.planning.context

PlanningContext stores planning-time variables and references.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .goal import Goal


@dataclass(slots=True)
class PlanningContext:
    goal: Goal

    variables: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    # Conversation references and execution hints may be added to metadata

    def validate(self) -> None:
        if self.goal is None:
            raise ValueError("PlanningContext.goal is required")

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def has_variable(self, key: str) -> bool:
        return key in self.variables

    def clear(self) -> None:
        self.variables.clear()

    def __repr__(self) -> str:  # pragma: no cover - small helper
        return f"PlanningContext(goal={self.goal.id!r}, vars={len(self.variables)})"
