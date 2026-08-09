"""
Webster Alpha

Plan Validator
"""

from __future__ import annotations

from core.capability.registry import CapabilityRegistry
from core.planning.plan import Plan


class Validator:
    """Validates execution plans against the authoritative capability registry."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        if registry is None:
            raise ValueError("Validator requires a CapabilityRegistry.")
        self._registry = registry

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    def validate(self, plan: Plan) -> tuple[bool, list[str]]:
        """Perform a complete, deterministic pre-execution validation."""
        errors: list[str] = []

        if plan is None:
            return False, ["Plan cannot be None."]

        goal = str(plan.goal or "").strip()
        if not goal:
            errors.append("Plan goal cannot be empty.")

        if plan.is_empty:
            errors.append("Plan contains no steps.")
            return False, errors

        seen: set[tuple[str, str]] = set()

        for index, step in enumerate(plan.steps):
            prefix = f"Step {index + 1}"
            capability = str(step.capability or "").strip().lower()

            if not capability:
                errors.append(f"{prefix}: capability is empty.")
                continue

            if capability != step.capability:
                # Keep the plan internally canonical. The registry is
                # case-insensitive, but downstream execution should receive
                # exactly the same canonical name that was validated.
                step.capability = capability

            if not self._registry.exists(capability):
                errors.append(
                    f"{prefix}: Unknown capability '{capability}'."
                )

            if not isinstance(step.arguments, dict):
                errors.append(f"{prefix}: arguments must be a dictionary.")
                arguments_key = "<invalid>"
            else:
                arguments_key = repr(sorted(step.arguments.items(), key=lambda item: str(item[0])))

            key = (capability, arguments_key)
            if key in seen:
                errors.append(f"{prefix}: duplicate step detected.")
            seen.add(key)

            metadata = step.metadata if isinstance(step.metadata, dict) else {}
            requires = metadata.get("requires")
            if requires:
                if isinstance(requires, str):
                    requires = [requires]
                if not isinstance(requires, (list, tuple, set)):
                    errors.append(f"{prefix}: metadata.requires must be a string or sequence.")
                    requires = []

                previous = {
                    str(previous_step.capability).strip().lower()
                    for previous_step in plan.steps[:index]
                }
                for required in requires:
                    required_name = str(required).strip().lower()
                    if required_name and required_name not in previous:
                        errors.append(
                            f"{prefix}: requires capability '{required_name}' earlier in the plan."
                        )

        return len(errors) == 0, errors

    def is_valid(self, plan: Plan) -> bool:
        valid, _ = self.validate(plan)
        return valid
