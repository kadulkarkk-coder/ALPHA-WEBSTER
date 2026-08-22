"""Integration facade for the capability governance layer."""

from __future__ import annotations

from core.capability.capability import Capability
from core.capability.executor import CapabilityExecutor
from core.capability.governance import CapabilityGovernance, GovernanceDecision
from core.capability.registry import CapabilityRegistry
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityResultStatus


class CapabilityIntegration:
    """Coordinates registry, governance and execution without replacing them."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        executor: CapabilityExecutor | None = None,
        governance: CapabilityGovernance | None = None,
    ) -> None:
        self.registry = registry
        self.executor = executor or CapabilityExecutor(registry)
        self.governance = governance or CapabilityGovernance()

    def register(self, capability: Capability) -> None:
        self.registry.register(capability)

    def preflight(self, request: CapabilityRequest) -> GovernanceDecision:
        capability = self.registry.require(request.capability)
        return self.governance.evaluate(capability, request)

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        decision = self.preflight(request)
        if not decision.allowed:
            return CapabilityResult(
                status=CapabilityResultStatus.FAILURE,
                success=False,
                error=decision.reason,
                metadata={
                    "governance": True,
                    "availability": decision.availability.state.name,
                    "policy": decision.policy.decision.name,
                },
            )
        return self.executor.execute(request)
