"""
Webster Alpha

Plan Executor
"""

from __future__ import annotations

from core.capability.engine import CapabilityEngine
from core.capability.request import CapabilityRequest
from core.planning.plan import Plan


class Executor:
    """
    Executes plans produced by the Planner.
    """

    def __init__(
        self,
        capability_engine: CapabilityEngine,
    ) -> None:

        self._engine = capability_engine

    @property
    def capability_engine(self) -> CapabilityEngine:

        return self._engine

    # -----------------------------------------------------

    def execute(
        self,
        plan: Plan,
    ) -> Plan:
        """
        Execute every step in the plan.
        """

        if plan.is_empty:

            plan.mark_completed()
            return plan

        plan.mark_running()

        for step in plan.steps:

            step.mark_running()

            try:

                request = CapabilityRequest(
                    capability=step.capability,
                    arguments=step.arguments,
                )

                result = self.capability_engine.execute(
                    request,
                )

                if result.success:

                    step.mark_completed(
                        result=result,
                    )

                else:

                    step.mark_failed(
                        result.error,
                    )

                    plan.mark_failed()

                    return plan

            except Exception as error:

                step.mark_failed(
                    str(error),
                )

                plan.mark_failed()

                return plan

        plan.mark_completed()

        return plan

    # -----------------------------------------------------

    def execute_step(
        self,
        step,
    ):
        """
        Execute a single step.
        """

        request = CapabilityRequest(
            capability=step.capability,
            arguments=step.arguments,
        )

        return self.capability_engine.execute(
            request,
        )