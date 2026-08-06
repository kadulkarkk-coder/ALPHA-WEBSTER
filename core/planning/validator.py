"""
Webster Alpha

Plan Validator
"""

from __future__ import annotations

from core.capability.registry import CapabilityRegistry
from core.planning.plan import Plan


class Validator:
    """
    Validates execution plans before execution.
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        self._registry = registry

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    # ---------------------------------------------------------

    def validate(
        self,
        plan: Plan,
    ) -> tuple[bool, list[str]]:
        """
        Validate a complete plan.
        """

        errors: list[str] = []

        if not plan.goal.strip():

            errors.append(
                "Plan goal cannot be empty."
            )

        if plan.is_empty:

            errors.append(
                "Plan contains no steps."
            )

        seen = set()

        for index, step in enumerate(plan.steps):

            if not step.capability or not step.capability.strip():

                errors.append(f"Step {index + 1}: capability is empty.")

                continue

            if not self.registry.exists(step.capability):

                errors.append(
                    f"Step {index + 1}: Unknown capability '{step.capability}'."
                )

            if not isinstance(step.arguments, dict):

                errors.append(
                    f"Step {index + 1}: arguments must be a dictionary."
                )

            # duplicate detection by capability+arguments
            key = (step.capability, repr(step.arguments))

            if key in seen:

                errors.append(f"Step {index + 1}: duplicate step detected.")

            seen.add(key)

            # ordering validation: if step.metadata contains 'requires', ensure required caps appear earlier
            requires = step.metadata.get("requires") if isinstance(step.metadata, dict) else None

            if requires:
                for req in requires:
                    found = any(s.capability == req for s in plan.steps[:index])
                    if not found:
                        errors.append(
                            f"Step {index + 1}: requires capability '{req}' earlier in the plan."
                        )

        return (
            len(errors) == 0,
            errors,
        )

    # ---------------------------------------------------------

    def is_valid(
        self,
        plan: Plan,
    ) -> bool:
        """
        Convenience helper.
        """

        valid, _ = self.validate(plan)

        return valid