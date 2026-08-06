"""
Webster Alpha

Capability Executor
"""

from __future__ import annotations

from time import perf_counter

from core.capability.registry import CapabilityRegistry
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityResultStatus,
)


class CapabilityExecutor:
    """
    Executes registered capabilities.
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        self._registry = registry

    #
    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------
    #

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """
        Execute a capability request.
        """

        start = perf_counter()

        try:

            capability = self._registry.require(
                request.capability
            )

            if not capability.can_execute(
                request
            ):

                return CapabilityResult(

                    status=CapabilityResultStatus.FAILURE,

                    success=False,

                    error=(
                        "Capability cannot "
                        "be executed."
                    ),

                    duration=(
                        perf_counter()
                        - start
                    ),

                )

            capability.busy()

            try:

                result = capability.execute(
                    request
                )

            finally:

                capability.available()

            elapsed = (
                perf_counter()
                - start
            )

            #
            # Preserve the capability result
            # while updating duration.
            #

            return CapabilityResult(

                status=result.status,

                success=result.success,

                output=result.output,

                error=result.error,

                duration=elapsed,

                metadata=result.metadata,

            )

        except Exception as error:

            return CapabilityResult(

                status=CapabilityResultStatus.FAILURE,

                success=False,

                error=str(error),

                duration=(
                    perf_counter()
                    - start
                ),

            )

    #
    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    #

    @property
    def registry(
        self,
    ) -> CapabilityRegistry:

        return self._registry

    #
    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------
    #

    def __repr__(
        self,
    ) -> str:

        return (

            "CapabilityExecutor("

            f"registered={len(self.registry)}"

            ")"

        )