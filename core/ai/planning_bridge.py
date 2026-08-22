"""WEBSTER ALPHA - AI to planning integration bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.ai.goal_builder import GoalBuilder
from core.ai.router import Intent
from core.capability.engine import CapabilityEngine
from core.planning.engine import PlanningEngine
from core.planning.plan import Plan


@dataclass(slots=True, frozen=True)
class PlanningDecision:
    """Result of deciding whether an intent should enter the planner."""

    executable: bool
    reason: str
    capability: str | None = None


class AIPlanningBridge:
    """Connects intent routing, goal construction and plan execution."""

    def __init__(
        self,
        planning_engine: PlanningEngine,
        capability_engine: CapabilityEngine,
        goal_builder: GoalBuilder,
    ) -> None:
        if planning_engine is None or capability_engine is None or goal_builder is None:
            raise ValueError("AIPlanningBridge requires planning, capability and goal services.")
        self._planning = planning_engine
        self._capabilities = capability_engine
        self._goal_builder = goal_builder

    @property
    def planning_engine(self) -> PlanningEngine:
        return self._planning

    @property
    def capability_engine(self) -> CapabilityEngine:
        return self._capabilities

    def decide(self, intent: Intent) -> PlanningDecision:
        """Determine whether an intent contains enough information for planning."""
        action = (intent.action or "").strip().lower()
        if action and self._capabilities.exists(action):
            return PlanningDecision(True, "registered capability", action)

        if action:
            return PlanningDecision(False, f"capability '{action}' is not registered", action)

        # An action intent with no resolved capability is not a planning goal.
        # Sending it to the planner creates a valid-looking but empty plan and
        # hides the real routing failure behind "Plan contains no steps".
        if intent.is_action:
            return PlanningDecision(
                False,
                "I couldn't determine an executable capability for that request.",
            )

        return PlanningDecision(False, "intent is not actionable")

    def build_plan(self, message: str, intent: Intent) -> Plan:
        decision = self.decide(intent)
        if not decision.executable:
            raise ValueError(decision.reason)
        goal = self._goal_builder.build(message, intent)
        return self._planning.plan_goal(goal)

    def execute(self, message: str, intent: Intent) -> Any:
        plan = self.build_plan(message, intent)
        return self._planning.execute_plan(plan)

    def health(self) -> dict[str, Any]:
        return {
            "healthy": self._planning.ready and self._capabilities.ready,
            "planning": self._planning.health(),
            "capabilities": self._capabilities.health(),
        }
