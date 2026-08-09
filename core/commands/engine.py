"""Deterministic command-to-capability execution for Webster."""

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

    def _sync_authoritative_registry(self) -> None:
        """Ensure all command-stage components use the live capability registry.

        The CapabilityEngine owns the authoritative registry. Older initialization
        paths could leave Planner, Validator, or TaskDecomposer holding a different
        registry instance. That produced the contradictory state where a capability
        existed during command routing but was reported as unknown during validation.
        """
        registry = self.capability_engine.registry
        if getattr(self.planner, "_registry", None) is not registry:
            self.planner._registry = registry
        if getattr(self.validator, "_registry", None) is not registry:
            self.validator._registry = registry
        if getattr(self.decomposer, "_registry", None) is not registry:
            self.decomposer._registry = registry

    def can_handle(self, message: str) -> bool:
        self._sync_authoritative_registry()
        intent = self.router.route(message)
        return bool(
            intent.is_action
            and intent.action
            and self.capability_engine.exists(intent.action)
        )

    def execute(self, message: str) -> str:
        self._sync_authoritative_registry()
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
        self._sync_authoritative_registry()
        registry = self.capability_engine.registry
        return {
            "healthy": True,
            "capabilities": len(self.capability_engine.names()),
            "mode": "direct-capability",
            "registry_synchronized": (
                getattr(self.planner, "_registry", None) is registry
                and getattr(self.validator, "_registry", None) is registry
                and getattr(self.decomposer, "_registry", None) is registry
            ),
        }
