"""
Webster Alpha

Planning Manager
"""

from __future__ import annotations
from __future__ import annotations

from typing import Dict, Optional

from core.planning.plan import Plan
from core.planning.workflow import Workflow


class PlanningManager:
    """
    PlanningManager manages only state: plans, workflows and history.
    """

    def __init__(self) -> None:

        self._plans: Dict[str, Plan] = {}

        self._workflows: Dict[str, Workflow] = {}

        self._history: Dict[str, Plan] = {}
        
        self._goals: Dict[str, "Goal"] = {}

        self._tasks: Dict[str, "Task"] = {}

    # ---------------------------------------------------------
    # Plans
    # ---------------------------------------------------------

    def add_plan(self, plan: Plan) -> None:

        if plan is None or plan.id is None:
            raise ValueError("Plan must have an id")

        self._plans[plan.id] = plan

    # ---------------------------------------------------------
    # Goals
    # ---------------------------------------------------------

    def add_goal(self, goal: "Goal") -> None:

        if goal is None or not getattr(goal, "id", None):
            raise ValueError("Goal must have an id")

        self._goals[goal.id] = goal

    def get_goal(self, goal_id: str):

        return self._goals.get(goal_id)

    def remove_goal(self, goal_id: str):

        return self._goals.pop(goal_id, None)

    @property
    def goal_count(self) -> int:

        return len(self._goals)

    def remove_plan(self, plan_id: str) -> Optional[Plan]:

        return self._plans.pop(plan_id, None)

    def get_plan(self, plan_id: str) -> Optional[Plan]:

        return self._plans.get(plan_id)

    def clear_plans(self) -> None:

        self._plans.clear()

    @property
    def plan_count(self) -> int:

        return len(self._plans)

    # ---------------------------------------------------------
    # Workflows
    # ---------------------------------------------------------

    def add_workflow(self, workflow: Workflow) -> None:

        if workflow is None or workflow.id is None:
            raise ValueError("Workflow must have an id")

        self._workflows[workflow.id] = workflow

    def remove_workflow(self, workflow_id: str) -> Optional[Workflow]:

        return self._workflows.pop(workflow_id, None)

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:

        return self._workflows.get(workflow_id)

    def clear_workflows(self) -> None:

        self._workflows.clear()

    @property
    def workflow_count(self) -> int:

        return len(self._workflows)

    # ---------------------------------------------------------
    # History
    # ---------------------------------------------------------

    def add_history(self, plan: Plan) -> None:

        if plan is None or plan.id is None:
            raise ValueError("Plan must have an id")

        self._history[plan.id] = plan

    # ---------------------------------------------------------
    # Tasks
    # ---------------------------------------------------------

    def add_task(self, task: "Task") -> None:

        if task is None or not getattr(task, "id", None):
            raise ValueError("Task must have an id")

        self._tasks[task.id] = task

    def get_task(self, task_id: str):

        return self._tasks.get(task_id)

    def remove_task(self, task_id: str):

        return self._tasks.pop(task_id, None)

    @property
    def task_count(self) -> int:

        return len(self._tasks)

    def get_history(self, plan_id: str) -> Optional[Plan]:

        return self._history.get(plan_id)

    def clear_history(self) -> None:

        self._history.clear()

    @property
    def history_count(self) -> int:

        return len(self._history)

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def clear(self) -> None:

        self.clear_plans()

        self.clear_workflows()

        self.clear_history()
        
        self._goals.clear()

        self._tasks.clear()

    @property
    def history(self) -> Dict[str, Plan]:

        return dict(self._history)

    def __repr__(self) -> str:

        return (
            f"PlanningManager(plans={self.plan_count}, "
            f"workflows={self.workflow_count}, history={self.history_count})"
        )