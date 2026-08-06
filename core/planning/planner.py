"""
Webster Alpha

Planner
"""

from __future__ import annotations

from typing import Iterable, List

from core.capability.registry import CapabilityRegistry
from core.planning.plan import Plan
from core.planning.step import PlanStep
from core.planning.task import Task


class Planner:
    """
    Planner converts Tasks into Plan and PlanSteps.
    """

    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    def create_plan(self, goal_text: str, tasks: Iterable[Task] | None = None) -> Plan:
        plan = Plan(goal=goal_text)

        if tasks:
            for task in tasks:
                step = PlanStep(capability=task.capability, arguments=task.arguments or {})
                step.metadata.update(task.metadata or {})
                plan.add_step(step)

        return plan

    def to_plan_step(self, task: Task) -> PlanStep:
        return PlanStep(capability=task.capability, arguments=task.arguments or {})

    def available_capabilities(self) -> list[str]:
        return list(self.registry.names())

    def has_capability(self, capability: str) -> bool:
        return self.registry.exists(capability)