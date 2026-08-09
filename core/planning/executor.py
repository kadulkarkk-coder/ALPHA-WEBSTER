"""WEBSTER ALPHA - Plan Executor."""

from __future__ import annotations

from core.capability.engine import CapabilityEngine
from core.capability.request import CapabilityRequest
from core.planning.plan import Plan


class Executor:
    """Execute validated plans through the capability engine."""

    def __init__(self, capability_engine: CapabilityEngine) -> None:
        self._engine = capability_engine

    @property
    def capability_engine(self) -> CapabilityEngine:
        return self._engine

    def execute(self, plan: Plan) -> Plan:
        if plan.is_empty:
            raise ValueError("Cannot execute an empty plan.")

        plan.mark_running()

        for step in plan.steps:
            step.mark_running()
            try:
                request = CapabilityRequest(
                    capability=step.capability,
                    action=step.metadata.get("action", step.capability),
                    step=step,
                    arguments=step.arguments,
                    metadata=step.metadata,
                )
                result = self._engine.execute(request)

                if result.success:
                    step.mark_completed(result=result)
                else:
                    step.mark_failed(result.error or "Capability execution failed.")
                    plan.mark_failed()
                    return plan
            except Exception as error:
                step.mark_failed(str(error))
                plan.mark_failed()
                return plan

        plan.mark_completed()
        return plan

    def execute_step(self, step):
        request = CapabilityRequest(
            capability=step.capability,
            action=step.metadata.get("action", step.capability),
            step=step,
            arguments=step.arguments,
            metadata=step.metadata,
        )
        return self._engine.execute(request)
