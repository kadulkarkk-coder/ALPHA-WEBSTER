"""
WEBSTER ALPHA

Planning Engine
"""

from __future__ import annotations

from core.capability.engine import CapabilityEngine
from core.capability.registry import CapabilityRegistry
from core.events.event import Event
from core.events.event_bus import EventBus
from core.events.event_types import EventType
from core.planning.manager import PlanningManager
from core.planning.planner import Planner
from core.planning.validator import Validator
from core.planning.executor import Executor
from core.planning.plan import Plan
from core.planning.step import PlanStep
from core.planning.goal import Goal
from core.planning.analyzer import GoalAnalyzer
from core.planning.decomposer import TaskDecomposer
from core.planning.task import Task


class PlanningEngine:
    """Public interface to Webster's planning subsystem."""

    def __init__(self, capability_engine: CapabilityEngine, manager: PlanningManager,
                 planner: Planner, validator: Validator, executor: Executor,
                 analyzer: GoalAnalyzer, decomposer: TaskDecomposer,
                 event_bus: EventBus | None = None,
                 registry: CapabilityRegistry | None = None) -> None:
        dependencies = {"capability_engine": capability_engine, "manager": manager,
                        "planner": planner, "validator": validator, "executor": executor,
                        "analyzer": analyzer, "decomposer": decomposer}
        missing = [name for name, value in dependencies.items() if value is None]
        if missing:
            raise ValueError("PlanningEngine missing injected dependencies: " + ", ".join(missing))
        self._capability_engine = capability_engine
        self._manager = manager
        self._planner = planner
        self._validator = validator
        self._executor = executor
        self._analyzer = analyzer
        self._decomposer = decomposer
        self._event_bus = event_bus
        self._registry = registry
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        if self._registry is None:
            raise RuntimeError("PlanningEngine requires a CapabilityRegistry.")
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError("PlanningEngine has not been initialized. Call initialize() first.")

    @property
    def capability_engine(self) -> CapabilityEngine:
        return self._capability_engine

    @property
    def manager(self) -> PlanningManager:
        return self._manager

    @property
    def planner(self) -> Planner:
        return self._planner

    @property
    def validator(self) -> Validator:
        return self._validator

    @property
    def executor(self) -> Executor:
        return self._executor

    @property
    def registry(self) -> CapabilityRegistry | None:
        return self._registry

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def ready(self) -> bool:
        return self._initialized and self._registry is not None

    def _build_tasks(self, goal: Goal) -> list[Task]:
        analysis = self._analyzer.analyze(goal)
        tasks = self._decomposer.decompose(goal, analysis)
        if analysis.required_capabilities and not tasks:
            missing = [capability for capability in analysis.required_capabilities
                       if self._registry is None or not self._registry.exists(capability)]
            if missing:
                raise ValueError("Required capability is not registered: " + ", ".join(missing))
            raise ValueError("Goal was recognized as actionable, but no executable tasks were created.")
        return tasks

    def create_plan(self, goal_text: str, tasks: list[Task] | None = None) -> Plan:
        self._ensure_initialized()
        if tasks is None:
            goal = Goal(objective=goal_text, priority=0)
            goal.validate()
            tasks = self._build_tasks(goal)
        plan = self._planner.create_plan(goal_text, tasks=tasks)
        self._manager.add_plan(plan)
        return plan

    def to_plan_step(self, task: Task) -> PlanStep:
        return PlanStep(capability=task.capability, arguments=task.arguments or {})

    def available_capabilities(self) -> list[str]:
        return list(self._registry.names()) if self._registry else []

    def has_capability(self, capability: str) -> bool:
        return self._registry.exists(capability) if self._registry else False

    def validate(self, plan: Plan) -> bool:
        return self._validator.is_valid(plan)

    def validate_plan(self, plan: Plan) -> tuple[bool, list[str]]:
        return self._validator.validate(plan)

    def plan_goal(self, request) -> Plan:
        self._ensure_initialized()
        if isinstance(request, Goal):
            goal = request
        elif isinstance(request, str):
            goal = Goal(objective=request, priority=0)
        else:
            raise TypeError("plan_goal expects a Goal or string objective")
        goal.validate()
        self._manager.add_goal(goal)
        tasks = self._build_tasks(goal)
        for task in tasks:
            task.validate()
            self._manager.add_task(task)
        plan = self._planner.create_plan(goal.objective, tasks=tasks)
        self._manager.add_plan(plan)
        if self._event_bus is not None:
            self._event_bus.publish(Event(name=EventType.PLANNING_STARTED.name,
                                           source="planning_engine",
                                           data={"goal": goal.objective,
                                                 "plan_id": plan.id,
                                                 "tasks": [task.capability for task in tasks]}))
        return plan

    def execute_plan(self, plan: Plan):
        self._ensure_initialized()
        valid, errors = self._validator.validate(plan)
        if not valid:
            raise ValueError(f"Plan validation failed: {errors}")
        result = self._executor.execute(plan)
        self._manager.add_history(plan)
        if self._event_bus is not None:
            self._event_bus.publish(Event(name=EventType.PLANNING_COMPLETED.name,
                                           source="planning_engine",
                                           data={"plan_id": plan.id, "goal": plan.goal,
                                                 "success": getattr(result, "success", True)}))
        return result

    def execute_goal(self, request):
        return self.execute_plan(self.plan_goal(request))

    def create_workflow(self, name: str, goals: list[str] | None = None):
        self._ensure_initialized()
        from core.planning.workflow import Workflow
        workflow = Workflow(name=name)
        if goals:
            for goal in goals:
                workflow.add_plan(self.plan_goal(goal))
        self._manager.add_workflow(workflow)
        return workflow

    def execute_workflow(self, workflow_name: str) -> list[Plan]:
        self._ensure_initialized()
        workflow = next((candidate for candidate in self._manager._workflows.values()
                         if candidate.name == workflow_name), None)
        if workflow is None:
            raise KeyError(f"Workflow '{workflow_name}' not found.")
        results: list[Plan] = []
        workflow.status = "running"
        for plan in workflow.plans:
            self.execute_plan(plan)
            results.append(plan)
        workflow.status = "completed"
        return results

    def cancel(self, plan_id: str) -> None:
        self._manager.remove_plan(plan_id)

    def clear(self) -> None:
        self._manager.clear()

    @property
    def plan_count(self) -> int:
        return self._manager.plan_count

    @property
    def workflow_count(self) -> int:
        return self._manager.workflow_count

    @property
    def history(self):
        return self._manager.history

    def health(self) -> dict:
        return {"initialized": self._initialized, "ready": self.ready,
                "healthy": self.ready, "plans": self.plan_count,
                "workflows": self.workflow_count, "history": self._manager.history_count}
