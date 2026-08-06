"""
WEBSTER ALPHA

Planning Manager
"""

from __future__ import annotations

from core.planning.plan import Plan
from core.planning.workflow import Workflow


class PlanningManager:
    """
    Manages planning state.

    Responsible for storing active plans,
    workflows and execution history.
    """

    def __init__(self) -> None:

        self._plans: dict[str, Plan] = {}

        self._workflows: dict[str, Workflow] = {}

        self._history: list[Plan] = []

    # =====================================================
    # Plans
    # =====================================================

    def add_plan(self, plan: Plan) -> None:

        self._plans[plan.id] = plan

    # -----------------------------------------------------

    def remove_plan(self, plan_id: str) -> Plan | None:

        return self._plans.pop(plan_id, None)

    # -----------------------------------------------------

    def get_plan(self, plan_id: str) -> Plan | None:

        return self._plans.get(plan_id)

    # -----------------------------------------------------

    @property
    def plans(self) -> dict[str, Plan]:

        return self._plans

    # =====================================================
    # Workflows
    # =====================================================

    def add_workflow(
        self,
        workflow: Workflow,
    ) -> None:

        self._workflows[workflow.id] = workflow

    # -----------------------------------------------------

    def remove_workflow(
        self,
        workflow_id: str,
    ) -> Workflow | None:

        return self._workflows.pop(
            workflow_id,
            None,
        )

    # -----------------------------------------------------

    def get_workflow(
        self,
        workflow_id: str,
    ) -> Workflow | None:

        return self._workflows.get(
            workflow_id,
        )

    # -----------------------------------------------------

    @property
    def workflows(self) -> dict[str, Workflow]:

        return self._workflows

    # =====================================================
    # History
    # =====================================================

    def add_history(
        self,
        plan: Plan,
    ) -> None:

        self._history.append(plan)

    @property
    def history(self) -> list[Plan]:

        return self._history

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def plan_count(self) -> int:

        return len(self._plans)

    @property
    def workflow_count(self) -> int:

        return len(self._workflows)

    @property
    def history_count(self) -> int:

        return len(self._history)

    # =====================================================
    # Cleanup
    # =====================================================

    def clear(self) -> None:

        self._plans.clear()

        self._workflows.clear()

        self._history.clear()

