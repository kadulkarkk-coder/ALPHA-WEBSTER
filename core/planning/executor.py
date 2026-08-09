"""WEBSTER ALPHA - Plan Executor."""

from __future__ import annotations

from core.capability.engine import CapabilityEngine
from core.capability.request import CapabilityRequest
from core.planning.plan import Plan


class Executor:
    """Execute plans through the authoritative CapabilityEngine."""

    def __init__(self, capability_engine: CapabilityEngine) -> None:
        if capability_engine is None:
            raise ValueError("Executor requires a CapabilityEngine.")
        self._engine = capability_engine

    @property
    def capability_engine(self) -> CapabilityEngine:
        return self._engine

    def _preflight(self, plan: Plan) -> None:
        """Verify every step can reach the same capability engine before running any step."""
        if plan is None:
            raise ValueError("Plan cannot be None.")
        if plan.is_empty:
            raise ValueError("Cannot execute an empty plan.")
        if not self._engine.ready:
            raise RuntimeError("CapabilityEngine is not ready.")

        errors: list[str] = []
        for index, step in enumerate(plan.steps):
            capability = str(step.capability or "").strip().lower()
            if not capability:
                errors.append(f"Step {index + 1}: capability is empty.")
                continue
            if not self._engine.exists(capability):
                errors.append(
                    f"Step {index + 1}: capability '{capability}' is not registered."
                )
            if not isinstance(step.arguments, dict):
                errors.append(f"Step {index + 1}: arguments must be a dictionary.")

        if errors:
            raise ValueError("Plan preflight failed: " + "; ".join(errors))

    @staticmethod
    def _request_for(step) -> CapabilityRequest:
        capability = str(step.capability).strip().lower()
        metadata = step.metadata if isinstance(step.metadata, dict) else {}
        return CapabilityRequest(
            capability=capability,
            action=str(metadata.get("action", capability)).strip() or capability,
            step=step,
            arguments=dict(step.arguments),
            metadata=metadata,
        )

    def execute(self, plan: Plan) -> Plan:
        """Preflight the entire plan, then execute steps sequentially."""
        self._preflight(plan)
        plan.mark_running()

        for step in plan.steps:
            step.mark_running()
            try:
                result = self._engine.execute(self._request_for(step))
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
        """Execute one already-validated step through the same preflight rules."""
        if step is None:
            raise ValueError("Step cannot be None.")
        capability = str(step.capability or "").strip().lower()
        if not capability:
            raise ValueError("Step capability cannot be empty.")
        if not self._engine.ready:
            raise RuntimeError("CapabilityEngine is not ready.")
        if not self._engine.exists(capability):
            raise ValueError(f"Capability '{capability}' is not registered.")
        if not isinstance(step.arguments, dict):
            raise ValueError("Step arguments must be a dictionary.")
        return self._engine.execute(self._request_for(step))
