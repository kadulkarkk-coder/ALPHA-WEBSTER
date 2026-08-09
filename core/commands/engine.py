"""Deterministic command-to-capability execution for Webster.

Part 1 keeps ordinary computer commands out of the LLM. A command that has
already been classified by IntentRouter is converted directly into one Task;
there is no second classifier/decomposer decision involved in the execution
path.
"""

from __future__ import annotations

from core.ai.response_builder import ResponseBuilder
from core.ai.router import IntentRouter
from core.capability.engine import CapabilityEngine
from core.planning.decomposer import TaskDecomposer
from core.planning.goal import Goal
from core.planning.planner import Planner
from core.planning.validator import Validator
from core.planning.executor import Executor


class CommandEngine:
    """Execute deterministic single-intent commands through real capabilities."""

    def __init__(
        self,
        router: IntentRouter,
        decomposer: TaskDecomposer,
        planner: Planner,
        validator: Validator,
        executor: Executor,
        capability_engine: CapabilityEngine,
        response_builder: ResponseBuilder,
    ) -> None:
        self.router = router
        self.decomposer = decomposer
        self.planner = planner
        self.validator = validator
        self.executor = executor
        self.capability_engine = capability_engine
        self.response_builder = response_builder

    def can_handle(self, message: str) -> bool:
        intent = self.router.route(message)
        return bool(
            intent.is_action
            and intent.action
            and self.capability_engine.exists(intent.action)
        )

    def execute(self, message: str) -> str:
        intent = self.router.route(message)

        if not intent.is_action:
            raise ValueError("Command is not an executable action.")
        if not intent.action:
            raise ValueError("I couldn't determine which capability should execute this command.")

        capability = intent.action.strip().lower()
        if not self.capability_engine.exists(capability):
            available = ", ".join(self.capability_engine.names())
            raise ValueError(
                f"Capability '{capability}' is not registered. "
                f"Available capabilities: {available or 'none'}."
            )

        # IMPORTANT: the router has already made the capability decision.
        # Create the executable task directly instead of running a second
        # analysis/decomposition pass. This guarantees that a recognized
        # capability cannot disappear between routing and execution.
        goal = Goal(objective=message.strip(), priority=0)
        task = self.decomposer.create_task(goal, capability)
        task.validate()

        plan = self.planner.create_plan(goal.objective, tasks=(task,))
        valid, errors = self.validator.validate(plan)
        if not valid:
            raise ValueError(f"Command plan is invalid: {errors}")

        result = self.executor.execute(plan)
        if getattr(result, "status", "") == "failed":
            failed = next(
                (step for step in result.steps if step.status == "failed"),
                None,
            )
            return self.response_builder.error(
                getattr(failed, "error", None) or "Capability execution failed."
            )

        step_results = [
            step.result for step in result.steps if step.result is not None
        ]
        if step_results:
            return self.response_builder.build(step_results[-1])
        return "Task completed successfully."

    def health(self) -> dict:
        return {
            "healthy": True,
            "capabilities": len(self.capability_engine.names()),
            "mode": "direct-capability",
        }
